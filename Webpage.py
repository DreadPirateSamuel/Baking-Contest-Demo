from flask import Flask, request, render_template, redirect, url_for, session
from Encryption import AESCipher
import sqlite3, sys

app = Flask(__name__)
app.secret_key = 'samuelyoder' #Used with session

DATABASE = 'assign6.db'
host = '127.0.0.1'
port = 50000

if (len(sys.argv) > 1):
    host = sys.argv[1]

if len(sys.argv) > 2:
    port = int(sys.argv[2])

def dbStart():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
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

        conn.commit()

#New default page is where you login.
@app.route('/')
def login():
    session.clear()
    return render_template('login.html')


#Checks the username/password entered against names/logins in the DB.
@app.route('/login', methods=['GET', 'POST'])
def handleLogin():
    securityLevel = session.get('securityLevel', 0)

    #If the user tries to access this page by editing the URL, it is handled here.
    if request.method != 'POST':
        return render_template('login.html', errors="Log in via the default page.")

    username = request.form['username']
    password = request.form['password']
    id = 0

    #Encryption setup for logging in.
    key = b'BLhgpCL81fdLBk23HkZp8BgbT913cqt0'
    iv = b'OWFJATh1Zowac2xr'
    cipher = AESCipher(key, iv)

    encrypted_username = cipher.encrypt(username.encode('utf-8')).decode('utf-8')
    encrypted_password = cipher.encrypt(password.encode('utf-8')).decode('utf-8')

    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('''SELECT name, security, id FROM users WHERE name=? AND login=?''', 
                       (encrypted_username, encrypted_password))
        user = cur.fetchone()

    if user:
        session['username'] = username
        session['securityLevel'] = user[1]
        session['id'] = user[2]
        loginSuccess = True
        return redirect(url_for('home'))
    else:
        # Invalid login
        return render_template('login.html', loginSuccess=False)

#Home page now behaves differently based on name and security level.
@app.route('/home')
def home():
    username = session.get('username', 'DEFAULT')
    securityLevel = session.get('securityLevel', 0)
    return render_template('home.html', username=username, securityLevel=securityLevel)

#Add baker.
@app.route('/enternew', methods=['GET'])
def enternew():
    securityLevel = session.get('securityLevel', 0)
    return render_template('enternew.html', securityLevel=securityLevel)

#Shows submission results.
@app.route('/result', methods=['GET', 'POST'])
def result():
    errors = []
    securityLevel = session.get('securityLevel', 0)

    #If the user tries to access this page by editing the URL, it is handled here.
    if request.method != 'POST':
        errors.append("Please enter the necessary information via the 'Add New Baking Contest User' link on the home page.")
        return render_template('result.html', errors=errors, securityLevel=securityLevel)

    name = request.form['name']
    age = request.form['age']
    phoneNum = request.form['pnum']
    security = request.form['slevel']
    login = request.form['login']

    #Encryption setup for processing results.
    key = b'BLhgpCL81fdLBk23HkZp8BgbT913cqt0'
    iv = b'OWFJATh1Zowac2xr'
    cipher = AESCipher(key, iv)

    encrypted_name = cipher.encrypt(name.encode('utf-8')).decode('utf-8')
    encrypted_phoneNum = cipher.encrypt(phoneNum.encode('utf-8')).decode('utf-8')
    encrypted_login = cipher.encrypt(login.encode('utf-8')).decode('utf-8')

    if name.strip() == "":
        errors.append("You can not enter in an empty name.")

    try:
        ageN = int(age)
        if ageN < 1 or ageN >= 121:
            errors.append("The Age must be a whole number greater than 0 and less than 121.")
    except ValueError:
        errors.append("The Age must be a whole number greater than 0 and less than 121.")

    if phoneNum.strip() == "":
        errors.append("You cannot enter an empty phone number.")

    try:
        sec = int(security)
        if sec < 1 or sec > 3:
            errors.append("The Security Level must be a numeric value between 1 and 3.")
    except ValueError:
        errors.append("The Security Level must be a numeric value between 1 and 3.")

    if not login.strip():
        errors.append("You cannot enter an empty password.")

    if errors:
        return render_template('result.html', errors=errors, securityLevel=securityLevel)

    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('''INSERT INTO users (name, age, phoneNum, security, login)
                          VALUES (?, ?, ?, ?, ?)''', 
                          (encrypted_name, age, encrypted_phoneNum, security, encrypted_login))
        conn.commit()

    return render_template('result.html', errors=None, securityLevel=securityLevel)

