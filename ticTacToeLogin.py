import wsgiref.simple_server
import urllib.parse
import sqlite3
import http.cookies

#checks to see if database is created and table created
connection = sqlite3.connect('users.db')
stmt = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
cursor = connection.cursor()
result = cursor.execute(stmt)
r = result.fetchall()
if (r == []):
    exp = 'CREATE TABLE users (username,password,playing,partner)'
    connection.execute(exp)

def application(environ, start_response):
    headers = [('Content-Type', 'text/html; charset=utf-8')]

    path = environ['PATH_INFO']
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])
    un = params['username'][0] if 'username' in params else None
    pw = params['password'][0] if 'password' in params else None
    pl = False
    pr = ''
#.
    if path == '/register' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ?', [un]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['Sorry, username {} is taken'.format(un).encode()]
        else: #Start code student should have entered
            connection.execute('INSERT INTO users VALUES (?, ?, ?, ?)', [un, pw, pl, pr])
            connection.commit()
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['Congratulations, username {} been successfully registered. <a href="/account">Account</a>'.format(un).encode()]
       #End code student should have entered

    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['User {} successfully logged in. <a href="/account">Account</a>'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password'.encode()]

    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        return ['Logged out. <a href="/">Login</a>'.encode()]

    elif path == '/account':
        start_response('200 OK', headers)

        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:

            return ['Logged in: {}. <a href="/play">Play</a> <a href="/logout">Logout</a>'.format(un).encode()]
        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]

    elif path == '/play':
        pl=True
        cursor.execute('''UPDATE users SET playing = ? WHERE username = ? ''',(pl, un)) #update user from not playing to playing
        ok= cursor.execute('SELECT * FROM users WHERE pl = ? and pr = ?', [True, '']).fetchall() #check if anyone else needs partner
        if(ok):
            pr= cursor.execute('''SELECT username FROM users WHERE pl = ? and pr = ?''', (True, '',))
            cursor.execute('''UPDATE users SET partner = ? WHERE username = ? ''', (pr, un))#set pr to other persons username
        else:
            pass #change later to start game where they make first move before getting partner
        return ['playing {} partner {}'.format(pl,pr).encode()]
    ###############################send user to game here####################################
    elif path == '/':
        login_form = '''
<form action="/login" style="background-color:lightblue">
    <h1>Login</h1>
    Username <input type="text" name="username"><br>
    Password <input type="password" name="password"><br>
    <input type="submit" value="Log in">
    <input type="submit" value="Register" formaction="/register">
</form>
'''
        start_response('200 OK', headers)
        return[login_form.encode()]


    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]

httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()
