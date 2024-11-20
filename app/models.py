from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()



class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(150), unique=True, nullable=False)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password_hash = db.Column(db.String(150), nullable=False)

    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MLTask(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    prompt = db.Column(db.String, nullable=False)

    status = db.Column(db.String, default="Pending")

    result = db.Column(db.Text)
