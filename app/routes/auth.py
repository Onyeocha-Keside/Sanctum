from flask import Blueprint, request, jsonify
from app.models import User
from app import database, bcrypt
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__)

@bp.route('/')
def home():
    return "Welcome to Sanctum!"

@bp.route('/register', methods =['GET',"POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or email already exist"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, email=email, password_hash = hashed_password)
    database.session.add(new_user)
    database.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@bp.route('/login', methods = ['GET',"POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email = data.get('email')).first()

    if user and bcrypt.check_passwor_hash(user.password_hash, data.get("password")):
        access_token = create_access_token(indentity = user.id)
        return jsonify(access_token = access_token), 200
    return jsonify({"message": "Invalid email or password"}), 401
