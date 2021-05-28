from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import bcrypt
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'r2-NxD9NRpy6Qv2vRqgY0Q'
app.config['UPLOAD_FOLDER'] = 'static/img/uploads'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crud_python'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        flash('Register succesfully!')
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        connect = mysql.connection.cursor()
        connect.execute("INSERT INTO users (fullname, email, password) VALUES(%s, %s, %s)", (fullname, email, password_hash))
        mysql.connection.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('FULLNAME', None) is not None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        connect = mysql.connection.cursor()
        connect.execute("SELECT fullname, email, password FROM users WHERE email = %s",[email])
        data = connect.fetchall()
        connect.close()
        if data:
            if bcrypt.checkpw(password.encode('utf-8'), data[0][2].encode('utf-8')):
                for d in data:
                    session['FULLNAME'] = d[0]
                    session['EMAIL'] = d[1]
                    return redirect(url_for('home'))
            else:
                flash('Wrong Password!')
        else:
            flash('Data not found')
            
    return render_template('login.html')

@app.route('/home')
def home():
    if session.get('FULLNAME', None) is not None:
        user = {
            "fullname": session.get('FULLNAME'),
            "email": session.get("EMAIL")
        }
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/employed')
def employed():
    return render_template('karyawan.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/employed/add', methods=['GET', 'POST'])
def add_employed():
    if request.method == 'POST':
        file = request.files['thumbnail']
        if not file:
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('That extension not allowed')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('employed'))
    return render_template('add_karyawan.html')
