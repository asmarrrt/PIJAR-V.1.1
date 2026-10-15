from datetime import datetime,timezone
from flask import Blueprint,flash,redirect,render_template,url_for,request
from flask_login import current_user
from sqlalchemy import func
from ..extensions import db
from ..models import Exam,Question,ExamQuestion,ExamAttempt,QuestionOption
from ..auth.security import role_required
from ..utils import generate_exam_code

bp=Blueprint("teacher",__name__)
def parse_dt(value):
    if not value: return None
    try: return datetime.fromisoformat(value)
    except ValueError: return None
@bp.get("/")
@role_required("TEACHER")
def dashboard():
    exams=db.session.scalars(db.select(Exam).where(Exam.teacher_id==current_user.id).order_by(Exam.created_at.desc())).all()
    exam_ids=[e.id for e in exams]
    participant_count=db.session.scalar(db.select(func.count(ExamAttempt.id)).where(ExamAttempt.exam_id.in_(exam_ids))) if exam_ids else 0
    active=sum(e.status=="PUBLISHED" for e in exams)
    return render_template("teacher/dashboard.html",exams=exams,participant_count=participant_count,active=active)
@bp.get("/exams")
@role_required("TEACHER")
def exams(): return render_template("teacher/exams.html",exams=db.session.scalars(db.select(Exam).where(Exam.teacher_id==current_user.id).order_by(Exam.created_at.desc())).all())
@bp.route("/exams/new",methods=["GET","POST"])
@role_required("TEACHER")
def new_exam():
    if request.method=="POST":
        try: duration=int(request.form["duration_minutes"]); attempts=int(request.form["attempts_allowed"]);
        except ValueError: flash("Durasi dan percobaan harus berupa angka.","error"); return render_template("teacher/exam_form.html",exam=None),400
        if duration<1 or attempts<1: flash("Durasi dan percobaan harus lebih dari 0.","error"); return render_template("teacher/exam_form.html",exam=None),400
        starts=parse_dt(request.form.get("starts_at")); ends=parse_dt(request.form.get("ends_at"))
        if request.form.get("starts_at") and not starts or request.form.get("ends_at") and not ends or starts and ends and starts>=ends: flash("Jadwal ujian tidak valid.","error"); return render_template("teacher/exam_form.html",exam=None),400
        e=Exam(teacher_id=current_user.id,title=request.form["title"].strip(),description=request.form.get("description","").strip(),subject=request.form["subject"].strip(),class_group=request.form.get("class_group","").strip(),duration_minutes=duration,starts_at=starts,ends_at=ends,attempts_allowed=attempts,shuffle_questions="shuffle_questions" in request.form,shuffle_options="shuffle_options" in request.form,show_results="show_results" in request.form,passing_score=float(request.form["passing_score"]) if request.form.get("passing_score") else None,code=generate_exam_code())
        db.session.add(e); db.session.commit(); flash("Ujian dibuat sebagai draft.","success"); return redirect(url_for("teacher.edit_exam",exam_id=e.id))
    return render_template("teacher/exam_form.html",exam=None)
@bp.route("/exams/<int:exam_id>/edit",methods=["GET","POST"])
@role_required("TEACHER")
def edit_exam(exam_id):
    e=get_exam(exam_id)
    if request.method=="POST":
        if e.status!="DRAFT": flash("Detail ujian hanya dapat diubah saat masih draft.","error")
        else:
            try: duration=int(request.form["duration_minutes"]); attempts=int(request.form["attempts_allowed"])
            except ValueError: flash("Durasi dan percobaan harus berupa angka.","error"); return redirect(url_for("teacher.edit_exam",exam_id=e.id))
            if duration<1 or attempts<1: flash("Durasi dan percobaan harus more than 0.","error")
            else:
                starts=parse_dt(request.form.get("starts_at")); ends=parse_dt(request.form.get("ends_at"))
                if request.form.get("starts_at") and not starts or request.form.get("ends_at") and not ends or starts and ends and starts>=ends:
                    flash("Jadwal ujian tidak valid.","error"); return redirect(url_for("teacher.edit_exam",exam_id=e.id))
                e.title=request.form["title"].strip(); e.description=request.form.get("description","").strip(); e.subject=request.form["subject"].strip(); e.class_group=request.form.get("class_group","").strip(); e.duration_minutes=duration; e.starts_at=starts; e.ends_at=ends; e.attempts_allowed=attempts; e.shuffle_questions="shuffle_questions" in request.form; e.shuffle_options="shuffle_options" in request.form; e.show_results="show_results" in request.form; e.passing_score=float(request.form["passing_score"]) if request.form.get("passing_score") else None; db.session.commit(); flash("Detail ujian diperbarui.","success")
        return redirect(url_for("teacher.edit_exam",exam_id=e.id))
    return render_template("teacher/exam_edit.html",exam=e,questions=e.questions,bank_questions=db.session.scalars(db.select(Question).where(Question.teacher_id==current_user.id).order_by(Question.created_at.desc())).all())
