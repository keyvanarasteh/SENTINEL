"""
Database migration script for HPES v2.0
Adds support for sessions, analytics, and text inputs
"""
from sqlalchemy import create_engine, text
import os
from datetime import datetime


def get_engine():
    """Get database engine"""
    db_url = os.getenv('DATABASE_URL', 'sqlite:///data/hpes.db')
    return create_engine(db_url)


def upgrade():
    """Apply v2.0 schema changes"""
    engine = get_engine()
    
    print("🔄 Starting database migration to v2.0...")
    
    with engine.connect() as conn:
        # Create sessions table
        print("  Creating 'sessions' table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                session_metadata TEXT  -- JSON stored as TEXT in SQLite (renamed from 'metadata')
            )
        """))
        
        # Create session_files junction table
        print("  Creating 'session_files' table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS session_files (
                session_id INTEGER NOT NULL,
                file_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, file_id),
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES file_metadata(id) ON DELETE CASCADE
            )
        """))
        
        # Create extraction_stats table
        print("  Creating 'extraction_stats' table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS extraction_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_files INTEGER DEFAULT 0,
                total_blocks INTEGER DEFAULT 0,
                language_stats TEXT,  -- JSON as TEXT
                avg_confidence REAL
            )
        """))
        
        # Create text_inputs table
        print("  Creating 'text_inputs' table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS text_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source_type TEXT DEFAULT 'paste',  -- 'paste' or 'markdown'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_hash TEXT UNIQUE
            )
        """))
        
        # Add new columns to existing tables (if they don't exist)
        print("  Adding 'session_id' to 'extracted_blocks'...")
        try:
            conn.execute(text("""
                ALTER TABLE extracted_blocks 
                ADD COLUMN session_id INTEGER REFERENCES sessions(id)
            """))
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"    Warning: {e}")
        
        print("  Adding 'batch_id' to 'file_metadata'...")
        try:
            conn.execute(text("""
                ALTER TABLE file_metadata 
                ADD COLUMN batch_id TEXT
            """))
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"    Warning: {e}")
        
        print("  Adding 'processing_status' to 'file_metadata'...")
        try:
            conn.execute(text("""
                ALTER TABLE file_metadata 
                ADD COLUMN processing_status TEXT DEFAULT 'pending'
            """))
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"    Warning: {e}")
        
        # Create indexes for better performance (only if tables exist)
        print("  Creating indexes...")
        
        # Check if tables exist before creating indexes
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        existing_tables = {row[0] for row in result}
        
        if 'extracted_blocks' in existing_tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_blocks_session 
                ON extracted_blocks(session_id)
            """))
        
        if 'file_metadata' in existing_tables:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_files_batch 
                ON file_metadata(batch_id)
            """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sessions_created 
            ON sessions(created_at DESC)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stats_date 
            ON extraction_stats(date DESC)
        """))
        
        conn.commit()
        print("✅ Migration completed successfully!")


def downgrade():
    """Rollback v2.0 changes (optional)"""
    engine = get_engine()
    
    print("⚠️  Rolling back v2.0 migration...")
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS session_files"))
        conn.execute(text("DROP TABLE IF EXISTS sessions"))
        conn.execute(text("DROP TABLE IF EXISTS extraction_stats"))
        conn.execute(text("DROP TABLE IF EXISTS text_inputs"))
        
        # Note: SQLite doesn't support DROP COLUMN easily
        # Would need to recreate tables to remove columns
        
        conn.commit()
        print("✅ Rollback completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
