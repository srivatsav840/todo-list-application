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
        mycursor.execute("CREATE TABLE IF NOT EXISTS todo (Task TEXT, Datetime VARCHAR(20), username varchar(20))")

    except mysql.connector.Error as err:
        return f"Failed to create table{err}"


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
        elif button == 'Remove Task':
            return render_template('delete task.html')
        elif button == 'Update Task':
            return render_template('Update Task.html')
        else:
            return "404 unkown error"


@app.route('/add task', methods=["POST", "GET"])
def add_task():
    if request.method == "POST":
        task = request.form['task']
        dat = request.form['datetime']
        date = str(dat)
        username = session.get('username', None)
        create_table2()
        sql = "INSERT INTO todo (Task, Datetime,username) VALUES (%s, %s, %s)"
        values = (task, date, username)
        mycursor.execute(sql, values)
        mydb.commit()
        re = "Task added"
        return render_template('add task.html', re=re)
    return render_template('add task.html')


@app.route('/Home', methods=["POST", "GET"])
def Home():
    return render_template('crud.html')


@app.route('/showtasks', methods=["POST", "GET"])
def show_tasks():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="sri@vatsav840",
            database="sri"
        )
        mycursor = mydb.cursor()
        username = session.get('username', None)

        if username:
            query = "SELECT Task, Datetime, username FROM todo WHERE username=%s"
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
            r = "delete from todo where Task =%s and username =%s"
            values = (task, username)
            mycursor.execute(r, values)
            mydb.commit()
            return render_template('delete task.html', re="removed successfully")
        else:
            return render_template('delete task.html', re="Task not found")
    return render_template('delete task.html', re="something error occured please try again")


@app.route('/update_task', methods=["POST", "GET"])
def update_task():
    if request.method == "POST":
        oldtask = request.form['oldtask']
        newtask = request.form['newtask']
        dat = request.form['datetime']
        date = str(dat)
        username = session.get('username', None)
        mycursor.execute("select * from todo where Task=%s and username =%s", (oldtask, username))
        exist = mycursor.fetchall()
        if exist:
            mycursor.execute("UPDATE todo SET Task = %s, Datetime = %s WHERE task = %s AND username = %s",
                             (newtask, date, oldtask, username))
            mydb.commit()
            return render_template('update task.html', re="task updated successfully")
        return render_template('update task.html', re="task not found")


if __name__ == '__main__':
    app.run(debug=True)
