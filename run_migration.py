#!/usr/bin/env python
"""Database migration script for multi-modal screening table"""

import sqlite3
from pathlib import Path
import sys

def run_migration():
    db_path = Path('data/mb_compass.db')
    print(f"Connecting to database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mb_multimodal_screenings'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating mb_multimodal_screenings table...")
            
            # Read schema file
            with open('scripts/db_schema.sql', 'r') as f:
                schema = f.read()
            
            # Extract and execute screening table creation
            in_screening_table = False
            statement = ""
            
            for line in schema.split('\n'):
                if 'CREATE TABLE IF NOT EXISTS mb_multimodal_screenings' in line:
                    in_screening_table = True
                
                if in_screening_table:
                    statement += line + '\n'
                    if line.strip().endswith(');'):
                        cursor.execute(statement)
                        print("  ✓ Created mb_multimodal_screenings table")
                        in_screening_table = False
                        statement = ""
            
            # Create indices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_screening_student 
                ON mb_multimodal_screenings(student_id)
            """)
            print("  ✓ Created idx_screening_student")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_screening_submitted 
                ON mb_multimodal_screenings(submitted_at)
            """)
            print("  ✓ Created idx_screening_submitted")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_screening_status 
                ON mb_multimodal_screenings(screening_status)
            """)
            print("  ✓ Created idx_screening_status")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_screening_personality_fit 
                ON mb_multimodal_screenings(personality_fit_level)
            """)
            print("  ✓ Created idx_screening_personality_fit")
            
            conn.commit()
            print("\n✅ Database migration complete!")
            return True
        else:
            print("✓ mb_multimodal_screenings table already exists")
            
            # Verify indices
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='mb_multimodal_screenings'")
            indices = cursor.fetchall()
            print(f"✓ {len(indices)} indices found")
            
            return True
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
