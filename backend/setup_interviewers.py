"""
Setup sample interviewers for the automation to work
"""

from app.models.models import User, engine
from sqlalchemy.orm import sessionmaker

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_interviewers():
    """Create sample interviewers for testing automation"""
    
    db = SessionLocal()
    
    try:
        # Check if interviewers already exist
        existing = db.query(User).filter(User.role == 'interviewer').first()
        if existing:
            print("✅ Interviewers already exist")
            return
        
        # Create sample interviewers
        interviewers = [
            {
                'name': 'Bob Smith',
                'email': 'bob.smith@company.com',
                'role': 'interviewer',
                # Add more fields as needed for your User model
            },
            {
                'name': 'Alice Johnson', 
                'email': 'alice.johnson@company.com',
                'role': 'interviewer',
            },
            {
                'name': 'Carol Davis',
                'email': 'carol.davis@company.com', 
                'role': 'interviewer',
            }
        ]
        
        for interviewer_data in interviewers:
            interviewer = User(
                name=interviewer_data['name'],
                email=interviewer_data['email'],
                role=interviewer_data['role']
            )
            db.add(interviewer)
        
        db.commit()
        print(f"✅ Created {len(interviewers)} sample interviewers")
        
        # List created interviewers
        created = db.query(User).filter(User.role == 'interviewer').all()
        for interviewer in created:
            print(f"   📋 {interviewer.name} ({interviewer.email})")
    
    except Exception as e:
        print(f"❌ Error creating interviewers: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_interviewers()
