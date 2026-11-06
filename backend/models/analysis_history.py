from datetime import datetime

from database.database import db


class AnalysisHistory(db.Model):

    __tablename__ = "analysis_history"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    ats_score = db.Column(
        db.Integer,
        nullable=False
    )

    ats_category = db.Column(
        db.String(50),
        nullable=False
    )

    match_percentage = db.Column(
        db.Integer,
        default=0
    )

    skills = db.Column(
        db.Text,
        nullable=True
    )

    report_name = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "analysis_history",
            lazy=True
        )
    )