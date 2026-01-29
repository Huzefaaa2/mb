import sqlite3
from pathlib import Path

db_path = Path('data/mb_compass.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('📊 Database Tables:')
for table in tables:
    table_name = table[0]
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    print(f'\n{table_name}:')
    for col in columns:
        print(f'  - {col[1]} ({col[2]})')

conn.close()
