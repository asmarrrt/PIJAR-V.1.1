from datetime import datetime,timezone,timedelta
from flask import Blueprint,flash,redirect,render_template,request,url_for,jsonify,session
from sqlalchemy import func
from ..extensions import db
from ..models import Exam,ExamAttempt,StudentAnswer,ExamQuestion
from ..utils import utcnow

bp=Blueprint("student",__name__)
@bp.route("/join",methods=["GET","POST"])
def join():
    if request.method=="POST":
        code=request.form["code"].strip().upper(); e=db.session.scalar(db.select(Exam).where(Exam.code==code))
        if not e or e.status!="PUBLISHED": flash("Kode ujian tidak valid atau ujian belum tersedia.","error"); return render_template("student/join.html")
        now=utcnow()
        if e.starts_at and now<e.starts_at or e.ends_at and now>e.ends_at: flash("Ujian tidak tersedia pada waktu ini.","error"); return render_template("student/join.html")
        return render_template("student/info.html",exam=e)
    return render_template("student/join.html")
@bp.post("/start/<int:exam_id>")
def start(exam_id):
    e=db.session.get(Exam,exam_id); name=request.form["participant_name"].strip(); identity=request.form["participant_identity"].strip()
    if not e or e.status!="PUBLISHED" or not name or not identity: return ("Invalid",400)
    now=utcnow()
    if e.starts_at and now<e.starts_at or e.ends_at and now>e.ends_at: return ("Exam unavailable",400)
    count=db.session.scalar(db.select(func.count(ExamAttempt.id)).where(ExamAttempt.exam_id==e.id,ExamAttempt.participant_identity==identity))
    if count>=e.attempts_allowed: flash("Jumlah percobaan untuk identitas ini sudah habis.","error"); return redirect(url_for("student.join"))
    a=ExamAttempt(exam_id=e.id,participant_name=name,participant_identity=identity,max_score=sum(q.weight for q in e.questions)); db.session.add(a); db.session.commit(); session["attempt_id"]=a.id; return redirect(url_for("student.take_exam",attempt_id=a.id))
@bp.get("/attempt/<int:attempt_id>")
def take_exam(attempt_id):
    a=load_attempt(attempt_id);
    if not a: return ("Not found",404)
    if a.status!="IN_PROGRESS": return redirect(url_for("results.attempt_result",attempt_id=a.id))
    remaining=max(0,int((a.started_at+timedelta(minutes=a.exam.duration_minutes)-utcnow()).total_seconds()))
    return render_template("student/take.html",attempt=a,remaining=remaining,questions=a.exam.questions)
@bp.post("/attempt/<int:attempt_id>/answer")
def save_answer(attempt_id):
    a=load_attempt(attempt_id)
    if not a or a.status!="IN_PROGRESS": return jsonify(ok=False,error="Percobaan tidak aktif."),400
    if utcnow()>a.started_at+timedelta(minutes=a.exam.duration_minutes): finalize(a); return jsonify(ok=False,error="Waktu habis."),409
    data=request.get_json(silent=True) or request.form; eq=db.session.get(ExamQuestion,int(data.get("exam_question_id")))
    if not eq or eq.exam_id!=a.exam_id: return jsonify(ok=False,error="Soal tidak valid."),400
    ans=db.session.scalar(db.select(StudentAnswer).where(StudentAnswer.attempt_id==a.id,StudentAnswer.exam_question_id==eq.id))
    if not ans: ans=StudentAnswer(attempt_id=a.id,exam_question_id=eq.id); db.session.add(ans)
    ans.answer_text=(data.get("answer_text") or "")[:10000]; ans.selected_option_id=int(data["selected_option_id"]) if data.get("selected_option_id") else None; db.session.commit(); return jsonify(ok=True,saved_at=utcnow().isoformat())
@bp.post("/attempt/<int:attempt_id>/submit")
def submit(attempt_id):
    a=load_attempt(attempt_id)
    if not a: return ("Not found",404)
    if a.status=="IN_PROGRESS": finalize(a)
    return redirect(url_for("results.attempt_result",attempt_id=a.id))
def load_attempt(attempt_id):
    a=db.session.get(ExamAttempt,attempt_id)
    if not a or session.get("attempt_id")!=a.id: return None
    return a
def finalize(a):
    if a.status!="IN_PROGRESS": return
    total=0; complete=True
    for eq in a.exam.questions:
        ans=db.session.scalar(db.select(StudentAnswer).where(StudentAnswer.attempt_id==a.id,StudentAnswer.exam_question_id==eq.id))
        if not ans: ans=StudentAnswer(attempt_id=a.id,exam_question_id=eq.id); db.session.add(ans)
        if eq.type_snapshot=="MULTIPLE_CHOICE":
            correct=next((o["id"] for o in eq.options_snapshot if o.get("is_correct")),None); ans.auto_score=eq.weight if ans.selected_option_id==correct else 0
        elif eq.type_snapshot=="TRUE_FALSE":
            correct=next((o["id"] for o in eq.options_snapshot if o.get("is_correct")),None); ans.auto_score=eq.weight if ans.selected_option_id==correct else 0
        elif eq.type_snapshot=="SHORT_ANSWER":
            expected=(eq.reference_answer_snapshot or "").strip().casefold(); actual=(ans.answer_text or "").strip().casefold(); ans.auto_score=eq.weight if actual==expected and expected else 0
        else:
            ans.auto_score=None; complete=False
        if ans.auto_score is not None: total+=ans.auto_score
    a.total_score=total; a.submitted_at=utcnow(); a.status="SUBMITTED"; a.grading_complete=complete; db.session.commit()
