from flask import Flask
from extensions import db
from routes import routes

app = Flask(__name__)

# App configs
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flasgger import Swagger

template = {
    "swagger": "2.0",
    "info": {
        "title": "Healthcare API",
        "description": "API for healthcare system with Zero Trust and JWT security",
        "version": "1.0"
    },
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    },
    "security": [{"BearerAuth": []}]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",  # ✅ IMPORTANT
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

Swagger(app, config=swagger_config, template=template)


# Register DB and routes
db.init_app(app)
app.register_blueprint(routes)

# Create DB tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

