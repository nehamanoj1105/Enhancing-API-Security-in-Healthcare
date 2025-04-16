from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
import bcrypt
from users import User
from app import db

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
        hashed_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
        users = [
            User(username='alice', password=hashed_password, role='doctor'),
            User(username='bob', password=hashed_password, role='nurse'),
            User(username='claire', password=hashed_password, role='receptionist')
        ]
        db.session.bulk_save_objects(users)
        db.session.commit()
