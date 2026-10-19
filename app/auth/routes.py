from flask import Blueprint,flash,redirect,render_template,url_for,request
from flask_login import login_user,logout_user,current_user,login_required
from sqlalchemy import func
from ..extensions import db
from ..models import User
from .security import role_required
from .forms import LoginForm,RegisterForm

bp=Blueprint("auth",__name__,url_prefix="/auth")
@bp.get("/login")
def login():
    if current_user.is_authenticated: return redirect(url_for("auth.dashboard_redirect"))
    return render_template("auth/login.html",form=LoginForm())
@bp.post("/login")
def login_post():
    form=LoginForm()
    if not form.validate_on_submit(): return render_template("auth/login.html",form=form),400
    user=db.session.scalar(db.select(User).where(func.lower(User.email)==form.email.data.lower().strip()))
    if not user or not user.check_password(form.password.data) or not user.is_active:
        flash("Email atau password tidak valid.","error"); return render_template("auth/login.html",form=form),401
    login_user(user,remember=False); return redirect(url_for("auth.dashboard_redirect"))
@bp.get("/register")
def register(): return render_template("auth/register.html",form=RegisterForm())
@bp.post("/register")
def register_post():
    form=RegisterForm()
    if not form.validate_on_submit(): return render_template("auth/register.html",form=form),400
    email=form.email.data.lower().strip()
    if db.session.scalar(db.select(User).where(func.lower(User.email)==email)):
        form.email.errors.append("Email sudah digunakan."); return render_template("auth/register.html",form=form),400
    u=User(full_name=form.full_name.data.strip(),email=email,role="TEACHER"); u.set_password(form.password.data)
    db.session.add(u); db.session.commit(); flash("Akun guru berhasil dibuat. Silakan login.","success"); return redirect(url_for("auth.login"))
@bp.post("/logout")
def logout(): logout_user(); return redirect(url_for("index"))
@bp.get("/dashboard")
@login_required
def dashboard_redirect():
    if current_user.role=="TEACHER": return redirect(url_for("teacher.dashboard"))
    if current_user.role=="SUPERADMIN": return redirect(url_for("admin.dashboard"))
    return redirect(url_for("student.join"))
