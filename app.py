from flask import Flask, render_template, url_for
from flask import flash, redirect, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from data import Articles

app = Flask(__name__)

Articles = Articles()


@app.route('/')
def index():
  return render_template('home.html')
    
    
@app.route('/about')
def about():
  return render_template('about.html')

    
@app.route('/articles/')
def articles():
  return render_template('articles.html', articles=Articles)

@app.route('/articles/article/<string:id>/')
def article(id):
  return render_template('article.html', id=id)

if __name__ == '__main__':
  app.run(debug=True)