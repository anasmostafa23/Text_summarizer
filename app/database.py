from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
import datetime
from zoneinfo import ZoneInfo
from datetime import datetime


db = SQLAlchemy()
migrate = Migrate()


class User(UserMixin , db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    balance = db.Column(db.Float, default=0.0)

    # Add other fields you need (e.g., balance, etc.)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_balance(self):
        return self.balance
    
    def c(self, deductible):
        self.balance -= deductible

    # Flask-Login requires these methods:

    def get_id(self):
        """Returns the unique identifier for the user."""
        return str(self.id)

    def is_authenticated(self):
        """Returns True if the user is authenticated."""
        # For this simple example, it's always True.
        return True

    def is_active(self):
        """Returns True if the user is active."""
        # Here you can implement logic to check if a user is active.
        return True

    def is_anonymous(self):
        """Returns True if the user is anonymous."""
        # This will return False for authenticated users.
        return False


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    transaction_type = db.Column(db.String(50), nullable=False)  


class MLTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompt = db.Column(db.String, nullable=False)
    result = db.Column(db.Text)
