from flask import Blueprint, render_template
from flask_login import login_required
import sqlite3

students_bp = Blueprint('students', __name__)

@students_bp.route('/students')
@login_required
def list_students():
    conn = sqlite3.connect('database/faces.db')
    c = conn.cursor()
    c.execute('''SELECT id, id_lophoc, face_path, emotion, confidence, timestamp FROM sinhvien''')
    students = c.fetchall()
    conn.close()
    return render_template('students.html', students=students)
