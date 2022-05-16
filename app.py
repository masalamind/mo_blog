from flask import Flask, render_template, url_for, request
from flask import flash, redirect, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
# from data import Articles
from functools import wraps

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mobyte73'
app.config['MYSQL_DB'] = 'moblog'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#init mysql 

mysql = MySQL(app)

# Articles = Articles()

@app.route('/')
def index():
  return render_template('home.html')
    
    
@app.route('/about')
def about():
  return render_template('about.html')

    
@app.route('/articles/')
def articles():
      # create cursor
    cur = mysql.connection.cursor()

    # get article
    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()

    if result > 0:
      return render_template('articles.html', articles=articles)
    else:
      msg = "No Articles Found"
      return render_template('articles.html', msg=msg)
    cur.close()

    return render_template('articles.html', articles=Articles)

# Single article
@app.route('/articles/article/<string:id>/')
def article(id):

  cur = mysql.connection.cursor()
  result = cur.execute("SELECT * FROM articles WHERE id= %s", [id])
  article = cur.fetchone()

  return render_template('article.html', article=article)


class RegisterForm(Form):
  name = StringField('Name', [validators.Length(min=1, max=50)])
  username = StringField('Username', [validators.length(min=4, max=25)])
  email = StringField('Email', [validators.Length(min=6, max=50)])
  password = PasswordField('Password', [
    validators.DataRequired(),
    validators.EqualTo('confirm', message='Passwords do not match')
  ])
  
  confirm = PasswordField('Confirm Password')
  
@app.route('/register', methods=['GET','POST']) 
def register():
  form = RegisterForm(request.form)
  
  if request.method == 'POST' and form.validate():
    name = form.name.data
    email = form.email.data
    username = form.username.data
    password = sha256_crypt.encrypt(str(form.password.data))
    
    cur = mysql.connection.cursor()
    
    cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s,%s,%s,%s)", (name,email,username,password))
    
    mysql.connection.commit()
    
    cur.close()
    
    flash("You are now registered and can log in", "success")
    
    return redirect(url_for('login'))
    
  return render_template('register.html', form=form) 
  

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # not using wtforms to retrieve field values
    username = request.form['username']
    password_candidate = request.form['password']

    cur = mysql.connection.cursor()
    # Get user by username

    result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

    if result > 0:
      # Get stored hash
      data = cur.fetchone()
      password = data['password']

      # compare passwords
      if sha256_crypt.verify(password_candidate, password):
        # app.logger.info('PASSWORD MATCHED')
        session['logged_in'] = True
        session['username'] = username

        flash('You are now logged in', 'success')
        return redirect(url_for('dashboard'))
      else:
        error = "Invalid login"
        app.logger.info('PASSWORD NOT MATCHED', error=error)
      cur.close() # close the connection

    else:
      error = "Username not found"
      return render_template('login.html', error=error)

  return render_template('login.html')


def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      flash('Unauthorized, Please login', 'danger')
      return redirect(url_for('login'))
  return wrap

@app.route('/dashboard')
@is_logged_in
def dashboard():

    # create cursor
    cur = mysql.connection.cursor()

    # get article
    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()

    if result > 0:
      return render_template('dashboard.html', articles=articles)
    else:
      msg = "No Articles Found"
      return render_template('dashboard.html', msg=msg)
    cur.close()

# Use wtforms for blog articles
class ArticleForm(Form):
  title = StringField('Title', [validators.Length(min=1, max=200)])
  body = TextAreaField('Body', [validators.length(min=30)])


@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
  form = ArticleForm(request.form)
  if request.method == 'POST' and form.validate():
    title = form.title.data
    body = form.body.data

    # create cursor
    cur = mysql.connection.cursor()
    # execute
    cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

    # commit to db
    mysql.connection.commit()

    # close connection
    cur.close()

    flash('Article Created', 'success')
    return redirect(url_for('dashboard'))
  return render_template('add_article.html', form=form)


# Check if user logged in


@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  flash("You are now logged out", 'success')
  return redirect(url_for('login'))



if __name__ == '__main__':
  app.secret_key ='secret123'
  app.run(debug=True)