from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from config import app
import MySQLdb.cursors
import re
from config import mysql
 
# cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
# cursor.execute('CREATE TABLE IF NOT EXISTS author (author_id int AUTO_INCREMENT , author_name varchar(255), email varchar(255), password varchar(16), reviewer_role varchar(255), PRIMARY KEY(author_id)) ')

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('CREATE TABLE IF NOT EXISTS author (author_id int AUTO_INCREMENT , author_name varchar(255), email varchar(255), password varchar(16), reviewer_role varchar(255), PRIMARY KEY(author_id)) ')
        cursor.execute('SELECT * FROM accounts WHERE email = % s AND password = % s', (email, password, ))
        author = cursor.fetchone()
        if author:
            session['loggedin'] = True
            session['author_id'] = author['author_id']
            session['email'] = author['email']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect loginId / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('author_id', None)
    session.pop('email', None)
    return redirect(url_for('login'))
 
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