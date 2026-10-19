import secrets,string
from datetime import datetime,timezone
def generate_exam_code():
    from .extensions import db
    from .models import Exam
    while True:
        code="".join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(8))
        if not db.session.scalar(db.select(Exam).where(Exam.code==code)): return code
def utcnow(): return datetime.now(timezone.utc)
