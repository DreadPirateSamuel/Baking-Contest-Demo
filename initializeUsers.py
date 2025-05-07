from Encryption import AESCipher
import sqlite3, sys

key = b'BLhgpCL81fdLBk23HkZp8BgbT913cqt0'
iv = b'OWFJATh1Zowac2xr'
cipher = AESCipher(key,iv)

name1 = cipher.encrypt("User1".encode('utf-8')).decode('utf-8')
p1 = cipher.encrypt("8133908538".encode('utf-8')).decode('utf-8')
l1 = cipher.encrypt("Pass1".encode('utf-8')).decode('utf-8')
name2 = cipher.encrypt("User2".encode('utf-8')).decode('utf-8')
p2 = cipher.encrypt("8133908537".encode('utf-8')).decode('utf-8')
l2 = cipher.encrypt("Pass2".encode('utf-8')).decode('utf-8')
name3 = cipher.encrypt("User3".encode('utf-8')).decode('utf-8')
p3 = cipher.encrypt("8133908539".encode('utf-8')).decode('utf-8')
l3 = cipher.encrypt("Pass3".encode('utf-8')).decode('utf-8')

with sqlite3.connect('./assign6.db') as conn:
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS users''')
    cur.execute('''DROP TABLE IF EXISTS contestresults''')

    cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                age INTEGER NOT NULL,
                phoneNum TEXT NOT NULL,
                security INTEGER NOT NULL,
                login TEXT NOT NULL
            )
        ''')

    #Adding contestants for website testing.
    cur.execute('''INSERT OR IGNORE INTO users (name, age, phoneNum, security, login)
                   VALUES (?, ?, ?, ?, ?)''', (name1, 20, p1, 1, l1))
    cur.execute('''INSERT OR IGNORE INTO users (name, age, phoneNum, security, login)
                   VALUES (?, ?, ?, ?, ?)''', (name2, 10, p2, 2, l2))
    cur.execute('''INSERT OR IGNORE INTO users (name, age, phoneNum, security, login)
                   VALUES (?, ?, ?, ?, ?)''', (name3, 19, p3, 3, l3))


    conn.commit()
