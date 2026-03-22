import sys
import os
from app import app
from models import db, User

def initialize_database():
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        
        # Seed Admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Seeding Admin user (admin/admin123)...")
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Optional: Seed a Judge & Parties for starting test
            judge = User(username='judge_smith', role='judge')
            judge.set_password('judge123')
            db.session.add(judge)

            accuser = User(username='accuser_one', role='accuser')
            accuser.set_password('accuser123')
            db.session.add(accuser)

            db.session.commit()
            print("Database initialized and seeded.")
        else:
            print("Admin already exists. Skipping seed.")

if __name__ == "__main__":
    # Add parent to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    initialize_database()
