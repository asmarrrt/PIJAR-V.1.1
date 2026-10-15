from flask import Blueprint,render_template,request,redirect,url_for,flash
from sqlalchemy import func
from ..extensions import db
from ..models import User,Exam,ExamAttempt
from ..auth.security import role_required
bp=Blueprint("admin",__name__)
@bp.get("/")
@role_required("SUPERADMIN")
def dashboard():
    q=request.args.get("q","").strip()
    teachers=db.session.scalars(db.select(User).where(User.role=="TEACHER",User.full_name.ilike(f"%{q}%") if q else True).order_by(User.created_at.desc())).all()
    return render_template("admin/dashboard.html",teachers=teachers,teacher_count=db.session.scalar(db.select(func.count(User.id)).where(User.role=="TEACHER")),exam_count=db.session.scalar(db.select(func.count(Exam.id))),attempt_count=db.session.scalar(db.select(func.count(ExamAttempt.id))))
@bp.post("/teacher/<int:user_id>/toggle")
@role_required("SUPERADMIN")
def toggle_teacher(user_id):
    u=db.session.get(User,user_id)
    if not u or u.role!="TEACHER": return ("Not found",404)
    u.is_active=not u.is_active; db.session.commit(); flash("Status akun diperbarui.","success"); return redirect(url_for("admin.dashboard"))
@bp.get("/exams")
@role_required("SUPERADMIN")
def exams(): return render_template("admin/exams.html",exams=db.session.scalars(db.select(Exam).order_by(Exam.created_at.desc())).all())
