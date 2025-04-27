from flask import Blueprint, request, jsonify, g, current_app
from flasgger import swag_from
import pandas as pd
import joblib
import bcrypt
import jwt
import datetime

from users import User
from functions import token_required, require_role
from extensions import db

import joblib

model = joblib.load('saved_models/random_forest_model.pkl')
scaler = joblib.load('saved_models/scaler.pkl')
label_encoder = joblib.load('saved_models/label_encoder.pkl')

routes = Blueprint('routes', __name__)


@routes.route('/predict', methods=['POST'])
@swag_from({
    'tags': ['Anomaly Detection'],
    'description': 'Detects login anomaly based on login time, failed attempts, and location.',
    'parameters': [
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'login_time': {'type': 'string', 'example': '10'},
                    'failed_attempts': {'type': 'integer', 'example': 3},
                    'login_location': {'type': 'string', 'example': 'New York'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Anomaly detected or normal login',
            'schema': {
                'type': 'object',
                'properties': {'message': {'type': 'string'}}
            }
        }
    }
})
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
@swag_from({
    'tags': ['Authentication'],
    'description': 'Registers a new user with a specified role.',
    'parameters': [
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'johndoe'},
                    'password': {'type': 'string', 'example': 'password123'},
                    'role': {'type': 'string', 'example': 'doctor'}
                }
            }
        }
    ],
    'responses': {
        '201': {'description': 'User successfully registered'},
        '400': {'description': 'Invalid request'},
        '409': {'description': 'Username already exists'}
    }
})
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
@swag_from({
    'tags': ['Authentication'],
    'description': 'Logs in a user and returns a JWT token.',
    'parameters': [
        {
            'name': 'data',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'johndoe'},
                    'password': {'type': 'string', 'example': 'password123'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful login with JWT token',
            'schema': {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'}
                }
            }
        },
        '401': {'description': 'Invalid credentials'}
    }
})
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'username': user.username,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})


@routes.route('/public', methods=['GET'])
@swag_from({
    'tags': ['Public Operations'],
    'description': 'A public endpoint accessible without a token.',
    'responses': {
        '200': {
            'description': 'Public access granted',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'This is a public endpoint, no token needed.'}
                }
            }
        }
    }
})
def public():
    return jsonify({'message': 'This is a public endpoint, no token needed.'})


@routes.route('/doctor/prescribe', methods=['GET'])
@token_required
@require_role('doctor')
@swag_from({
    'tags': ['Doctor Operations'],
    'description': 'Allows doctors to prescribe medicine.',
    'security': [{'BearerAuth': []}],
    'responses': {
        '200': {
            'description': 'Doctor can prescribe medicine',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Dr. johndoe can prescribe medicine.'}
                }
            }
        },
        '403': {
            'description': 'Forbidden: User is not a doctor'
        }
    }
})
def prescribe():
    return jsonify({'message': f'Dr. {g.user["username"]} can prescribe medicine.'})


@routes.route('/nurse/vitals', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Nurse Operations'],
    'description': 'Allows nurses or doctors to record vitals.',
    'security': [{'BearerAuth': []}],
    'responses': {
        '200': {
            'description': 'Vitals accessed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Nurse johndoe is accessing vitals.'}
                }
            }
        },
        '403': {'description': 'Forbidden: Only nurses or doctors can access vitals'}
    }
})
def vitals():
    if g.user['role'] not in ['nurse', 'doctor']:
        return jsonify({'message': 'Only nurses or doctors can record vitals.'}), 403
    return jsonify({'message': f'{g.user["role"].title()} {g.user["username"]} is accessing vitals.'})


@routes.route('/receptionist/schedule', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Receptionist Operations'],
    'description': 'Allows receptionists to manage appointment schedules.',
    'security': [{'BearerAuth': []}],
    'responses': {
        '200': {
            'description': 'Schedule accessed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Receptionist johndoe is managing appointments.'}
                }
            }
        },
        '403': {'description': 'Forbidden: Only receptionists can manage schedules'}
    }
})
def manage_schedule():
    if g.user['role'] != 'receptionist':
        return jsonify({'message': 'Only receptionists can manage schedules.'}), 403
    return jsonify({'message': f'Receptionist {g.user["username"]} is managing appointments.'})


@routes.route('/admin/dashboard', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Admin Operations'],
    'description': 'Allows admins to access the admin dashboard.',
    'security': [{'BearerAuth': []}],
    'responses': {
        '200': {
            'description': 'Dashboard accessed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Admin johndoe is accessing the dashboard.'}
                }
            }
        },
        '403': {'description': 'Forbidden: Only admins can access the dashboard'}
    }
})
def admin_dashboard():
    if g.user['role'] != 'admin':
        return jsonify({'message': 'Only admins can access the dashboard.'}), 403
    return jsonify({'message': f'Admin {g.user["username"]} is accessing the dashboard.'})


@routes.route('/patient/records', methods=['GET'])
@token_required
@swag_from({
    'tags': ['Patient Operations'],
    'description': 'Allows patients to view their medical records.',
    'security': [{'BearerAuth': []}],
    'responses': {
        '200': {
            'description': 'Records accessed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Patient johndoe is viewing their records.'}
                }
            }
        },
        '403': {'description': 'Forbidden: Only patients can view their records'}
    }
})
def view_records():
    if g.user['role'] != 'patient':
        return jsonify({'message': 'Only patients can view their records.'}), 403
    return jsonify({'message': f'Patient {g.user["username"]} is viewing their records.'})

