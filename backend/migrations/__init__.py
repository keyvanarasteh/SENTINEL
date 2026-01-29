"""
Migration runner
"""
from migrations import migration_001_v2_enhancements

if __name__ == "__main__":
    migration_001_v2_enhancements.upgrade()
