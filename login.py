import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'sri@vatsav*40'
mydb = mysql.connector.connect(host="localhost", user="root", passwd="sri@vatsav840", database="sri")
mycursor = mydb.cursor()

def create_table():
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS login_details (userid VARCHAR(20), password VARCHAR(20))")
    except mysql.connector.Error as err:
        return f"Failed to create table: {err}"

def create_table2():
    try:
        mycursor.execute("CREATE TABLE IF NOT EXISTS todo (Task TEXT, Description TEXT, Datetime VARCHAR(20), username VARCHAR(20))")
    except mysql.connector.Error as err:
        return f"Failed to create table: {err}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=["POST", "GET"])
def signin():
    return render_template('signin.html')

@app.route('/signup', methods=["POST", "GET"])
def signup():
    return render_template('signup.html')

@app.route('/signup_submit', methods=["POST", "GET"])
def signup_submit():
    if request.method == "POST":
        user = request.form['username']
        pswd = request.form['password']
        create_table()
        mycursor.execute("select userid from login_details where userid=%s ", ([user]))
        row = mycursor.fetchall()
        if row == []:
            sql = "INSERT INTO login_details (userid, password) VALUES (%s, %s)"
            values = (user, pswd)
            mycursor.execute(sql, values)
            mydb.commit()
            re = "account successfully created you can login now"
            return render_template('signup.html', re=re)
        else:
            ss = "user name already exists use a different username"
            return render_template('signup.html', ss=ss)
    return render_template('signup.html')

@app.route('/gosignin', methods=["POST", "GET"])
def gosignin():
    if request.method == "POST":
        return redirect(url_for('signin'))

@app.route('/gosignup', methods=["POST", "GET"])
def gosignup():
    if request.method == "POST":
        return redirect(url_for('signup'))

@app.route('/signin_submit', methods=["POST", "GET"])
def signin_submit():
    if request.method == "POST":
        user = request.form['username']
        pswd = request.form['password']
        create_table()
        session['username'] = user
        mycursor.execute("select * from login_details where userid=%s and password = %s", (user, pswd))
        row = mycursor.fetchone()
        if row is None:
            re = "username or password did not match please try again!!"
            return render_template('signin.html', re=re)
        else:
            return render_template('crud.html')

@app.route('/crud', methods=["POST", "GET"])
def crud():
    if request.method == "POST":
        button = request.form['submit']
        if button == '+Add Task':
            return render_template('add task.html')
        elif button == 'Update Task':
            oldtask = request.form.get('oldtask', '')
            return render_template('Update Task.html', oldtask=oldtask)
        else:
            return "404 unknown error"

@app.route('/add_task', methods=["POST", "GET"])
def add_task():
    if request.method == "POST":
        task = request.form['task']
        description = request.form['description']
        dat = request.form['datetime']
        date = str(dat)
        username = session.get('username', None)
        create_table2()
        sql = "INSERT INTO todo (Task, Description, Datetime, username) VALUES (%s, %s, %s, %s)"
        values = (task, description, date, username)
        mycursor.execute(sql, values)
        mydb.commit()
        re = "Task added"
        query = "SELECT Task, Description, Datetime FROM todo WHERE username=%s"
        mycursor.execute(query, (username,))
        tasks = mycursor.fetchall()
        return render_template('add task.html', re=re, tasks=tasks)
    return render_template('add task.html')

@app.route('/Home', methods=["POST", "GET"])
def Home():
    return render_template('crud.html')

@app.route('/showtasks', methods=["POST", "GET"])
def show_tasks():
    try:
        username = session.get('username', None)
        if username:
            search_query = request.args.get('search', '').lower()
            if search_query:
                query = "SELECT Task, Description, Datetime FROM todo WHERE username=%s AND LOWER(Task) LIKE %s"
                mycursor.execute(query, (username, f"%{search_query}%"))
            else:
                query = "SELECT Task, Description, Datetime FROM todo WHERE username=%s"
                mycursor.execute(query, (username,))
            tasks = mycursor.fetchall()
            return render_template('show tasks.html', tasks=tasks)
        else:
            return render_template('show tasks.html', ss="No username in session.")
    except Exception as e:
        return render_template('show tasks.html', ss="Error while fetching: " + str(e))

@app.route('/remove_task', methods=["POST", "GET"])
def remove_task():
    if request.method == "POST":
        task = request.form['task']
        username = session.get('username', None)
        mycursor.execute("select * from todo where Task=%s and username =%s", (task, username))
        tasks = mycursor.fetchall()
        if tasks:
            r = "DELETE FROM todo WHERE Task =%s and username =%s"
            values = (task, username)
            mycursor.execute(r, values)
            mydb.commit()
            query = "SELECT Task, Description, Datetime FROM todo WHERE username=%s"
            mycursor.execute(query, (username,))
            tasks = mycursor.fetchall()
            return render_template('show tasks.html', tasks=tasks)
        else:
            ss = "Something went wrong, please try again."
            return render_template('show tasks.html', ss=ss)
    return render_template('show tasks.html', ss="An error occurred, please try again.")

@app.route('/update_task', methods=["POST", "GET"])
def update_task():
    if request.method == "POST":
        oldtask = request.form['oldtask']
        newtask = request.form['newtask']
        description = request.form['description']
        dat = request.form['datetime']
        date = str(dat)
        username = session.get('username', None)
        mycursor.execute("UPDATE todo SET Task=%s, Description=%s, Datetime=%s WHERE Task=%s AND username=%s", (newtask, description, date, oldtask, username))
        mydb.commit()
        return redirect(url_for('show_tasks'))
    else:
        oldtask = request.args.get('oldtask', '')
        return render_template('update_task.html', oldtask=oldtask)

if __name__ == '__main__':
    app.run(debug=True)
