from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import re
import os.path
import sqlite3

DATABASE = 'C:\\Users\\Ronan\\Documents\\SailingRace\\database.db'

app = Flask(__name__)
app.config.from_object(__name__)

#Connects to the sqlite database
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
    
#Database functions
@app.before_request
def before_request():
	g.db=connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g,'db',None)
	if db is not None:
		db.close()


#Front End Routes
@app.route('/')
def entry_point():
    return render_template('index.html', message = '')
    
@app.route('/register')
def register():
    return render_template('register.html')
    
@app.route('/register/success')
def register_success():
    return render_template('index.html', message='Account created with success ! You can now sign in !')
    
@app.route('/main')
def main_page():
    if session.has_key('id') == False:
        return render_template('index.html', message = 'You have been disconnected...')
    print 'id of current user is : ', session['id']
    
    #Let's get races user is taking part incur = g.db.execute('SELECT id, name, description FROM races')
    cur = g.db.execute('SELECT id, name, description FROM races WHERE id IN (SELECT race_id FROM userraces WHERE user_id = ?)', [session['id']])
    userraces = [dict(id=row[0], name=row[1], description=row[2]) for row in cur.fetchall()]
    
    #Let's fetch all races info
    cur = g.db.execute('SELECT id, name, description FROM races')
    allraces = [dict(id=row[0], name=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('chooserace.html', allraces = allraces, userraces = userraces) 
    
@app.route('/race/play/<int:race_id>')
def race_play(race_id):
    cur = g.db.execute('SELECT id, name, description FROM races WHERE id = ?', [race_id])
    currentrace = [dict(id=row[0], name=row[1], description=row[2]) for row in cur.fetchall()]
    currentrace = currentrace[0]
    
    cur = g.db.execute('SELECT boat_id, course FROM userraces WHERE user_id = ? AND race_id = ?', [session['id'], race_id])
    boatinfo = [dict(boat_id=row[0], course=row[1]) for row in cur.fetchall()]
    boatinfo = boatinfo[0]
    
    return render_template('play.html', currentrace = currentrace, boatinfo = boatinfo)
    
@app.route('/race/register/<int:race_id>')
def race_register(race_id):
    cur = g.db.execute('SELECT id, name FROM boats')
    boats = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]
    
    return render_template('raceregister.html', race_id = race_id, boats=boats)
    
    
    
    
#API Routes
@app.route('/api/register', methods=['POST'])
def api_register():
    print 'keys received : '
    print request.form.viewkeys
       
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return 'Email address invalid !'
    #Let's check that no one is alreday using these names/emails
    cur = g.db.execute('SELECT id FROM users WHERE name = ?', [name])
    entries = [dict(id=row[0]) for row in cur.fetchall()]
    if(len(entries) > 0):
        return 'Name already taken, please choose another one...'
        
    cur = g.db.execute('SELECT id FROM users WHERE email = ?', [email])
    entries = [dict(id=row[0]) for row in cur.fetchall()]
    if(len(entries) > 0):
        return 'Email already taken, please choose another one...'
        
    #Save user if everything is ok
    g.db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', [name, email, password])
    g.db.commit()
    
    return 'ok'
    
@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.form['email']
    password = request.form['password']
    
    cur = g.db.execute('SELECT id FROM users WHERE email = ? AND password = ?', [email, password])
    entries = [dict(id=row[0]) for row in cur.fetchall()]
    if(len(entries) != 1):
        return 'Unknown combination of user and password, please retry...'
        
    id = entries[0]['id']  
    print 'User is connected with id : ', id
    session['id'] = id
        
    return 'ok'
    
@app.route('/api/race/register', methods=['POST'])
def api_race_register():
    boat_id = request.form['boatid']
    race_id = request.form['raceid']
    
    #penser a verifier que l'utilisateur n'est pas deja enregistre pour cette course
    g.db.execute('INSERT INTO userraces (user_id, race_id, boat_id) VALUES (?, ?, ?)', [session['id'], race_id, boat_id])
    g.db.commit()
  
    return 'ok'
    
@app.route('/api/race/<int:race_id>/updateboat', methods=['POST'])
def api_race_updateboat(race_id):
    course = request.form['course']
    g.db.execute('UPDATE userraces SET course = ? WHERE race_id = ? AND user_id = ?', [course, race_id, session['id']])
    g.db.commit()
  
    return 'ok'
        
if __name__ == '__main__':
    app.secret_key = 'ssssshhhhh'
    app.run(debug=True)