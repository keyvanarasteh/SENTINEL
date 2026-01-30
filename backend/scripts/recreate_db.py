import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, engine, init_db
# Import all models to ensure they are registered with Base.metadata
from app.models import (
    FileMetadata, 
    ExtractedBlock, 
    UserFeedback,
    Session,
    SessionFile,
    ExtractionStats,
    TextInput
)

from app.database import Base, engine, init_db, DATABASE_URL

def recreate_database():
    print(f"🔧 Target Database URL: {DATABASE_URL}")
    
    # Extract path from sqlite:///...
    if "sqlite:///" in str(DATABASE_URL):
        db_path = str(DATABASE_URL).replace("sqlite:///", "")
        print(f"🗑️  Removing existing database at: {db_path}")
        if os.path.exists(db_path):
            os.remove(db_path)
            print("   Database file removed.")
        else:
            print("   No existing database found at that path.")
    
    print("🏗️  Creating new database tables...")
    # This creates the tables based on the imported models
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"   Tables found: {', '.join(tables)}")
    
    # Check columns for file_metadata
    columns = [c['name'] for c in inspector.get_columns('file_metadata')]
    print(f"   Columns in file_metadata: {', '.join(columns)}")
    
    if 'batch_id' in columns and 'processing_status' in columns:
        print("✅ Schema verification PASSED: v2.0 columns exist.")
    else:
        print("❌ Schema verification FAILED: Missing v2.0 columns!")

if __name__ == "__main__":
    recreate_database()
