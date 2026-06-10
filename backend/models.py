from database import db


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        nullable=False
    )


class Project(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    budget = db.Column(
        db.Integer,
        nullable=False
    )

    deadline = db.Column(
        db.String(100),
        nullable=False
    )

    client_name = db.Column(
        db.String(100),
        nullable=False
    )

    trust_score = db.Column(
        db.Integer,
        default=50
    )

    risk_level = db.Column(
        db.String(50),
        default="Medium"
    )

    ai_reason = db.Column(
        db.Text,
        default=""
    )