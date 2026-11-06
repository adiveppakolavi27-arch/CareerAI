from datetime import datetime
from database.database import db


class Application(db.Model):

    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_id = db.Column(db.String(100), nullable=True)

    job_title = db.Column(
        db.String(255),
        nullable=False
    )

    company = db.Column(
        db.String(255),
        nullable=True
    )

    location = db.Column(
        db.String(255),
        nullable=True
    )

    apply_url = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="Applied",
        nullable=False
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    applied_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("applications", lazy=True)
    )