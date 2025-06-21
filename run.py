from app import create_app, db
from functions import create_default_users

app = create_app()

with app.app_context():
    db.create_all()              # ✅ Create all tables from models
    create_default_users()       # ✅ Insert default data after tables exist

if __name__ == "__main__":
    app.run(debug=True)

