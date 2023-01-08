from flask import Flask,flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import app
from flask import jsonify
from wxconv import WXC
import MySQLdb.cursors
import re
from config import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import json
import pprint
import os

# cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
# cursor.execute("CREATE TABLE IF NOT EXISTS discourse (discourse_id int NOT NULL AUTO_INCREMENT, author_id int, no_sentences int, domain varchar(255), create_date datetime default now(), other_attributes VARCHAR(255), sentences VARCHAR(255),PRIMARY KEY (discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id)")
# mysql.connection.commit()

@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("CREATE TABLE IF NOT EXISTS author (author_id int AUTO_INCREMENT , author_name varchar(255), email varchar(255), password varchar(16), reviewer_role varchar(255), PRIMARY KEY(author_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS discourse (discourse_id int NOT NULL AUTO_INCREMENT, discourse_name varchar(255),author_id int, no_sentences int, domain varchar(255), create_date datetime default now(), other_attributes VARCHAR(255), sentences MEDIUMTEXT,PRIMARY KEY (discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS usr (author_id int,  discourse_id int, sentence_id varchar(255) ,USR_ID int NOT NULL AUTO_INCREMENT, orignal_USR_json MEDIUMTEXT,final_USR json,create_date datetime default now(),USR_status varchar(255),FOREIGN KEY (discourse_id) REFERENCES discourse(discourse_id),FOREIGN KEY (author_id) REFERENCES author(author_id), PRIMARY KEY (USR_ID))")
    cursor.execute("CREATE TABLE IF NOT EXISTS demlo(demlo_id int AUTO_INCREMENT, demlo_txt JSON, PRIMARY KEY (demlo_id))")
    mysql.connection.commit()
    return render_template('index.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        # password = generate_password_hash(password)
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
            return render_template('index.html')
        else:
            flash('Incorrect loginId / password !')
    return render_template('login.html')
 
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
            flash('author already exists !')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address !')
        # elif not re.match(r'[A-Za-z]+', author_name):
        #     msg = 'author_name must contain only characters !'
        elif not author_name or not password or not email:
            flash('Please fill out the form !')
        else:
            # hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO author VALUES (NULL, % s, % s, % s, % s)', (author_name, email, password, reviewer_role ))
            mysql.connection.commit()
            flash('You have successfully registered !')
            return render_template('login.html')
    elif request.method == 'POST':
        flash('Please fill out the form !')
    return render_template('signup.html')

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
            # _hashed_password = generate_password_hash(_password)
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

def usr_conversion(usr_file):
    dict1 = {}
    file = open(usr_file)
    line1 = file.readline()
    line2 = (file.readline()).strip().split(',')
    dict1["Concept"] = line2
    line3 = [int(x) for x in file.readline().split(",")]
    dict1["Index"] = line3
    line4 = (file.readline()).strip().split(',')
    dict1["Sem. Cat"] = line4
    line5 = (file.readline()).strip().split(',')
    dict1["G-N-P"] = line5
    line6 = (file.readline()).strip().split(',')
    dict1["Dep-Rel"] = line6
    line7 = (file.readline()).strip().split(',')
    dict1["Discourse"] = line7
    line8 = (file.readline()).strip().split(',')
    dict1["Speaker's View"] = line8
    line9 = (file.readline()).strip().split(',')
    dict1["Scope"] = line9
    line10 = file.readline().strip().split(',')
    dict1["Sentence Type"] = line10
    return dict1

def getUSR():
    os.getcwd()
    data_folder = os.path.join(os.getcwd(), 'Bulk_USRs')
    data=[]
    for root, folders, files in os.walk(data_folder):
        for file in files:
            path = os.path.join(root, file)
            data.append(usr_conversion(path))
    return data

l1 = json.dumps(getUSR()[0])
m = l1.encode()
print(m)
l2 = json.loads(l1)
print(type(getUSR()[0]))




@app.route('/discourse/create', methods = ['POST'])
def create_discourse():
    try:
        _json = request.json
        _author_id = _json['author_id']
        _no_sentences = _json['no_sentences']
        _domain = _json['domain']
        _other_attributes = _json['other_attributes']
        _sentences = _json['sentences']
        _discourse_name = _json['discourse_name']
        if _author_id and _no_sentences and _domain and _other_attributes and _sentences and _discourse_name and request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            hin2wx = WXC(order='utf2wx', lang="hin").convert
            _sentences = hin2wx(_sentences)
            # text_file = open("sentences_for_USR", "w")
            sc = 12345
            sent_list = _sentences.split(".")
            sent_list= sent_list[:-1]
            tmp_list = []
            with open ('sentences_for_USR', 'w') as file:  
                for x in sent_list:
                    st = str(sc) + "   " +  x.lstrip(" ")
                    file.write(st)
                    file.write('\n')
                    sc += 1
            sqlQuery = "INSERT INTO discourse(author_id, discourse_name, no_sentences, domain, other_attributes, sentences) VALUES(%s, %s, %s, %s, %s, %s)"
            bindData = (_author_id, _discourse_name,_no_sentences,_domain, _other_attributes, _sentences)
            cursor.execute(sqlQuery, bindData)
            mysql.connection.commit()
            row_id = cursor.lastrowid
            c=1
            for x in getUSR():
                rd = str(row_id)+'.'+str(c)
                cursor.execute("INSERT INTO usr(author_id,discourse_id,sentence_id,orignal_USR_json) VALUES(%s,%s,%s,%s)", [_author_id,row_id, rd, getUSR()[c-1]])
                c += 1
            mysql.connection.commit()
            respone = jsonify('discourse added successfully!')
            respone.status_code = 200
            return respone
    except Exception as e:
        print(e)
    
@app.route('/usr/<discourse_name>')
def usrin_details(discourse_name):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT discourse_id FROM discourse WHERE discourse_name = %s", [discourse_name])
        dis_row = cursor.fetchone()
        d_id = dis_row.get("discourse_id")
        cursor.execute("SELECT author_id, discourse_id, sentence_id, orignal_USR_json FROM usr  WHERE discourse_id  =%s", [d_id])
        authRow = cursor.fetchall()
        respone = jsonify(authRow)
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
        _final_USR = _json['final_USR']
        _USR_status = _json['USR_status']
        if _author_id and _discourse_id and _sentence_id and _final_USR and _USR_status and request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sqlQuery = "INSERT INTO usr(author_id, discourse_id, sentence_id, final_USR, USR_status) VALUES(%s, %s, %s, %s, %s)"
            bindData = (_author_id, _discourse_id, _sentence_id, _final_USR, _USR_status)           
            cursor.execute(sqlQuery, bindData)
            mysql.connection.commit()
            respone = jsonify('USR added successfully!')
            respone.status_code = 200
            mysql.connection.commit()
            return respone
    except Exception as e:
        print(e) 
    
@app.route('/USR')
def USR():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)	
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM usr")
        usrRows = cursor.fetchall()
        respone = jsonify(usrRows)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)

@app.route('/USR/<USR_ID>')
def usr_details(USR_ID):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT author_id, discourse_id, sentence_id, USR_ID, orignal_USR_json, final_USR, create_date, USR_status FROM usr WHERE USR_ID =%s", [USR_ID])
        usrRow = cursor.fetchone()
        respone = jsonify(usrRow)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)