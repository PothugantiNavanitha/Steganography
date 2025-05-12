import cv2
import numpy as np
import os
from scipy.io import wavfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img = os.path.normpath(os.path.join(BASE_DIR, "../static/uploaded_files/enc_704212.png"))
audio = os.path.normpath(os.path.join(BASE_DIR, "../static/uploaded_files/BAK_cDot0jw.wav"))
video = os.path.normpath(os.path.join(BASE_DIR, "../static/uploaded_files/tay_wCvUl0f.avi"))

def calculate_bpp(image_path, embedded_bits):
    image = cv2.imread(image_path)
    h, w, _ = image.shape
    total_pixels = h * w
    bpp = embedded_bits / total_pixels
    return bpp

# Example Usage
bpp = calculate_bpp(img, 10000)
print(f"BPP: {bpp:.4f}")


def bits_per_sample_audio(audio_path, embedded_bits):
    rate, data = wavfile.read(audio_path)
    total_samples = len(data)
    return embedded_bits / total_samples

# Example
bps = bits_per_sample_audio(audio, 10000)
print(f"Bits per sample: {bps:.4f}")


import cv2

def bits_per_frame(video_path, embedded_bits):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return embedded_bits / total_frames

# Example
bpf = bits_per_frame(video, 500000)
print(f"Bits per frame: {bpf:.2f}")

