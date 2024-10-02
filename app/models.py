from app import database
from datetime import datetime

class User(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    username = database.Column(database.String(64), unique = True, nullable = False)
    email = database.Column(database.String(120), unique = True, nullable = False)
    password_hash = database.Column(database.String(128), nullable = False)
    #documents = database.relationship('Document', backref='owner', lazy=True)

class Document(database.Model):
    id = database.Column(database.Integer, primary_key = True)
    filename = database.Column(database.String(128), nullable = False)
    user_id = database.Column(database.Integer, database.ForeignKey("user.id"), nullable = False)
    upload_data = database.Column(database.DateTime, default = datetime.utcnow)
    summary = database.Column(database.Text)
    qa_pairs = database.Column(database.Text)
    #summary = database.Column(database.Text)

