from app import app, db
import sys

def reset_db():
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            print("Database tables dropped and recreated successfully")
        except Exception as e:
            print(f"Error resetting database: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "reset_db":
            reset_db()