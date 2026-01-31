"""
Migration: Add Secret Detection Columns
"""
import sys
import os
from pathlib import Path

# Add backend directory to sys.path to allow imports from app
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

def run_migration():
    print(f"Running migration on {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if columns exist (SQLite doesn't support IF NOT EXISTS for columns easily)
        try:
            print("Adding has_secrets column...")
            conn.execute(text("ALTER TABLE extracted_blocks ADD COLUMN has_secrets BOOLEAN DEFAULT 0"))
        except Exception as e:
            print(f"Column has_secrets might already exist or error: {e}")

        try:
            print("Adding secret_type column...")
            conn.execute(text("ALTER TABLE extracted_blocks ADD COLUMN secret_type VARCHAR"))
        except Exception as e:
            print(f"Column secret_type might already exist or error: {e}")
            
        conn.commit()
    
    print("Migration completed successfully.")

if __name__ == "__main__":
    run_migration()
