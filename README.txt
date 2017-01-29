Cybersecurity Base Project 1

Cyber Security Base - Course Project I
--------------------------------------

This vulnerable web app is written in Python 2.7 using flask. This is the
first course project for https://cybersecuritybase.github.io/.

The app uses port 8888.

Installation instructions
-------------------------

Make sure to have Python 2.7 installed. You'll also need sqlite3, but it's included in Python already.

LINUX (Ubuntu)
1) Install pip:
 apt-get install python-pip
2) Install this project's requirements with pip:
 pip install --user -r requirements.txt

OS X
1) Install pip:
 easy_install pip
2) Install this project's requirements with pip:
 pip install --user -r requirements.txt

WINDOWS:
1) Install pip from:
 https://pypi.python.org/pypi/pip
2) Install this project's requirements with pip:
 pip install --user -r requirements.txt

Running instructions
--------------------

Being in the "app" folder run the following commands.

LINUX and OS X:
1) export FLASK_APP=./app.py
2) flask initdb
3) python ./app.py

WINDOWS:
1) set FLASK_APP=./app.py
2) flask initdb
3) python ./app.py

Credentials
-----------
Username: johnny
Passowrd: walker

You can also check/cheat by looking at schema.sql.
