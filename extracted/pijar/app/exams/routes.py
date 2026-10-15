from flask import Blueprint,redirect,url_for
bp=Blueprint("exams",__name__)
@bp.get("/<code>")
def public_exam_code(code): return redirect(url_for("student.join",code=code.upper()))
