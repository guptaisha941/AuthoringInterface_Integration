from flask import Flask,flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import app
from flask import jsonify
from wxconv import WXC
import MySQLdb.cursors
import re
from config import mysql
import json

# cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
# cursor.execute("CREATE TABLE IF NOT EXISTS discourse (discourse_id int NOT NULL AUTO_INCREMENT, author_id int, no_sentences int, domain varchar(255), create_date datetime default now(), other_attributes VARCHAR(255), sentences VARCHAR(255),PRIMARY KEY (discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id)")
# mysql.connection.commit()

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("CREATE TABLE IF NOT EXISTS author (author_id int AUTO_INCREMENT , author_name varchar(255), email varchar(255), password varchar(16), reviewer_role varchar(255), PRIMARY KEY(author_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS discourse (discourse_id int NOT NULL AUTO_INCREMENT, author_id int, no_sentences int, domain varchar(255), create_date datetime default now(), other_attributes VARCHAR(255), sentences VARCHAR(255),PRIMARY KEY (discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS usr (author_id int,  discourse_id int, sentence_id int ,USR_ID int NOT NULL AUTO_INCREMENT, orignal_USR_json JSON,final_USR json,create_date datetime default now(),USR_status varchar(255),FOREIGN KEY (sentence_id) REFERENCES discourse (discourse_id) ,FOREIGN KEY (discourse_id) REFERENCES discourse(discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id), PRIMARY KEY (USR_ID))")
    mysql.connection.commit()
    return render_template('index.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('CREATE TABLE IF NOT EXISTS author (author_id int AUTO_INCREMENT , author_name varchar(255), email varchar(255), password varchar(16), reviewer_role varchar(255), PRIMARY KEY(author_id)) ')
        cursor.execute('SELECT * FROM author WHERE email = % s AND password = % s', (email, password, ))
        author = cursor.fetchone()
        if author:
            session['loggedin'] = True
            session['author_id'] = author['author_id']
            session['email'] = author['email']
            msg = 'Logged in successfully !'
            flash('Logged in successfully')
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect loginId / password !'
    return render_template('login.html', msg = msg)
 
# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('author_id', None)
#     session.pop('email', None)
#     return redirect(url_for('login'))
 
@app.route('/signup', methods =['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'author_name' in request.form and 'email' in request.form and 'password' in request.form and 'reviewer_role' in request.form :
        author_name = request.form['author_name']
        email = request.form['email']
        password = request.form['password']
        reviewer_role = request.form['reviewer_role']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM author WHERE author_name = % s', (author_name, ))
        author = cursor.fetchone()
        if author:
            msg = 'author already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        # elif not re.match(r'[A-Za-z]+', author_name):
        #     msg = 'author_name must contain only characters !'
        elif not author_name or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO author VALUES (NULL, % s, % s, % s, % s)', (author_name, email, password, reviewer_role ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('signup.html', msg = msg)

@app.route('/authors')
def author():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT author_id, author_name, email, password, reviewer_role FROM author")
        authRows = cursor.fetchall()
        respone = jsonify(authRows)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)

@app.route('/author/<author_id>')
def auth_details(author_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT author_id , author_name, email, password, reviewer_role FROM author WHERE author_id =%s", author_id)
        authRow = cursor.fetchone()
        respone = jsonify(authRow)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)

@app.route('/author/update', methods=['PUT'])
def update_author():
    try:
        _json = request.json
        _author_id = _json['author_id']
        _author_name = _json['author_name']
        _email = _json['email']
        _password = _json['password']
        _reviewer_role = _json['reviewer_role']
        if _author_name and _email and _password and _reviewer_role and request.method == 'PUT':
            sql = "UPDATE author SET author_name=%s, email=%s, password=%s, reviewer_role=%s WHERE author_id=%s"
            data = (_author_name, _email, _password, _reviewer_role, _author_id)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql, data)
            mysql.connection.commit()
            resp = jsonify('author updated successfully!')
            resp.status_code = 200
            return resp
    except Exception as e:
        print(e)

@app.route('/author/delete/<author_id>', methods=['DELETE'])
def delete_author(author_id):
	conn = None
	cursor = None
	try:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("DELETE FROM author WHERE author_id=%s", (author_id,))
		mysql.connection.commit()
		resp = jsonify('author deleted successfully!')
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)

@app.route('/discourse/create', methods = ['POST'])
def create_discourse():
    try:
        _json = request.json
        _author_id = _json['author_id']
        _no_sentences = _json['no_sentences']
        _domain = _json['domain']
        _other_attributes = _json['other_attributes']
        _sentences = _json['sentences']
        if _author_id and _no_sentences and _domain and _other_attributes and _sentences and request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            hin2wx = WXC(order='utf2wx', lang="hin").convert
            _sentences = hin2wx(_sentences)
            sqlQuery = "INSERT INTO discourse(author_id, no_sentences, domain, other_attributes, sentences) VALUES(%s, %s, %s, %s, %s)"
            bindData = (_author_id, _no_sentences,_domain, _other_attributes, _sentences)
            cursor.execute(sqlQuery, bindData)
            mysql.connection.commit()
            respone = jsonify('discourse added successfully!')
            respone.status_code = 200
            return respone
    except Exception as e:
        print(e)