#Lists all users in the competition.
@app.route('/listusers')
def listusers():
    securityLevel = session.get('securityLevel', 0)
    data = [['Name', 'Age', 'Phone Number', 'Security Level', 'Login Password']]

    #Decryption setup for listing participants.
    key = b'BLhgpCL81fdLBk23HkZp8BgbT913cqt0'
    iv = b'OWFJATh1Zowac2xr'
    cipher = AESCipher(key, iv)

    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        test = cur.execute("SELECT * from 'users'").fetchall()
        for user in test:
            decrypted_name = cipher.decrypt(user[1])
            decrypted_phoneNum = cipher.decrypt(user[3])
            decrypted_login = cipher.decrypt(user[5])
            data.append([decrypted_name, user[2], decrypted_phoneNum, user[4], decrypted_login])

    return render_template('listusers.html', result = data, securityLevel=securityLevel)

#Lists the current competition results.
@app.route('/contestresults')
def contestresults():
    securityLevel = session.get('securityLevel', 0)
    data = [['Entry Id', 'User Id', 'Name of Baking Item', 'Number of Excellent Votes', 'Number of Ok Votes', 'Number of Bad Votes']]

    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        test = cur.execute("SELECT * from 'contestresults'").fetchall()
        data = data + [list(t) for t in test]

    return render_template('contestresults.html', result = data, securityLevel=securityLevel)


#Similar to the contestresults page, except only the current users results are found using their ID. 
@app.route('/mycontestresults')
def mycontestresults():
    securityLevel = session.get('securityLevel', 0)
    data = [['Name of Baking Item', 'Number of Excellent Votes', 'Number of Ok Votes', 'Number of Bad Votes']]
    id = session.get('id', 0)  # Get the user's ID from the session
    print(securityLevel)

    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        # Fetch results for the specific user based on their User Id
        test = cur.execute("SELECT bakingitem, exVoteNum, okVoteNum, bdVoteNum FROM 'contestresults' WHERE userid=?", (id,)).fetchall()
        
        # Append the results to the data
        data += [list(t) for t in test]

    return render_template('mycontestresults.html', result=data, securityLevel=securityLevel)


#Handles competition entry inputs from the user.
@app.route('/newentry', methods=['GET'])
def newentry():
    securityLevel = session.get('securityLevel', 0)
    return render_template('newentry.html', securityLevel=securityLevel)

#Adds the entry results if they are valid, otherwise responds with appropriate error messages.
@app.route('/entryresult', methods=['GET', 'POST'])
def entryResults():
    errors = []
    securityLevel = session.get('securityLevel', 0)
    if request.method != 'POST':
        errors.append("Please enter the necessary information via the 'Add New Baking Contest Entry' link on the home page.")
        return render_template('entryresult.html', errors=errors, securityLevel=securityLevel)

    bakingItem = request.form['bakingitem']
    exVotes = request.form['exvotes']
    okVotes = request.form['okvotes']
    badVotes = request.form['bdvotes']
    id = session.get('id', 0)

    if bakingItem.strip() == "":
        errors.append("You can not enter in an empty name.")

    try:
        exV = int(exVotes)
        if exV < 0:
            errors.append("The number of excellent votes needs to be an integer greater than or equal to 0.")
    except ValueError:
        errors.append("The number of excellent votes needs to be an integer greater than or equal to 0.")

    try:
        okV = int(okVotes)
        if okV < 0:
            errors.append("The number of OK votes needs to be an integer greater than or equal to 0.")
    except ValueError:
        errors.append("The number of OK votes needs to be an integer greater than or equal to 0.")

    try:
        badV = int(badVotes)
        if badV < 0:
            errors.append("The number of bad votes needs to be an integer greater than or equal to 0.")
    except ValueError:
        errors.append("The number of bad votes needs to be an integer greater than or equal to 0.")

    if errors:
        return render_template('entryresult.html', errors=errors, securityLevel=securityLevel)

    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute('''INSERT INTO contestresults (userid, bakingitem, exVoteNum, okVoteNum, bdVoteNum)
                          VALUES (?, ?, ?, ?, ?)''', 
                          (id, bakingItem , exVotes, okVotes, badVotes))
        conn.commit()

    return render_template('entryresult.html', errors=None, securityLevel=securityLevel)

if __name__ == '__main__':
    dbStart()
    app.run(host = host, port = port, debug = True)


