

from PIL import Image
import numpy as np
import cv2


def encode_image(img_path, message, out_path):
    img = Image.open(img_path).convert('RGB')
    data = np.array(img)
    binary_msg = ''.join(format(ord(i), '08b') for i in message + '#####')
    flat_data = data.flatten()

    if len(binary_msg) > len(flat_data):
        raise Exception("Message too large!")

    for i in range(len(binary_msg)):
        flat_data[i] = (int(flat_data[i]) & 0b11111110) | int(binary_msg[i])

    encoded = flat_data.reshape(data.shape)
    encoded_img = Image.fromarray(encoded.astype('uint8'))
    encoded_img.save(out_path)



def decode_image(img_path):
    img = Image.open(img_path)
    data = np.array(img).flatten()
    bits = ''.join([str(i & 1) for i in data])
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    msg = ''
    for ch in chars:
        if ch == '00100011':  # '#' in binary
            if msg.endswith("####"):
                break
        msg += chr(int(ch, 2))
    return msg.replace("####", "")

import wave


# ---------- AUDIO ----------
def encode_audio(audio_path, message, out_path):
    audio = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    message += '#####'
    bits = ''.join([format(ord(i), '08b') for i in message])

    if len(bits) > len(frame_bytes):
        raise Exception("Message too large!")

    for i in range(len(bits)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(bits[i])

    modified = bytes(frame_bytes)
    with wave.open(out_path, 'wb') as fd:
        fd.setparams(audio.getparams())
        fd.writeframes(modified)

    audio.close()


def decode_audio(audio_path):
    audio = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    bits = [str(byte & 1) for byte in frame_bytes]
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message = ''

    for byte in chars:
        char = chr(int(''.join(byte), 2))
        message += char
        if message.endswith('#####'):
            break

    audio.close()
    return message.replace('#####', '')


#------------------------video------------------


def encode_video(video_path, message, out_path):
    cap = cv2.VideoCapture(video_path)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out    = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    message += '#####'
    bits = ''.join([format(ord(i), '08b') for i in message])
    bit_idx = 0
    done = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        flat = frame.flatten().astype(np.uint8)  # Ensure uint8 before manipulation

        for i in range(len(flat)):
            if bit_idx < len(bits):
                original = int(flat[i])
                lsb = int(bits[bit_idx])
                new_value = (original & 0xFE) | lsb
                flat[i] = np.clip(new_value, 0, 255)  # Clamp to valid range
                bit_idx += 1
            else:
                done = True
                break

        frame = flat.reshape(frame.shape)
        out.write(frame)

        if done:
            break

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()



def decode_video(video_path):
    cap = cv2.VideoCapture(video_path)
    bits = []
    message = ''
    byte = ''
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        flat = frame.flatten()
        for i in flat:
            bits.append(str(i & 1))
            if len(bits) == 8:
                byte = ''.join(bits)
                char = chr(int(byte, 2))
                message += char
                bits = []
                if message.endswith('#####'):
                    cap.release()
                    return message.replace('#####', '')


