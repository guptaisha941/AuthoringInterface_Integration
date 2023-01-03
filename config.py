from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL


app = Flask(__name__)

app.secret_key = 'asdfghjkl'
 
# app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mysql@1234'
app.config['MYSQL_DB'] = 'testdb'
 
mysql = MySQL(app)