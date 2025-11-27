from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.db import get_all_classes, create_class, get_analyses_by_class

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/classes', methods=['GET', 'POST'])
def classes():
    if request.method == 'POST':
        ten_lop = request.form.get('ten_lop')
        if ten_lop:
            create_class(ten_lop)
            flash("Thêm lớp thành công.", "success")
        else:
            flash("Tên lớp không được để trống.", "warning")
        return redirect(url_for('classes.classes'))

    classes = get_all_classes()
    return render_template('classes.html', classes=classes)

@classes_bp.route('/classes/<class_id>/<analysis_id>')
def analysis_detail(class_id, analysis_id):
    students = get_analyses_by_class(class_id, analysis_id)
    return render_template('analysis_detail.html', students=students)
