from app import create_app, db
from functions import create_default_users

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_users()
    app.run(debug=True)
