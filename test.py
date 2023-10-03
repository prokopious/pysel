import sqlite3

conn = sqlite3.connect('C:\\Users\\cirru\\OneDrive\\Desktop\\pysel\\pysel\\dev.db')  # Replace with your SQLite database file path
cursor = conn.cursor()

cursor.execute('SELECT * FROM POST')  
rows = cursor.fetchall()
with open('output.txt', 'w', encoding='utf-8') as f:
    for row in rows:
        f.write(str(row) + '\n')

