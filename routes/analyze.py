from flask import Blueprint, render_template, request, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from deepface import DeepFace
from models.db import save_sinhvien
import uuid, os, cv2

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    file = request.files['file']
    if not file:
        return "Không có file được chọn."

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    result_faces = []
    try:
        if filename.lower().endswith(".mp4"):
            cap = cv2.VideoCapture(filepath)
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret or frame_count > 5:
                    break

                temp_img = f"temp_{uuid.uuid4()}.jpg"
                cv2.imwrite(temp_img, frame)
                try:
                    analysis = DeepFace.analyze(img_path=temp_img, actions=['emotion'], enforce_detection=False)
                    if not isinstance(analysis, list):
                        analysis = [analysis]

                    for face_data in analysis:
                        region = face_data['region']
                        emotion = face_data['dominant_emotion']
                        conf = face_data['emotion'][emotion]
                        x, y, w, h = region['x'], region['y'], region['w'], region['h']
                        face_crop = frame[y:y+h, x:x+w]
                        face_id = str(uuid.uuid4())
                        face_path = os.path.join(current_app.config['FACES_FOLDER'], f"{face_id}.jpg")
                        cv2.imwrite(face_path, face_crop)
                        save_sinhvien(face_id, None, filepath, face_path, emotion, conf)
                        result_faces.append({'emotion': emotion, 'confidence': conf, 'path': face_path})
                except:
                    pass
                os.remove(temp_img)
                frame_count += 1
            cap.release()

        else:
            analysis = DeepFace.analyze(img_path=filepath, actions=['emotion'], enforce_detection=False)
            if not isinstance(analysis, list):
                analysis = [analysis]

            img = cv2.imread(filepath)
            for face_data in analysis:
                region = face_data['region']
                emotion = face_data['dominant_emotion']
                conf = face_data['emotion'][emotion]
                x, y, w, h = region['x'], region['y'], region['w'], region['h']
                face_crop = img[y:y+h, x:x+w]
                face_id = str(uuid.uuid4())
                face_path = os.path.join(current_app.config['FACES_FOLDER'], f"{face_id}.jpg")
                cv2.imwrite(face_path, face_crop)
                save_sinhvien(face_id, None, filepath, face_path, emotion, conf)
                result_faces.append({'emotion': emotion, 'confidence': conf, 'path': face_path})

    except Exception as e:
        print("Phân tích lỗi:", e)
        return "Lỗi khi phân tích file."

    return render_template('result.html', results=result_faces)
