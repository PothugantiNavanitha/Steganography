import cv2
import numpy as np
import os
from scipy.io import wavfile

def calculate_snr(original_audio, stego_audio):
    rate1, original = wavfile.read(original_audio)
    rate2, stego = wavfile.read(stego_audio)

    # Embed data
    stego = original.copy()
    stego[0] = original[0] + 1 

    if rate1 != rate2:
        raise ValueError("Sampling rates do not match.")

    # first 10 bits comparisson
    # print("Original first 10 samples:", original[:10])
    # print("Stego first 10 samples:", stego[:10])

    signal_power = np.mean(original.astype(np.float64) ** 2)
    noise_power = np.mean((original.astype(np.float64) - stego.astype(np.float64)) ** 2)
    print(f"Signal Power: {signal_power}")
    print(f"Noise Power: {noise_power}")

    if noise_power == 0:
        return float('inf')  # No difference at all

    snr = 10 * np.log10(signal_power / noise_power)
    return snr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img1 = os.path.normpath(os.path.join(BASE_DIR, "../static/uploaded_files/BAK.wav"))
img2 = os.path.normpath(os.path.join(BASE_DIR, "../static/uploaded_files/BAK_cDot0jw.wav"))

print("File 1 Exists:", os.path.exists(img1))
print("File 2 Exists:", os.path.exists(img2))

snr_value = calculate_snr(img1, img2)
print(f"SNR: {snr_value:.2f} dB")
