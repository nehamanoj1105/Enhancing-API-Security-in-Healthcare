from flask import Flask
from extensions import db
from routes import routes

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # or your DB URI
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    app.register_blueprint(routes)

    return app

