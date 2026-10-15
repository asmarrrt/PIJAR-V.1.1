from datetime import datetime,timezone
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from ..extensions import db

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    full_name=db.Column(db.String(150),nullable=False)
    email=db.Column(db.String(255),unique=True,index=True,nullable=False)
    password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(20),nullable=False,default="TEACHER",index=True)
    is_active=db.Column(db.Boolean,nullable=False,default=True)
    created_at=db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
    exams=db.relationship("Exam",back_populates="teacher",cascade="all, delete-orphan")
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)
    @property
    def is_teacher(self): return self.role=="TEACHER"
    @property
    def is_superadmin(self): return self.role=="SUPERADMIN"
