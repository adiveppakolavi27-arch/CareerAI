from datetime import datetime
from database.database import db


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_id = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    apply_url = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(50), default="Adzuna")

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("saved_jobs", lazy=True)
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "job_id",
            "source",
            name="unique_saved_job_per_user"
        ),
    )