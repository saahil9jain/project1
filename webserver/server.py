#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally
    python server.py

Go to http://localhost:8111 in your browser

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from cd_collection_queries import *

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of:
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
# DATABASEURI = "sqlite:///test.db"
DATABASEURI = "postgresql://sj2675:huw2z@104.196.175.120/postgres"

# This line creates a database engine that knows how to connect to the URI above
engine = create_engine(DATABASEURI)

# START SQLITE SETUP CODE
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
#
# The setup code should be deleted once you switch to using the Part 2 postgresql database
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
# END SQLITE SETUP CODE

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    #print request.args

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    context = dict(counter = trackCount)

    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    return render_template("index.html", **context)

@app.route('/list_all_artists/')
def list_all_artists():

    # list all artists
    cursor = g.conn.execute(LIST_ARTISTS)
    artists = []
    for result in cursor:
        artists.append("%s: [%s]" % (result[0], result[1]))
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(data = artists, counter=trackCount)
    return render_template("list_all_artists.html", **context)

@app.route('/list_all_albums/')
def list_all_albums():

    cursor = g.conn.execute(LIST_ALBUMS)
    albums = []
    for result in cursor:
        albums.append("%s: [%s], released by [%s] and [%s] on %s" % (result[0], result[1], result[2], result[3], result[4]))
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(data = albums, counter=trackCount)
    return render_template("list_all_albums.html", **context)

@app.route('/list_all_tracks/')
def list_all_tracks():

    cursor = g.conn.execute(LIST_TRACKS)
    tracks = []
    for result in cursor:
        tracks.append("\"%s\": track %s on [%s], by [%s]" % (result[0], result[1], result[2], result[3]))
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(data = tracks, counter=trackCount)
    return render_template("list_all_tracks.html", **context)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
    return render_template("anotherfile.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    print name
    cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
    g.conn.execute(text(cmd), name1 = name, name2 = name);
    return redirect('/')

@app.route('/list_albums_given_artist', methods=['POST'])
def list_albums_given_artist():

    artist_id = request.form['artist_id']

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    cursor = g.conn.execute(text(GET_ARTIST_NAME_BY_ARTIST_ID), artist_id=artist_id)
    artist_name = []
    for result in cursor:
        artist_name.append("%s" % (result[0]))
    cursor.close()

    cursor = g.conn.execute(text(LIST_ALBUMS_GIVEN_ARTIST), artist_id=artist_id)
    albums = []
    for result in cursor:
        albums.append("%s: [%s], released by [%s] on %s" % (result[0], result[1], result[2], result[3]))
    cursor.close()

    context = dict(counter=trackCount, artist_name=artist_name, data=albums)
    return render_template("list_albums_given_artist.html", **context)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using
            python server.py

        Show the help text using
            python server.py --help
        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()

