import base64
from functools import wraps
import os
import sqlite3
from flask import Flask, request, g, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'data.db'),
))
db = SQLAlchemy(app)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


#########################################
# The lines below have vulnerabilities. #
#########################################


_HEADER_MENU_HTML = """
<a href='/profile'>My profile</a>&nbsp;|&nbsp;
<a href='/create'>Create post</a>&nbsp;|&nbsp;
<a href='/browse'>Browse posts</a>&nbsp;|&nbsp;
<a href='/logout'>Logout</a>
<hr>
"""


# Check if the user is authenticated.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db = get_db()
        cur = db.execute(
            'select * from users where username = (?)',
            [request.cookies.get('username')]
        )
        user_db_entry = cur.fetchone()
        if not user_db_entry:
            return redirect('/', code=302)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET'])
def index():
    return """
    Welcome to FooBook!<br><br>With your account you can:
    <ul>
      <li>See posts by everyone</li>
      <li>Make up to 3 posts per day</li>
    </ul>
    Please log-in:
    <form method="post" action="/login">
        <input type="text" name="username" placeholder="username"/><br>
        <input type="password" name="password" placeholder="password"/><br>
        <input type="submit"/>
    </form>
    """


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # This returns the user's row from the DB if the credentials are correct.
    db = get_db()
    cur = db.execute('select * from users where username = "' + username + '" and password = "' + password + '"')
    user_rows = cur.fetchall()

    if not user_rows:  # There are no users with this user/pass combination.
        response = app.make_response(redirect('/error', code=302))
        response.set_cookie('username', value='')
    else:  # Log-in successful.
        username = user_rows[0][0]
        response = app.make_response(redirect('/profile', code=302))
        response.set_cookie('username', value=username)
    return response


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return """
    %s
    Welcome to your profile <b><u>%s</u></b>!<br>
    """ % (_HEADER_MENU_HTML, request.cookies['username'])


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':

        db = get_db()
        cur = db.execute(
            'select count(*) from posts \
            where username = (?) \
            and created_at = date("now")',
            [request.cookies.get('username')]
        )
        number_of_posts_made_today = cur.fetchone()[0]

        if number_of_posts_made_today < 3:
            return """
            %s
            You can still make %s (out of 3) posts today.<br>
            Create a post (image + caption):<br><br>
            <form method="post" action="/create" enctype="multipart/form-data">
                <input type="file" name="image" required="true"/><br>
                <textarea type="text" name="caption" placeholder="what's on your mind?" required="true"></textarea><br>
                <input type="submit" value="Create post"/>
            </form>
            """ % (_HEADER_MENU_HTML, (3 - number_of_posts_made_today))
        else:
            return _HEADER_MENU_HTML + """
            Unable to create more posts.
            You have reached today's post quota (3).
            """
    elif request.method == 'POST':
        # If required data is missing, bail out.
        if 'image' not in request.files or \
                request.files['image'].filename == '' or \
                request.form['caption'] == '':
            return redirect('/error', code=302)

        caption = request.form['caption']
        image = request.files['image']
        stream = image.read()
        encoded_stream = base64.b64encode(stream)  # Image in base64.

        # Save the post and associate it to its creator.
        db = get_db()
        cur = db.execute(
            'insert into posts (image, caption, username, created_at)  values (?, ?, ?, date("now"))',
            [encoded_stream, caption, request.cookies.get('username')]
        )
        db.commit()

        return redirect('/browse', code=302)


@app.route('/browse', methods=['GET'])
@login_required
def browse():
    db = get_db()
    cur = db.execute('select * from posts order by created_at desc')
    posts = cur.fetchall()

    if len(posts) == 0:
        return _HEADER_MENU_HTML + 'No posts yet! Go <a href="/create">create</a> one!'

    html = ''
    for post in posts:
        image_base64 = post[1]
        caption = post[2]
        created_at = post[3]
        username = post[4]
        html += 'By ' + username + ' on ' + created_at + ' - ' + caption + ':' + '<br><img src="data:image/gif;base64,' + image_base64 + '"/><hr>'
    return _HEADER_MENU_HTML + html


@app.route('/logout', methods=['GET'])
def logout():
    response = app.make_response(redirect('/', code=302))
    response.set_cookie('username', value='')
    return response


@app.route('/error', methods=['GET'])
def error():
    return 'ERROR: Something went wrong. You gave me invalid/incomplete data.'


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8888)
