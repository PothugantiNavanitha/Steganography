# views.py (with login/signup logic)

from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from . import steg_utils
import os
import uuid
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView as DjangoLogoutView
import cv2
import numpy as np
#from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
#from django.shortcuts import render
#from django.contrib import messages
#import os



UPLOAD_DIR = "stego_app/static/uploaded_files"
SECRET_DB = os.path.join(UPLOAD_DIR, "secret_codes.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper to read/write JSON secrets
def load_secrets():
    if os.path.exists(SECRET_DB):
        with open(SECRET_DB, 'r') as f:
            return json.load(f)
    return {}

def save_secret(file_name, secret_code):
    secrets = load_secrets()
    secrets[file_name] = secret_code
    with open(SECRET_DB, 'w') as f:
        json.dump(secrets, f)

#------------------logout btth------------

class LogoutView(DjangoLogoutView):
    next_page = 'login'

# ----------------- Auth -----------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            return redirect('dashboard')
    return render(request, 'signup.html')

# ----------------- Dashboard -----------------
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')

# ----------------- Image Steg -----------------
@login_required
def image_steg(request):
    return render(request, 'image_steg.html')

# def image_steg(request):
#     if request.method == 'POST':
#         action = request.POST['action']
#         uploaded_file = request.FILES.get('image_file')
#         secret_code = request.POST.get('secret_code')
#         msg = request.POST.get('message')

#         if uploaded_file:
#             fs = FileSystemStorage(location=UPLOAD_DIR)
#             filename = fs.save(uploaded_file.name, uploaded_file)
#             file_path = os.path.join(UPLOAD_DIR, filename)
#             print("Secret DB path:", SECRET_DB)

#             if action == 'encrypt':
#                 unique_name = f"enc_{uuid.uuid4().hex[:6]}.png"
#                 out_path = os.path.join(UPLOAD_DIR, unique_name)
#                 steg_utils.encode_image(file_path, msg, out_path)
#                 save_secret(unique_name, secret_code)
#                 messages.success(request, f"Image encrypted as: {unique_name}")
#                 #debug
#                 print("Saving secret:", unique_name, secret_code)  # during encryption


#             elif action == 'decrypt':
#                 secrets = load_secrets()
#                 if uploaded_file.name in secrets and secrets[uploaded_file.name] == secret_code:
#                     msg = steg_utils.decode_image(file_path)
#                     messages.success(request, f"Decrypted Message: {msg}")
#                 else:
#                     messages.error(request, "Incorrect secret code or file!")
#                 #debug
#                 print("Looking for:", filename, "in", secrets)  # during decryption

#     return render(request, 'image_steg.html')

@login_required
def image_encrypt(request):
    if request.method == 'POST':
        # action = request.POST.get['action']
        uploaded_file = request.FILES.get('image_file')
        secret_code = request.POST.get('secret_code')
        msg = request.POST.get('message')

        if uploaded_file:
            fs = FileSystemStorage(location=UPLOAD_DIR)
            if fs.exists(uploaded_file.name):
                fs.delete(uploaded_file.name)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(UPLOAD_DIR, filename)
            print("Secret DB path:", SECRET_DB)

            unique_name = f"enc_{uuid.uuid4().hex[:6]}.png"
            out_path = os.path.join(UPLOAD_DIR, unique_name)
            steg_utils.encode_image(file_path, msg, out_path)
            save_secret(unique_name, secret_code)
            messages.success(request, f"Image encrypted as: {unique_name}")
            print("Saving secret:", unique_name, secret_code)

    return render(request, 'image_encrypt.html')


@login_required
def image_decrypt(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image_file')
        secret_code = request.POST.get('secret_code')

        if uploaded_file:
            # Don't save the uploaded file again - use it directly from memory
            # Generate a temporary path for processing
            temp_path = os.path.join(UPLOAD_DIR, f"temp_{uuid.uuid4().hex[:6]}.png")
            
            # Save the uploaded file temporarily
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            secrets = load_secrets()
            decrypted_msg = None
            psnr_value = None
            
            # Check if the original filename (without temp prefix) is in secrets
            original_filename = uploaded_file.name
            if original_filename in secrets and secrets[original_filename] == secret_code:
                try:
                    decrypted_msg = steg_utils.decode_image(temp_path)
                except Exception as e:
                    messages.error(request, f"Decryption failed: {str(e)}")
                    decrypted_msg = None
                
                # Try to find the original file for PSNR calculation
                original_path = None
                if original_filename.startswith('enc_'):
                    # This is an encrypted file, look for original
                    base_name = original_filename[4:]  # Remove 'enc_' prefix
                    original_path = os.path.join(UPLOAD_DIR, base_name)
                
                if original_path and os.path.exists(original_path):
                    try:
                        psnr_value = calculate_psnr(original_path, temp_path)
                    except Exception as e:
                        psnr_value = f"Error calculating PSNR: {e}"
                else:
                    psnr_value = "Original file not found for PSNR calculation"
                
                if decrypted_msg:
                    messages.success(request, f"Decrypted Message: {decrypted_msg}")
            else:
                messages.error(request, "Incorrect secret code or file!")
            
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return render(request, 'image_decrypt.html', {
                'decrypted_msg': decrypted_msg,
                'psnr_value': psnr_value
            })

    return render(request, 'image_decrypt.html')


# ----------------- Audio Steg -----------------
# @login_required
# def audio_steg(request):
#     if request.method == 'POST':
#         action = request.POST['action']
#         uploaded_file = request.FILES.get('audio_file')
#         secret_code = request.POST.get('secret_code')
#         msg = request.POST.get('message')

#         if uploaded_file:
#             fs = FileSystemStorage(location=UPLOAD_DIR)
#             filename = fs.save(uploaded_file.name, uploaded_file)
#             file_path = os.path.join(UPLOAD_DIR, filename)

#             if action == 'encrypt':
#                 unique_name = f"enc_{uuid.uuid4().hex[:6]}.wav"
#                 out_path = os.path.join(UPLOAD_DIR, unique_name)
#                 steg_utils.encode_audio(file_path, msg, out_path)
#                 save_secret(unique_name, secret_code)
#                 messages.success(request, f"Audio encrypted as: {unique_name}")

#             elif action == 'decrypt':
#                 secrets = load_secrets()
#                 if uploaded_file.name in secrets and secrets[uploaded_file.name] == secret_code:
#                     msg = steg_utils.decode_audio(file_path)
#                     messages.success(request, f"Decrypted Message: {msg}")
#                 else:
#                     messages.error(request, "Incorrect secret code or file!")

#     return render(request, 'audio_steg.html')

@login_required
def audio_steg(request):
    return render(request, 'audio_steg.html')

@login_required
def audio_encrypt(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('audio_file')
        secret_code = request.POST.get('secret_code')
        msg = request.POST.get('message')

        if uploaded_file:
            fs = FileSystemStorage(location=UPLOAD_DIR)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(UPLOAD_DIR, filename)

            unique_name = f"enc_{uuid.uuid4().hex[:6]}.wav"
            out_path = os.path.join(UPLOAD_DIR, unique_name)

            steg_utils.encode_audio(file_path, msg, out_path)
            save_secret(unique_name, secret_code)
            messages.success(request, f"Audio encrypted and saved as: {unique_name}")

    return render(request, 'audio_encrypt.html')

@login_required
def audio_decrypt(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('audio_file')
        secret_code = request.POST.get('secret_code')

        if uploaded_file:
            fs = FileSystemStorage(location=UPLOAD_DIR)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(UPLOAD_DIR, filename)

            secrets = load_secrets()
            if uploaded_file.name in secrets and secrets[uploaded_file.name] == secret_code:
                msg = steg_utils.decode_audio(file_path)
                messages.success(request, f"Decrypted Message: {msg}")
            else:
                messages.error(request, "Incorrect secret code or file!")

    return render(request, 'audio_decrypt.html')

# ----------------- Video Steg -----------------
# @login_required
# def video_steg(request):
#     if request.method == 'POST':
#         action = request.POST['action']
#         uploaded_file = request.FILES.get('video_file')
#         secret_code = request.POST.get('secret_code')
#         msg = request.POST.get('message')

#         if uploaded_file:
#             fs = FileSystemStorage(location=UPLOAD_DIR)
#             filename = fs.save(uploaded_file.name, uploaded_file)
#             file_path = os.path.join(UPLOAD_DIR, filename)

#             if action == 'encrypt':
#                 unique_name = f"enc_{uuid.uuid4().hex[:6]}.avi"
#                 out_path = os.path.join(UPLOAD_DIR, unique_name)
#                 steg_utils.encode_video(file_path, msg, out_path)
#                 save_secret(unique_name, secret_code)
#                 messages.success(request, f"Video encrypted as: {unique_name}")

#             elif action == 'decrypt':
#                 secrets = load_secrets()
#                 if uploaded_file.name in secrets and secrets[uploaded_file.name] == secret_code:
#                     msg = steg_utils.decode_video(file_path)
#                     messages.success(request, f"Decrypted Message: {msg}")
#                 else:
#                     messages.error(request, "Incorrect secret code or file!")

#     return render(request, 'video_steg.html')


@login_required
def video_steg(request):
    return render(request, 'video_steg.html')


@login_required
def video_encrypt(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('video_file')
        secret_code = request.POST.get('secret_code')
        msg = request.POST.get('message')

        if uploaded_file:
            fs = FileSystemStorage(location=UPLOAD_DIR)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(UPLOAD_DIR, filename)

            unique_name = f"enc_{uuid.uuid4().hex[:6]}.avi"
            out_path = os.path.join(UPLOAD_DIR, unique_name)
            steg_utils.encode_video(file_path, msg, out_path)
            save_secret(unique_name, secret_code)
            messages.success(request, f"Video encrypted as: {unique_name}")

    return render(request, 'video_encrypt.html')


@login_required
def video_decrypt(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('video_file')
        secret_code = request.POST.get('secret_code')

        if uploaded_file:
            fs = FileSystemStorage(location=UPLOAD_DIR)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(UPLOAD_DIR, filename)

            secrets = load_secrets()
            if uploaded_file.name in secrets and secrets[uploaded_file.name] == secret_code:
                msg = steg_utils.decode_video(file_path)
                messages.success(request, f"Decrypted Message: {msg}")
            else:
                messages.error(request, "Incorrect secret code or file!")

    return render(request, 'video_decrypt.html')


def calculate_psnr(original_path, stego_path):
    original = cv2.imread(original_path)
    stego = cv2.imread(stego_path)

    if original is None or stego is None:
        raise FileNotFoundError("Could not load one or both images. Check paths.")

    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float('inf')
    psnr = 20 * np.log10(255.0 / np.sqrt(mse))
    return psnr

