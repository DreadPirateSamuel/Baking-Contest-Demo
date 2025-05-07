from Encryption import AESCipher
import sqlite3, sys

key = b'BLhgpCL81fdLBk23HkZp8BgbT913cqt0'
iv = b'OWFJATh1Zowac2xr'
cipher = AESCipher(key,iv)

with sqlite3.connect('./assign6.db') as conn:
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS contestresults''')

    cur.execute('''
            CREATE TABLE IF NOT EXISTS contestresults (
                entryid INTEGER PRIMARY KEY AUTOINCREMENT,

                userid INTEGER NOT NULL,

                bakingitem TEXT NOT NULL,

                exVoteNum INTEGER NOT NULL,

                okVoteNum INTEGER NOT NULL,

                bdVoteNum INTEGER NOT NULL
            )
        ''')

    #Adding entries for website testing.
    cur.execute('''INSERT OR IGNORE INTO contestresults (userid, bakingitem, exVoteNum, okVoteNum, bdVoteNum)
                   VALUES (?, ?, ?, ?, ?)''', (1, 'Apple Pie', 3, 2, 1))
    cur.execute('''INSERT OR IGNORE INTO contestresults (userid, bakingitem, exVoteNum, okVoteNum, bdVoteNum)
                   VALUES (?, ?, ?, ?, ?)''', (2, 'Peach Cobbler', 5, 7, 4))
    cur.execute('''INSERT OR IGNORE INTO contestresults (userid, bakingitem, exVoteNum, okVoteNum, bdVoteNum)
                   VALUES (?, ?, ?, ?, ?)''', (3, 'Pumpkin Pie', 1, 9, 2))

    conn.commit()
