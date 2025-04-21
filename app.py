from flask import Flask
from extensions import db
from routes import routes

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(routes)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
