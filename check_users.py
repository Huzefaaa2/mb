import sqlite3
from pathlib import Path

DB_PATH = Path('data') / 'mb_compass.db'
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

print('All users:')
cursor.execute('SELECT user_id, login_id, student_id FROM mb_users')
users = cursor.fetchall()
for user in users:
    print(f'  - User ID: {user[0]}, Login: {user[1]}, Student: {user[2]}')

# Count modules per user
print('\nModules per user:')
cursor.execute('SELECT user_id, COUNT(*) as count FROM learning_modules GROUP BY user_id')
results = cursor.fetchall()
for user_id, count in results:
    print(f'  - User ID {user_id}: {count} modules')

conn.close()
