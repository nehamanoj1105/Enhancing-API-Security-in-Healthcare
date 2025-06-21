from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
import bcrypt
from users import User
from extensions import db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            g.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated

def require_role(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if g.user.get('role') != role:
                return jsonify({'message': 'Access denied: insufficient role'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

def create_default_users():
    if User.query.count() == 0:
        password = 'password123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users = [
            User(username='dr_arjun', password=hashed_password, role='doctor'),
            User(username='dr_sneha', password=hashed_password, role='doctor'),
            User(username='nurse_riya', password=hashed_password, role='nurse'),
            User(username='nurse_karthik', password=hashed_password, role='nurse'),
            User(username='receptionist_meera', password=hashed_password, role='receptionist'),
            User(username='pharma_rakesh', password=hashed_password, role='pharmacist'),
            User(username='pharma_pooja', password=hashed_password, role='pharmacist'),
            User(username='admin_ankit', password=hashed_password, role='admin'),
            User(username='patient_rahul', password=hashed_password, role='patient'),
            User(username='patient_divya', password=hashed_password, role='patient')
        ]

        db.session.bulk_save_objects(users)
        db.session.commit()
        print("Default Indian users created.")
