from flask import Flask, request, jsonify

app = Flask(__name__)

# ----------- Sample Users with Roles -----------
users = {
    'admin1': {'role': 'admin'},
    'doc1': {'role': 'doctor'},
    'nurse1': {'role': 'nurse'},
    'patient1': {'role': 'patient'}
}

# ----------- Access Policies for Each Role -----------
access_policies = {
    'admin': ['manage_users', 'read_all_data'],
    'doctor': ['read_patient', 'write_prescription'],
    'nurse': ['read_patient'],
    'patient': ['read_own_data']
}

# ----------- Risk Behavior Tracking -----------
blocked_users = {}
risk_counter = {}

def check_access(role, action):
    return action in access_policies.get(role, [])

def simulate_risky_behavior(username):
    risk_counter[username] = risk_counter.get(username, 0) + 1
    if risk_counter[username] >= 3:
        blocked_users[username] = True
        print(f"[BLOCKED] {username} has been blocked due to repeated unauthorized attempts.")

def is_blocked(username):
    return blocked_users.get(username, False)

# ----------- Routes -----------

@app.route('/')
def home():
    return "Granular Access Control API is Running!"

@app.route('/get_patient_record')
def get_patient_record():
    username = request.args.get('username')
    user = users.get(username)

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if is_blocked(username):
        return jsonify({'error': 'User is blocked due to risky behavior'}), 403

    if not check_access(user['role'], 'read_patient'):
        simulate_risky_behavior(username)
        return jsonify({'error': 'Access denied'}), 403

    print(f"[ACCESS GRANTED] {username} accessed patient record.")
    return jsonify({'message': 'Patient record accessed successfully'})

@app.route('/manage_users')
def manage_users():
    username = request.args.get('username')
    user = users.get(username)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if is_blocked(username):
        return jsonify({'error': 'User is blocked due to risky behavior'}), 403

    if not check_access(user['role'], 'manage_users'):
        simulate_risky_behavior(username)
        return jsonify({'error': 'Access denied'}), 403

    print(f"[ACCESS GRANTED] {username} accessed user management.")
    return jsonify({'message': 'User management accessed successfully'})

@app.route('/write_prescription')
def write_prescription():
    username = request.args.get('username')
    user = users.get(username)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if is_blocked(username):
        return jsonify({'error': 'User is blocked due to risky behavior'}), 403

    if not check_access(user['role'], 'write_prescription'):
        simulate_risky_behavior(username)
        return jsonify({'error': 'Access denied'}), 403

    print(f"[ACCESS GRANTED] {username} wrote a prescription.")
    return jsonify({'message': 'Prescription written successfully'})

@app.route('/read_own_data')
def read_own_data():
    username = request.args.get('username')
    user = users.get(username)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if is_blocked(username):
        return jsonify({'error': 'User is blocked due to risky behavior'}), 403

    if not check_access(user['role'], 'read_own_data'):
        simulate_risky_behavior(username)
        return jsonify({'error': 'Access denied'}), 403

    print(f"[ACCESS GRANTED] {username} read their own data.")
    return jsonify({'message': 'Own data read successfully'})

# ----------- Run the App -----------
if __name__ == '__main__':
    app.run(debug=True)

