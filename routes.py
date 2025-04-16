from flask import request, jsonify, g
from users import User
import bcrypt
import jwt
import datetime
from functions import token_required, require_role

def register_routes(app):
    @app.route('/auth/login', methods=['POST'])
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
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    @app.route('/doctor/prescribe', methods=['GET'])
    @token_required
    @require_role('doctor')
    def prescribe():
        return jsonify({'message': f'Dr. {g.user["username"]} can prescribe medicine.'})

    @app.route('/nurse/vitals', methods=['GET'])
    @token_required
    def vitals():
        if g.user['role'] not in ['nurse', 'doctor']:
            return jsonify({'message': 'Only nurses or doctors can record vitals.'}), 403
        return jsonify({'message': f'{g.user["role"].title()} {g.user["username"]} is accessing vitals.'})

    @app.route('/public', methods=['GET'])
    def public():
        return jsonify({'message': 'This is a public endpoint, no token needed.'})