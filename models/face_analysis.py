import cv2
import os
import numpy as np
from tensorflow.keras.models import load_model
from config import Config
from models.db import connect_db

# Load model cảm xúc
emotion_model = load_model("emotion_model.h5")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Load Haar cascade của OpenCV để phát hiện khuôn mặt
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def analyze_image(file_path, id_lophoc):
    img = cv2.imread(file_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)

    if len(detected_faces) == 0:
        return {'error': 'Không phát hiện khuôn mặt nào trong ảnh.'}

    conn = connect_db()
    cursor = conn.cursor()
    results = []

    for idx, (x, y, w, h) in enumerate(detected_faces):
        face_img = img[y:y+h, x:x+w]
        face_filename = f"face_{id_lophoc}_{idx}.jpg"
        face_save_path = os.path.join(Config.FACE_FOLDER, face_filename)
        cv2.imwrite(face_save_path, face_img)

        # Chuẩn bị ảnh để dự đoán
        face_resized = cv2.resize(face_img, (48, 48))
        face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        face_normalized = face_gray.astype("float32") / 255.0
        face_input = np.expand_dims(face_normalized, axis=(0, -1))  # shape (1, 48, 48, 1)

        prediction = emotion_model.predict(face_input)
        emotion_idx = np.argmax(prediction)
        emotion = emotion_labels[emotion_idx]
        confidence = float(prediction[0][emotion_idx])

        cursor.execute('''
            INSERT INTO sinhvien (id_lophoc, image_path, face_path, emotion, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (id_lophoc, file_path, face_save_path, emotion, confidence))

        results.append({
            'face_path': face_save_path,
            'emotion': emotion,
            'confidence': confidence
        })

    conn.commit()
    conn.close()
    return results
