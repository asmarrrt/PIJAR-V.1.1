from datetime import datetime,timezone
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import current_user
from ..extensions import db
from ..models import Exam,ExamAttempt,StudentAnswer
from ..auth.security import role_required
bp=Blueprint("results",__name__)
@bp.get("/exam/<int:exam_id>")
@role_required("TEACHER")
def exam_results(exam_id):
    e=db.session.get(Exam,exam_id)
    if not e or e.teacher_id!=current_user.id: return ("Not found",404)
    attempts=db.session.scalars(db.select(ExamAttempt).where(ExamAttempt.exam_id==e.id).order_by(ExamAttempt.submitted_at.desc())).all()
    scores=[a.total_score for a in attempts if a.total_score is not None]
    return render_template("results/exam.html",exam=e,attempts=attempts,highest=max(scores) if scores else None,lowest=min(scores) if scores else None,average=(sum(scores)/len(scores)) if scores else None,pending=sum(not a.grading_complete for a in attempts))
@bp.get("/attempt/<int:attempt_id>")
def attempt_result(attempt_id):
    a=db.session.get(ExamAttempt,attempt_id)
    if not a: return ("Not found",404)
    if current_user.is_authenticated and current_user.role=="TEACHER":
        if a.exam.teacher_id!=current_user.id: return ("Not found",404)
    elif request.args.get("student")!="1":
        from flask import session
        if session.get("attempt_id")!=a.id: return ("Forbidden",403)
    if (not current_user.is_authenticated or current_user.role!="TEACHER") and not a.exam.show_results:
        return render_template("results/hidden.html",exam=a.exam)
    return render_template("results/attempt.html",attempt=a)
@bp.post("/attempt/<int:attempt_id>/grade")
@role_required("TEACHER")
def grade(attempt_id):
    a=db.session.get(ExamAttempt,attempt_id)
    if not a or a.exam.teacher_id!=current_user.id: return ("Not found",404)
    for ans in a.answers:
        if ans.exam_question.type_snapshot=="ESSAY":
            raw=request.form.get(f"score_{ans.id}")
            if raw is not None and raw!="":
                score=max(0,min(float(raw),ans.exam_question.weight)); ans.manual_score=score; ans.manual_note=request.form.get(f"note_{ans.id}","")[:5000]; ans.graded_at=datetime.now(timezone.utc)
    total=0; complete=True
    for ans in a.answers:
        if ans.exam_question.type_snapshot=="ESSAY":
            if ans.manual_score is None: complete=False
            else: total+=ans.manual_score
        else: total+=(ans.auto_score or 0)
    a.total_score=total; a.grading_complete=complete; db.session.commit(); flash("Penilaian disimpan.","success"); return redirect(url_for("results.attempt_result",attempt_id=a.id))
