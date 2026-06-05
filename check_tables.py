import sqlite3

conn = sqlite3.connect('training_bot.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()

print('Tables in DB:')
for table in sorted(tables):
    print(f'  - {table[0]}')

conn.close()
