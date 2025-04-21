from flask import request, jsonify, g, Blueprint, current_app
import pandas as pd
import joblib
import bcrypt
import jwt
import datetime
from users import User
from functions import token_required, require_role
from extensions import db

routes = Blueprint('routes', __name__)

scaler = joblib.load('scaler.pkl')
model = joblib.load('model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

@routes.route('/predict', methods=['POST'])
def predict_anomaly():
    data = request.get_json()
    login_time = data['login_time']
    failed_attempts = data['failed_attempts']
    login_location = data['login_location']

    input_data = pd.DataFrame([[login_time, failed_attempts, login_location]],
                              columns=['login_time', 'failed_attempts', 'login_locations'])
    location = input_data.loc[0, 'login_locations']

    if location not in label_encoder.classes_:
        if 'Unknown' not in label_encoder.classes_:
            label_encoder.classes_ = list(label_encoder.classes_) + ['Unknown']
        input_data.loc[0, 'login_locations'] = label_encoder.transform(['Unknown'])[0]
    else:
        input_data.loc[0, 'login_locations'] = label_encoder.transform([location])[0]

    input_scaled = scaler.transform(input_data.to_numpy())
    prediction = model.predict(input_scaled)

    if prediction[0] == -1:
        return jsonify({"message": "Anomaly detected"})
    else:
        return jsonify({"message": "Normal login"})

@routes.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({'message': 'Username, password, and role are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    allowed_roles = ['doctor', 'nurse', 'receptionist', 'pharmacist', 'patient', 'admin']
    if role not in allowed_roles:
        return jsonify({'message': f'Invalid role. Choose from: {", ".join(allowed_roles)}'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': f'User {username} registered successfully as {role}'}), 201

@routes.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'username': username,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})


@routes.route('/doctor/prescribe', methods=['GET'])
@token_required
@require_role('doctor')
def prescribe():
    return jsonify({'message': f'Dr. {g.user["username"]} can prescribe medicine.'})

@routes.route('/nurse/vitals', methods=['GET'])
@token_required
def vitals():
    if g.user['role'] not in ['nurse', 'doctor']:
        return jsonify({'message': 'Only nurses or doctors can record vitals.'}), 403
    return jsonify({'message': f'{g.user["role"].title()} {g.user["username"]} is accessing vitals.'})

@routes.route('/public', methods=['GET'])
def public():
    return jsonify({'message': 'This is a public endpoint, no token needed.'})

