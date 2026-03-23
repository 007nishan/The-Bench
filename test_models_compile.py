import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'flask_replica'))

from app import app, db
from models import JudgeProfile, Comment

def test_compile():
    print("Testing models compilation...")
    with app.app_context():
        # This will create missing tables (JudgeProfile, Comment)
        db.create_all()
        print("✅ New tables created/verified successfully.")
        
        # Test imports worked
        print("JudgeProfile Columns:", [c.name for c in JudgeProfile.__table__.columns])
        print("Comment Columns:", [c.name for c in Comment.__table__.columns])

if __name__ == "__main__":
    test_compile()
