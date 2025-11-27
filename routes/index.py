from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models.db import get_all_classes

index_bp = Blueprint('index', __name__)

@index_bp.route('/', methods=['GET', 'POST'])
def index():
    classes = get_all_classes()
    selected_class = session.get('selected_class')

    if request.method == 'POST':
        selected_class = request.form.get('class_id')
        if not selected_class:
            flash("Bạn cần chọn lớp trước khi phân tích.", "warning")
        else:
            session['selected_class'] = selected_class
            return redirect(url_for('analyze.upload'))

    if not classes:
        flash("Chưa có lớp nào, hãy tạo lớp ở mục Lớp học -> Thêm lớp học.", "info")

    return render_template('index.html', classes=classes, selected_class=selected_class)