@bp.post("/exams/<int:exam_id>/publish")
@role_required("TEACHER")
def publish_exam(exam_id):
    e=get_exam(exam_id)
    if not e.questions: flash("Tambahkan minimal satu soal sebelum menerbitkan.","error")
    else: e.status="PUBLISHED"; db.session.commit(); flash("Ujian diterbitkan.","success")
    return redirect(url_for("teacher.edit_exam",exam_id=e.id))
@bp.post("/exams/<int:exam_id>/close")
@role_required("TEACHER")
def close_exam(exam_id): e=get_exam(exam_id); e.status="CLOSED"; db.session.commit(); return redirect(url_for("teacher.exams"))
@bp.post("/exams/<int:exam_id>/add-question/<int:question_id>")
@role_required("TEACHER")
def add_question(exam_id,question_id):
    e=get_exam(exam_id); q=db.session.get(Question,question_id)
    if not q or q.teacher_id!=current_user.id: return ("Not found",404)
    if e.status!="DRAFT": flash("Soal hanya dapat diubah pada draft.","error"); return redirect(url_for("teacher.edit_exam",exam_id=e.id))
    if any(x.question_id==q.id for x in e.questions): return redirect(url_for("teacher.edit_exam",exam_id=e.id))
    snapshot=[{"id":o.id,"text":o.text,"is_correct":o.is_correct,"position":o.position} for o in q.options]
    eq=ExamQuestion(exam_id=e.id,question_id=q.id,position=len(e.questions)+1,weight=q.default_weight,prompt_snapshot=q.prompt,type_snapshot=q.question_type,options_snapshot=snapshot,reference_answer_snapshot=q.reference_answer)
    db.session.add(eq); db.session.commit(); return redirect(url_for("teacher.edit_exam",exam_id=e.id))
@bp.post("/exams/<int:exam_id>/remove-question/<int:eq_id>")
@role_required("TEACHER")
def remove_question(exam_id,eq_id):
    e=get_exam(exam_id); eq=db.session.get(ExamQuestion,eq_id)
    if not eq or eq.exam_id!=e.id: return ("Not found",404)
    if e.status!="DRAFT": flash("Soal tidak dapat diubah setelah diterbitkan.","error")
    else: db.session.delete(eq); db.session.commit()
    return redirect(url_for("teacher.edit_exam",exam_id=e.id))
@bp.get("/question-bank")
@role_required("TEACHER")
def bank(): return render_template("teacher/bank.html",questions=db.session.scalars(db.select(Question).where(Question.teacher_id==current_user.id).order_by(Question.created_at.desc())).all())
@bp.route("/question-bank/new",methods=["GET","POST"])
@role_required("TEACHER")
def new_question():
    if request.method=="POST":
        qt=request.form["question_type"]; prompt=request.form["prompt"].strip(); weight=float(request.form.get("weight") or 1)
        if not prompt or weight<=0: flash("Pertanyaan dan bobot wajib valid.","error"); return render_template("teacher/question_form.html",q=None)
        q=Question(teacher_id=current_user.id,question_type=qt,prompt=prompt,reference_answer=request.form.get("reference_answer") or None,explanation=request.form.get("explanation") or None,default_weight=weight)
        db.session.add(q); db.session.flush()
        if qt in ("MULTIPLE_CHOICE","TRUE_FALSE"):
            texts=request.form.getlist("option_text"); correct=request.form.get("correct_option")
            for i,text in enumerate(texts):
                if text.strip(): db.session.add(QuestionOption(question=q,text=text.strip(),is_correct=str(i)==str(correct),position=i+1))
        db.session.commit(); flash("Soal disimpan.","success"); return redirect(url_for("teacher.bank"))
    return render_template("teacher/question_form.html",q=None)
@bp.post("/question-bank/<int:q_id>/delete")
@role_required("TEACHER")
def delete_question(q_id):
    q=db.session.get(Question,q_id)
    if not q or q.teacher_id!=current_user.id: return ("Not found",404)
    used=db.session.scalar(db.select(func.count(ExamQuestion.id)).where(ExamQuestion.question_id==q.id))
    if used: flash("Soal yang sudah dipakai ujian tidak dihapus.","error")
    else: db.session.delete(q); db.session.commit(); flash("Soal dihapus.","success")
    return redirect(url_for("teacher.bank"))
@bp.route("/profile",methods=["GET","POST"])
@role_required("TEACHER")
def profile():
    if request.method=="POST":
        name=request.form.get("full_name","").strip()
        if len(name)<2: flash("Nama tidak valid.","error")
        else: current_user.full_name=name; db.session.commit(); flash("Profil diperbarui.","success")
    return render_template("teacher/profile.html")

def get_exam(exam_id):
    e=db.session.get(Exam,exam_id)
    if not e or e.teacher_id!=current_user.id: from flask import abort; abort(404)
    return e
