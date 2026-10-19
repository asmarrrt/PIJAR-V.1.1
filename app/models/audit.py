from datetime import datetime,timezone
from ..extensions import db
class AuditEvent(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    actor_user_id=db.Column(db.Integer,db.ForeignKey("user.id"))
    action=db.Column(db.String(120),nullable=False)
    entity_type=db.Column(db.String(80))
    entity_id=db.Column(db.Integer)
    created_at=db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
