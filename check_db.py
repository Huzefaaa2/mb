import sqlite3
from pathlib import Path

DB_PATH = Path('data') / 'mb_compass.db'
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for table in tables:
    print(f'  - {table[0]}')

# Check learning_modules table structure
print('\nLearning Modules Table Structure:')
cursor.execute('PRAGMA table_info(learning_modules)')
columns = cursor.fetchall()
for col in columns:
    print(f'  - {col[1]} ({col[2]})')

# Count rows
cursor.execute('SELECT COUNT(*) FROM learning_modules')
count = cursor.fetchone()[0]
print(f'\nTotal learning modules: {count}')

# Check latest modules
if count > 0:
    print('\nLatest 5 modules:')
    cursor.execute('SELECT module_id, title, status, user_id FROM learning_modules ORDER BY assigned_date DESC LIMIT 5')
    rows = cursor.fetchall()
    for row in rows:
        print(f'  - {row[0]}: {row[1]} ({row[2]}) - User ID: {row[3]}')

conn.close()
