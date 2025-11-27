from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from config import Config
from models.db import init_db, connect_db
from models.face_analysis import analyze_image
from datetime import date as dt_date


app = Flask(__name__)
app.config.from_object(Config)

init_db()

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password or not confirm_password:
            flash('Vui lòng nhập đầy đủ thông tin')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Mật khẩu không trùng khớp')
            return redirect(url_for('signup'))

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Tên đăng nhập đã tồn tại')
            conn.close()
            return redirect(url_for('signup'))

        password_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO user (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        flash('Đăng ký thành công')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT uid, password_hash FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['logged_in'] = True
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        else:
            flash('Sai tài khoản hoặc mật khẩu')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT uid FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['reset_user_id'] = user[0]
            return redirect(url_for('reset_password'))
        else:
            flash('Không tìm thấy tài khoản này')
            return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Mật khẩu không trùng khớp')
            return redirect(url_for('reset_password'))
        user_id = session.get('reset_user_id')
        if user_id:
            password_hash = generate_password_hash(password)
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET password_hash = ? WHERE uid = ?", (password_hash, user_id))
            conn.commit()
            conn.close()
            session.pop('reset_user_id', None)
            flash('Đổi mật khẩu thành công. Vui lòng đăng nhập lại.')
            return redirect(url_for('login'))
        else:
            flash('Quy trình reset lỗi, hãy thử lại.')
            return redirect(url_for('forgot_password'))
    return render_template('reset_password.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_lophoc, ten_lop FROM lophoc")
    classes = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        file = request.files['file']
        class_id = request.form.get('class_id')
        if file and class_id:
            filename = secure_filename(file.filename)
            save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(save_path)

            # Gọi hàm phân tích
            results = analyze_image(save_path, class_id)

            # Kiểm tra nếu không phát hiện khuôn mặt
            if isinstance(results, dict) and 'error' in results:
                flash(results['error'])
                return redirect(url_for('home'))

            # Nếu có khuôn mặt, redirect qua trang chi tiết phân tích
            return redirect(url_for('analyze', filename=filename, class_id=class_id))
        else:
            flash('Bạn phải chọn lớp học và file để upload!')

    return render_template('home.html', classes=classes)

@app.route('/classes', methods=['GET', 'POST'])
def classes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_lophoc, ten_lop, so_sv FROM lophoc")
    classes = cursor.fetchall()
    conn.close()

    return render_template('classes.html', classes=classes)

@app.route('/add_class', methods=['POST'])
def add_class():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    ten_lop = request.form.get('ten_lop')
    so_sv = request.form.get('so_sv')

    if ten_lop and so_sv.isdigit():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lophoc WHERE ten_lop = ?", (ten_lop,))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("INSERT INTO lophoc (ten_lop, so_sv, uid) VALUES (?, ?, ?)",
                           (ten_lop, int(so_sv), session.get('user_id', 1)))
            conn.commit()
            flash('Thêm lớp thành công!')
        else:
            flash('Tên lớp đã tồn tại!')
        conn.close()
    else:
        flash('Vui lòng nhập tên lớp và số sinh viên hợp lệ.')
    return redirect(url_for('classes'))


@app.route('/analyze/<filename>/<int:class_id>')
def analyze(filename, class_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT face_path, emotion, confidence, timestamp 
        FROM sinhvien
        WHERE id_lophoc = ? 
        ORDER BY timestamp DESC
    """, (class_id,))
    students_raw = cursor.fetchall()
    conn.close()

    students = []
    for s in students_raw:
        students.append({
            'face_path': s[0],
            'emotion': s[1],
            'confidence': round(s[2]*100, 2),
            'timestamp': s[3]
        })

    return render_template('analysis_detail.html', results=students)


@app.route('/stats')
def stats():
    class_id = request.args.get('class_id', type=int)
    selected_date = request.args.get('date')
    if not selected_date:
        selected_date = dt_date.today().isoformat()

    conn = connect_db()
    cursor = conn.cursor()

    # Lấy toàn bộ lớp để đổ vào select box
    cursor.execute("SELECT id_lophoc, ten_lop FROM lophoc")
    all_classes = cursor.fetchall()

    # Nếu chưa chọn lớp thì chọn lớp đầu tiên
    if not class_id and all_classes:
        class_id = all_classes[0][0]


    # Lấy danh sách ngày có phân tích
    date_filter_sql = "AND DATE(timestamp) = ?" if selected_date else ""
    date_filter_param = [selected_date] if selected_date else []

    cursor.execute(f"""
        SELECT DATE(timestamp)
        FROM sinhvien
        WHERE id_lophoc = ?
        {date_filter_sql}
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
    """, (class_id, *date_filter_param))
    dates = [row[0] for row in cursor.fetchall()]

    # sau khi lấy emotion data
    cursor.execute(f"""
        SELECT COUNT(*) FROM sinhvien
        WHERE id_lophoc = ?
        {date_filter_sql}
    """, (class_id, *date_filter_param))
    total_images = cursor.fetchone()[0]

    # Lấy biểu cảm theo ngày
    cursor.execute(f"""
        SELECT emotion, DATE(timestamp), COUNT(*)
        FROM sinhvien
        WHERE id_lophoc = ?
        {date_filter_sql}
        GROUP BY emotion, DATE(timestamp)
    """, (class_id, *date_filter_param))
    rows = cursor.fetchall()

    # Đếm tổng ảnh
    cursor.execute(f"""
            SELECT COUNT(*) FROM sinhvien
            WHERE id_lophoc = ?
            {date_filter_sql}
        """, (class_id, *date_filter_param))
    conn.close()

    # Chuẩn hóa dữ liệu
    emotions = set(row[0] for row in rows)
    emotion_counts = {e: [0]*len(dates) for e in emotions}
    date_index = {d: i for i, d in enumerate(dates)}

    for emotion, date, count in rows:
        emotion_counts[emotion][date_index[date]] = count

    colors = {
        'happy': '#f39c12',
        'sad': '#3498db',
        'angry': '#e74c3c',
        'neutral': '#95a5a6',
        'surprise': '#9b59b6',
        'fear': '#16a085',
        'disgust': '#2ecc71'
    }

    return render_template('emotion_stats_chart.html', labels=dates,
                           emotion_counts=emotion_counts, colors=colors, all_classes=all_classes,
                           selected_class_id=class_id, selected_date=selected_date,
                           current_date=selected_date , total_images=total_images)



if __name__ == '__main__':
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    app.run(debug=True)