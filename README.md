# Face Emotion Detection – Flask Web Application

A simple web application for **facial emotion recognition** built with **Flask**, **OpenCV**, and a pre–trained **Convolutional Neural Network (CNN)** model (`.h5`).  
The app can detect a face in an image or webcam frame and classify the emotion (e.g. *happy, sad, angry, neutral, surprised*, etc.).

---

## 🚀 Features

- Upload an image and detect the dominant emotion on the face  
- (Optional) Real‑time emotion detection from webcam stream  
- Face detection using Haar Cascade (OpenCV)  
- Emotion classification using a pre‑trained CNN model (`emotion_model.h5`)  
- Clean separation of routes, services, models, templates and static assets  
- Simple, responsive web UI

---

## 🛠 Tech Stack

**Backend**
- Python 3.x  
- Flask  
- OpenCV (cv2)  
- TensorFlow / Keras (for loading the `.h5` model)  
- NumPy, Pillow

**Frontend**
- HTML5, CSS3  
- Jinja2 templates  
- (Optional) Bootstrap or custom styling in `/static`

---

## 📂 Project Structure (simplified)

```bash
project-root/
│
├── auth/                # Authentication (if used)
├── database/            # Database helpers / models (if used)
├── models/              # ML / DL model helpers
├── routes/              # Flask Blueprints / route handlers
├── services/            # Business logic (preprocessing, prediction, etc.)
├── static/              # CSS, JS, images
├── templates/           # HTML templates (Jinja2)
│
├── emotion_model.h5     # Pretrained CNN emotion model
├── config.py / config/  # Application configuration (if present)
├── app.py               # Flask app entry point
└── README.md
```

> **Note:** Folder names may vary slightly depending on the final refactor,  
> but the general idea is a modular, layered Flask application.

---

## ▶️ Getting Started

### 1️⃣ Create and activate a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate   # on Windows
# source venv/bin/activate  # on macOS / Linux
```

### 2️⃣ Install dependencies

If a `requirements.txt` file is present:

```bash
pip install -r requirements.txt
```

Otherwise, install the core packages manually:

```bash
pip install flask opencv-python tensorflow keras numpy pillow
```

### 3️⃣ Run the application

```bash
python app.py
```

By default the app usually runs at:

```text
http://127.0.0.1:5000/
```

---

## 🧠 Model File (`emotion_model.h5`)

The repository **includes** the pre‑trained model file `emotion_model.h5`.  
This file is loaded at runtime to perform emotion prediction on detected faces.

If you want to retrain or replace the model:

1. Train a new CNN for emotion recognition  
2. Export it as a `.h5` file  
3. Update the model‑loading path in the corresponding service / model loader file

---

## ⚠️ Environment Variables

If you use any environment file (e.g. `google.env` or `.env`) to store API keys or credentials:

- **Do not commit real secrets** to public repositories  
- Consider adding those filenames to `.gitignore`  
- Document the expected variables in the README instead of exposing real values

---

## 📌 Author

**Vu Minh Duc**  
Fresher Python / Web Developer – NEU  
GitHub: https://github.com/minhduc-fitneu-dev
