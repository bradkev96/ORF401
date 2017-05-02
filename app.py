import os
import sqlite3
from flask import Flask, render_template, json, request, session, flash, redirect, url_for, g, abort, escape
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
#from app import views

app = Flask(__name__)
app.config.from_object(__name__)

 #Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)
def connect_db():
    #Connects to the specific database.
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    #Initializes the database.
    init_db()

def get_db():
    #Opens a new database connection if there is none yet for the
    #current application context.
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    #Closes the database again at the end of the request.
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

###################################################################################################################

@app.route('/signIn', methods=['POST', 'GET'])
def signIn():
    try:
        if session.get('logged_in'):
            flash('You are already logged in, %s' % escape(session['name']))
            return redirect(url_for('user',idR = session.get('id')))
        else:
            _username = request.form['inputEmail']
            _password = request.form['inputPassword']
            db = get_db()
            cursor = db.execute('SELECT id FROM entries WHERE email=? and password=?', (_username , _password) )
            data = cursor.fetchall()
            for row in data:
                    user = '{0}'.format(row[0])
            cursor = db.execute('SELECT name FROM entries WHERE email=? and password=?', (_username , _password) )
            data = cursor.fetchall()
            for row in data:
                    name = '{0}'.format(row[0])
            if len(data) > 0:
                session['logged_in'] = True
                session['name'] = name
                session['email'] = _username
                session['id'] = user
                flash('You are logged in, %s' % escape(session['name']))
                return redirect(url_for('user',idR = user))
            else:
                flash('Incorrect Email or Password')
                return redirect(url_for('showSignIn'))
    except Exception as e:
        return json.dumps({'error':str(e)})



@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try: 
        if session.get('logged_in'):
            flash('You are already logged in, %s' % escape(session['name']))
            return redirect(url_for('user',idR = session.get('id')))
        else:
            _name = request.form['inputName']
            _email = request.form['inputEmail']
            _password = request.form['inputPassword']

            # validate the received values
            if _name and _email and _password:
                db = get_db()
                db.execute('INSERT into entries (name, email, password) values (?, ?, ?)', (_name, _email, _password))
                db.commit()
                cursor = db.execute('SELECT id FROM entries WHERE email=? and password=?', (_email , _password) )
                data = cursor.fetchall()
                for row in data:
                    user = '{0}'.format(row[0])
                session['logged_in'] = True
                session['name'] = _name
                session['email'] = _email
                session['id'] = user
                flash('New user was successfully created, %s' % escape(session['name']))
                return redirect(url_for('user',idR = user))
            else:
                flash('Enter the required fields to sign up')
                return redirect(url_for('showSignUp'))
    except Exception as e:
        return json.dumps({'error':str(e)})


@app.route('/user/logout')
def userLogout():
    return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('name', None)
    session.pop('email', None)
    session['logged_in'] = False
    return redirect('http://127.0.0.1:5000/showHome')

@login_required
@app.route('/user/<idR>')
def user(idR):
    try:
        if idR != session.get('id') or not session.get('logged_in'):  #not
            return redirect(url_for('showHome'))
        return render_template('user.html', 
            title='User Profile')
    except Exception as e:
        return json.dumps({'error':str(e)})

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html',
        title='Sign Up')

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html',
        title='Sign In')

@app.route('/showHome')
def showHome():
    return render_template('home.html',
        title='Home')
    
@app.route("/")
def main():
    session['logged_in'] = False
    return showHome()

if __name__ == "__main__":
    app.run()

###################################################################################################################





















