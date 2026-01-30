
import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine

def add_column():
    print("Adding 'original_path' column to file_metadata table...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE file_metadata ADD COLUMN original_path VARCHAR"))
            conn.commit()
            print("✅ Column added successfully.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️ Column already exists.")
            else:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_column()
