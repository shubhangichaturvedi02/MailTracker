from app import db
# from datetime import datetime
from sqlalchemy import text
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, DateTime


class User(db.Model):
    __table_args__ = {
        'schema': 'public'
    }
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    is_active = db.Column(db.Boolean,default=True)
    created_on = db.Column(DateTime(timezone=True), server_default=func.now())
    last_login = db.Column(db.DATETIME)
    jwt_token = db.Column(db.Text)

class SentEmail(db.Model):
    __table_args__ = {
        'schema': 'public'
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(50), unique=True)
    user_id = db.Column(db.Integer)
    subject = db.Column(db.Text)
    body = db.Column(db.Text)
    received = db.Column(db.Boolean)
    sent_time = db.Column(DateTime(timezone=True))