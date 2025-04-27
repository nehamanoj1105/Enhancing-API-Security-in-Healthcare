# Enhancing API Security in Healthcare with Flask

## Problem Statement
Securing API-to-API communication in healthcare is crucial to protect sensitive patient data and ensure smooth interaction between various systems (EHRs, pharmacies, etc.). Traditional security methods, like perimeter-based authentication, are increasingly vulnerable to attacks. This project aims to implement Zero Trust Architecture (ZTA), ensuring all API requests are verified, authenticated, and authorized.

This solution combines Zero Trust, advanced access control, and AI to safeguard healthcare APIs from unauthorized access and data breaches.
This project aims to build a secure healthcare API backend with:

- Authentication (registration/login) using JWT tokens.
- Role-based access control (RBAC) for doctors, nurses, pharmacists, patients, receptionists, and admins.
- Anomaly detection in login behavior using machine learning (Random Forest).
- Granular access policies based on user roles.
- Interactive API documentation using Swagger UI.

## Project Overview

| Feature                   | Description                                                                |
|---------------------------|----------------------------------------------------------------------------|
| **Flask Backend**          | Developed with modular architecture using app factory pattern.            |
| **Authentication**         | Secure registration/login system using JWT tokens.                        |
| **Database**               | SQLite with SQLAlchemy ORM for managing users.                             |
| **Password Security**      | Passwords hashed with bcrypt before storage.                              |
| **Role-Based Authorization**| Only specific roles can access certain API endpoints.                     |
| **Anomaly Detection**      | Random Forest model detects suspicious login activity.                    |
| **API Documentation**      | Integrated Swagger UI with Flasgger for live API testing.                 |
| **Postman Testing**        | All APIs tested for functionality and security.                           |

## System Architecture

- **Client (Postman/Web)**: Sends HTTP requests (register, login, access protected routes).
- **Flask Application**: 
    - Authenticates user credentials and issues JWT tokens.
    - Verifies tokens for protected API routes.
    - Checks user roles for granular access control.
    - Predicts anomalies during login using a trained Random Forest model.
- **Database (SQLite)**: Stores user data securely with hashed passwords.
- **Swagger UI**: Provides interactive API documentation and testing interface.

## Key API Routes

| Method | Route                    | Access            | Description                                    |
|--------|--------------------------|-------------------|------------------------------------------------|
| POST   | /auth/register            | Public            | Register a new user.                          |
| POST   | /auth/login               | Public            | Login and receive a JWT token.                |
| POST   | /predict                  | Protected         | Detect anomalies in login behavior.           |
| GET    | /doctor/prescribe         | Doctor only       | Prescribe medicines.                          |
| GET    | /nurse/vitals             | Nurse only        | Record and view vitals.                       |
| GET    | /receptionist/appointments| Receptionist only | Manage appointments.                          |
| GET    | /pharmacist/medications   | Pharmacist only   | Manage medications.                           |
| GET    | /admin/manage-users       | Admin only        | Manage all users.                             |
| GET    | /public                   | Public            | General public information.                  |

## Anomaly Detection Details

- **Model Used**: Random Forest Classifier
- **Features Considered**:
  - login_time
  - failed_attempts
  - login_location
- **Outcome**: Detects suspicious login patterns and flags anomalies to prevent unauthorized access.

## Setup Instructions

```bash
# Clone the repository
git clone <repo-url>
cd Enhancing-API-Security-in-Healthcare

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 run.py
