import cv2
import numpy as np
import os

def calculate_psnr(original_path, stego_path):
    original = cv2.imread(original_path)
    stego = cv2.imread(stego_path)

    if original is None or stego is None:
        raise FileNotFoundError("Could not load one or both images. Check paths.")

    original = cv2.imread(img1)
    stego = cv2.imread(img2)

    if np.array_equal(original, stego):
        print("Images are identical")
    else:
        print("Images are different")

    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float('inf')
    psnr = 20 * np.log10(255.0 / np.sqrt(mse))
    return psnr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img1 = os.path.normpath(os.path.join(BASE_DIR, "../static/uploaded_files/Neongreen.png"))
img2 = os.path.normpath(os.path.join(BASE_DIR, "../static/uploaded_files/enc_55d02a.png"))

print("File 1 Exists:", os.path.exists(img1))
print("File 2 Exists:", os.path.exists(img2))

psnr_value = calculate_psnr(img1, img2)
print(f"PSNR: {psnr_value:.2f} dB")
