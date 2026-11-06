from datetime import datetime

from database.database import db


class LearningProgress(db.Model):

    __tablename__ = "learning_progress"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    roadmap = db.Column(
        db.String(100),
        nullable=False
    )

    topic = db.Column(
        db.String(255),
        nullable=False
    )

    completed = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "learning_progress",
            lazy=True
        )
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "roadmap",
            "topic",
            name="unique_user_roadmap_topic"
        ),
    )