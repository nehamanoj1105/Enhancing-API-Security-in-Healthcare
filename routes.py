from flask import Blueprint, request, jsonify, g, current_app
import pandas as pd
import joblib
import bcrypt
import jwt
import datetime
import numpy as np
import shap

from models import User
from extensions import db
from middleware import token_required, require_role

routes = Blueprint('routes', __name__)

# Load model and scaler
model = joblib.load('SS-Model/SSModel/xgb_model.pkl')
scaler = joblib.load('SS-Model/SSModel/scaler.pkl')
explainer = shap.Explainer(model)

print("✅ Model and Scaler Loaded")
print("Model:", model)
print("Scaler:", scaler)

# ------------------- Prediction Endpoint -------------------
@routes.route('/predict', methods=['POST'])
def predict_anomaly():
    data = request.get_json()

    expected_features = [
        'Header_Length', 'Protocol Type', 'Duration', 'Rate', 'Srate', 'Drate',
        'fin_flag_number', 'syn_flag_number', 'rst_flag_number', 'psh_flag_number',
        'ack_flag_number', 'ece_flag_number', 'cwr_flag_number', 'ack_count',
        'syn_count', 'fin_count', 'rst_count', 'HTTP', 'HTTPS', 'DNS', 'Telnet',
        'SMTP', 'SSH', 'IRC', 'TCP', 'UDP', 'DHCP', 'ARP', 'ICMP', 'IGMP',
        'IPv', 'LLC', 'Tot sum', 'Min', 'Max', 'AVG', 'Std', 'Tot size', 'IAT',
        'Number', 'Magnitue', 'Radius', 'Covariance', 'Variance', 'Weight'
    ]

    input_dict = {feature: 0.0 for feature in expected_features}
    input_dict.update({k: v for k, v in data.items() if k in input_dict})
    df = pd.DataFrame([input_dict])

    try:
        X = scaler.transform(df)
        pred = model.predict(X)[0]
        msg = "Anomaly detected" if pred == 1 else "Normal login"

        # SHAP explanation
        shap_values = explainer(X)
        feature_contribs = dict(zip(expected_features, shap_values.values[0].tolist()))

        return jsonify({
            'message': msg,
            'shap_explanation': feature_contribs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------- User Registration -------------------
@routes.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role     = data.get('role')

    if not username or not password or not role:
        return jsonify({'message': 'username, password, and role are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'username already exists'}), 409

    valid_roles = ['doctor','nurse','receptionist','pharmacist','patient','admin']
    if role not in valid_roles:
        return jsonify({'message': f'invalid role – choose one of {valid_roles}'}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user = User(username=username, password=hashed, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': f'user {username} registered as {role}'}), 201

# ------------------- User Login -------------------
@routes.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password):
        return jsonify({'message': 'invalid credentials'}), 401

    token = jwt.encode({
        'username': user.username,
        'role':     user.role,
        'exp':      datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token})

# ------------------- Protected Role-Based Endpoints -------------------
@routes.route('/public', methods=['GET'])
def public():
    return jsonify({'message': 'This is a public endpoint'}), 200

@routes.route('/doctor/prescribe', methods=['GET'])
@token_required
@require_role('doctor')
def prescribe():
    return jsonify({'message': f'Dr. {g.user["username"]} may prescribe'}), 200

@routes.route('/nurse/vitals', methods=['GET'])
@token_required
def vitals():
    if g.user['role'] not in ['nurse','doctor']:
        return jsonify({'message': 'Only nurses or doctors may access vitals'}), 403
    return jsonify({'message': f'{g.user["role"].title()} {g.user["username"]} accessing vitals'}), 200

@routes.route('/receptionist/schedule', methods=['GET'])
@token_required
@require_role('receptionist')
def manage_schedule():
    return jsonify({'message': f'Receptionist {g.user["username"]} managing schedule'}), 200

@routes.route('/admin/dashboard', methods=['GET'])
@token_required
@require_role('admin')
def admin_dashboard():
    return jsonify({'message': f'Admin {g.user["username"]} dashboard access'}), 200

@routes.route('/patient/records', methods=['GET'])
@token_required
@require_role('patient')
def view_records():
    return jsonify({'message': f'Patient {g.user["username"]} viewing records'}), 200