@app.route('/discourse')
def discourse():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT discourse_id, author_id, no_sentences, domain,create_date, other_attributes, sentences FROM discourse")
        disRows = cursor.fetchall()
        respone = jsonify(disRows)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)

@app.route('/discourse/<discourse_id>')
def dis_details(discourse_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT discourse_id , author_id, no_sentences, domain, create_date,other_attributes, sentences FROM discourse WHERE discourse_id =%s", discourse_id)
        disRow = cursor.fetchone()
        respone = jsonify(disRow)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e) 

@app.route('/discourse/update', methods=['PUT'])
def update_discourse():
    conn = None
    cursor = None
    try:
        _json = request.json
        _discourse_id = _json['discourse_id']
        _author_id = _json['author_id']
        _no_sentences = _json['no_sentences']
        _domain = _json['domain']
        _sentences = _json['sentences']
        _other_attributes = _json['other_attributes']
        if _author_id and _no_sentences and _domain and _other_attributes and _sentences and request.method == 'PUT':
            hin2wx = WXC(order='utf2wx', lang="hin").convert
            _sentences = hin2wx(_sentences)
            sql = "UPDATE discourse SET author_id=%s, no_sentences=%s, domain=%s, other_attributes=%s, sentences=%s WHERE discourse_id=%s"
            data = (_author_id, _no_sentences, _domain, _other_attributes, _discourse_id, _sentences)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql, data)
            mysql.connection.commit()
            resp = jsonify('discourse updated successfully!')
            resp.status_code = 200
            return resp
    except Exception as e:
        print(e)

@app.route('/discourse/delete/<discourse_id>', methods=['DELETE'])
def delete_discourse(discourse_id):
	conn = None
	cursor = None
	try:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("DELETE FROM discourse WHERE discourse_id=%s", (discourse_id,))
		mysql.connection.commit()
		resp = jsonify('discourse deleted successfully!')
		resp.status_code = 200
		return resp
	except Exception as e:
		print(e)

@app.route('/USR/create', methods = ['POST'])
def create_USR():
    try:
        _json = request.json
        _author_id = _json['author_id']
        _discourse_id = _json['discourse_id']
        _sentence_id = _json['sentence_id']
        _orignal_USR_json = _json['orignal_USR_json']
        _final_USR = _json['final_USR']
        _USR_status = _json['USR_status']
        if _author_id and _discourse_id and _sentence_id and _orignal_USR_json and _final_USR and _USR_status and request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)	
            _orignal_USR_json = json.dumps(_orignal_USR_json)
            sqlQuery = "INSERT INTO usr(author_id, discourse_id, sentence_id, orignal_USR_json, final_USR, USR_status) VALUES(%s, %s, %s, %s, %s, %s)"
            bindData = (_author_id, _discourse_id, _sentence_id, _orignal_USR_json, _final_USR, _USR_status)            
            cursor.execute(sqlQuery, bindData)
            mysql.connection.commit()
            print(type(_orignal_USR_json))
            respone = jsonify('USR added successfully!')
            respone.status_code = 200
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            _orignal_USR_json = json.loads(_orignal_USR_json)
            print(type(_orignal_USR_json))
            cursor.execute("UPDATE usr SET orignal_USR_json=%s",_orignal_USR_json) 
            mysql.connection.commit()
            return respone
    except Exception as e:
        print(e) 
    
@app.route('/USR')
def USR():
    try:
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)	
        # cursor.execute("SELECT orignal_USR_json from usr")
        # usr_json = cursor.fetchall()
        # orignal_USR_json = json.loads(usr_json)
        # cursor.execute("SELECT author_id, discourse_id, sentence_id, USR_ID, orignal_USR_json, final_USR, create_date, USR_status FROM usr WHERE orignal_USR_json = %s", orignal_USR_json)
        # mysql.connection.commit()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT author_id, discourse_id, sentence_id, USR_ID, orignal_USR_json, final_USR, create_date, USR_status FROM usr")
        usrRows = cursor.fetchall()
        # usrRows = json.loads(usrRows)
        respone = jsonify(usrRows)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)

@app.route('/USR/<USR_ID>')
def usr_details(USR_ID):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT author_id, discourse_id, sentence_id, USR_ID, orignal_USR_json, final_USR, create_date, USR_status FROM usr WHERE USR_ID =%s", USR_ID)
        usrRow = cursor.fetchone()
        respone = jsonify(usrRow)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)