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
    cursor = g.conn.execute(LIST_ALL_ARTISTS)
    artists = []
    for result in cursor:
        artists.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(data = artists, counter=trackCount)
    return render_template("list_all_artists.html", **context)

@app.route('/list_all_albums/')
def list_all_albums():

    cursor = g.conn.execute(LIST_ALL_ALBUMS)
    albums = []
    for result in cursor:
        albums.append("#%s: [%s], released by [%s] and [%s] on %s" % (result[0], result[1], result[2], result[3], result[4]))
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(data = albums, counter=trackCount)
    return render_template("list_all_albums.html", **context)

@app.route('/list_all_tracks/')
def list_all_tracks():

    cursor = g.conn.execute(LIST_ALL_TRACKS)
    tracks = []
    for result in cursor:
        #tracks.append("-- \"%s\": track %s on [%s]'s album [%s]" % (result[0], result[1], result[2], result[3]))
        tracks.append("\"%s\": track %s on [%s]'s album [%s]" % (result[0], result[1], result[2], result[3]))
        cursor2 = g.conn.execute(text(LIST_CONTRIBUTORS_GIVEN_TRACK), track_num=result[1], album_id=result[4])
        contributors = []
        for result2 in cursor2:
            tracks.append("---Recording credit: [%s], [%s], [%s], [%s]" % (result2[0], result2[1], result2[2], result2[3]))
        cursor2.close
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(data = tracks, counter=trackCount)
    return render_template("list_all_tracks.html", **context)

@app.route('/list_all_recordcompanies/')
def list_all_recordcompanies():

    cursor = g.conn.execute(LIST_ALL_RECORDCOMPANIES)
    recordcompanies = []
    for result in cursor:
        recordcompanies.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(data = recordcompanies, counter=trackCount)
    return render_template("list_all_recordcompanies.html", **context)

@app.route('/list_all_reviews/')
def list_all_reviews():

    cursor = g.conn.execute(LIST_ALL_FAN_REVIEWS)
    fReviews = []
    for result in cursor:
        fReviews.append("%s gave a score of %s/5 to %s on %s" % (result[0], result[1], result[2], result[3]))
    cursor.close()
    
    cursor = g.conn.execute(LIST_ALL_CRITIC_REVIEWS)
    cReviews = []
    for result in cursor:
        cReviews.append("%s gave a score of %s/5 to %s on %s" % (result[0], result[1], result[2], result[3]))
    cursor.close()

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    context = dict(cData = cReviews, fData = fReviews, counter=trackCount)
    return render_template("list_all_reviews.html", **context)

# This is an example of a different path.  You can see it at
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
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
        albums.append("#%s: [%s], released by [%s] on %s" % (result[0], result[1], result[2], result[3]))
    cursor.close()

    context = dict(counter=trackCount, artist_name=artist_name, data=albums)
    return render_template("list_albums_given_artist.html", **context)

@app.route('/list_artists_given_recordcompany_id', methods=['POST'])
def list_artists_given_recordcompany_id():

    company_id = request.form['company_id']

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    cursor = g.conn.execute(text(GET_COMPANY_NAME_BY_COMPANY_ID), company_id=company_id)
    company_name = []
    for result in cursor:
        company_name.append("%s" % (result[0]))
    cursor.close()

    cursor = g.conn.execute(text(LIST_ARTISTS_GIVEN_COMPANY), company_id=company_id)
    artists = []
    for result in cursor:
        artists.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    context = dict(counter=trackCount, company_name=company_name, data=artists)
    return render_template("list_artists_given_recordcompany_id.html", **context)

@app.route('/list_tracks_given_album_id', methods=['POST'])
def list_tracks_given_album_id():

    album_id = request.form['album_id']

    cursor = g.conn.execute(COUNT_TRACKS)
    trackCount = (cursor.first()[0])

    cursor = g.conn.execute(text(GET_ALBUM_NAME_GIVEN_ID), album_id=album_id)
    album_title = cursor.first()[0]

    cursor = g.conn.execute(text(LIST_TRACKS_GIVEN_ALBUM_ID), album_id=album_id)
    tracks = []
    for result in cursor:
        tracks.append("Track #%s: [%s]" % (result[0], result[1]))
        cursor2 = g.conn.execute(text(LIST_CONTRIBUTORS_GIVEN_TRACK), track_num=result[0], album_id=album_id)
        contributors = []
        for result2 in cursor2:
            tracks.append("---Recording credit: [%s], [%s], [%s], [%s]" % (result2[0], result2[1], result2[2], result2[3]))
        cursor2.close
    cursor.close()

    context = dict(counter=trackCount, album_title=album_title, data=tracks)
    return render_template("list_tracks_given_album_id.html", **context)

@app.route('/insert_new_recordcompany', methods=['POST'])
def insert_new_recordcompany():

    company_name = request.form['company_name']

    try:
        g.conn.execute(text(INSERT_NEW_RECORDCOMPANY), company_name=company_name)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_artist', methods=['POST'])
def insert_new_artist():

    artist_name = request.form['artist_name']
    company_id = request.form['company_id']

    try:
        g.conn.execute(text(INSERT_NEW_ARTIST), artist_name=artist_name, company_id=company_id)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_artist_recordcompany_employment', methods=['POST'])
def insert_new_artist_recordcompany_employment():

    artist_id = request.form['artist_id']
    company_id = request.form['company_id']

    try:
        g.conn.execute(text(INSERT_NEW_ARTIST_RECORDCOMPANY_EMPLOYMENT),
                artist_id=artist_id, company_id=company_id)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_album', methods=['POST'])
def insert_new_album():

    album_title = request.form['album_title']
    release_date = request.form['release_date']
    company_id = request.form['company_id']
    artist_id = request.form['artist_id']

    try:
        g.conn.execute(text(INSERT_NEW_ALBUM),
                album_title=album_title, release_date=release_date, company_id=company_id, artist_id=artist_id)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_track', methods=['POST'])
def insert_new_track():

    track_num = request.form['track_num']
    track_title = request.form['track_title']
    duration = request.form['duration']
    album_id = request.form['album_id']


    try:
        g.conn.execute(text(INSERT_NEW_TRACK),
                track_num=track_num, track_title=track_title, duration_secs=duration, album_id=album_id)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_recording_credit', methods=['POST'])
def insert_new_recording_credit():

    recording_date = request.form['recording_date']
    recording_location = request.form['recording_location']
    role = request.form['role']
    artist_id = request.form['artist_id']
    track_num = request.form['track_num']
    album_id = request.form['album_id']

    try:
        g.conn.execute(text(INSERT_NEW_RECORDING_CREDIT),
                recording_date=recording_date,
                recording_location=recording_location, role=role,
                artist_id=artist_id, track_num=track_num, album_id=album_id)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_critic', methods=['POST'])
def insert_new_critic():

    critic_name = request.form['critic_name']

    try:
        g.conn.execute(text(INSERT_NEW_CRITIC), person_name=critic_name)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_fan', methods=['POST'])
def insert_new_fan():

    fan_name = request.form['fan_name']

    try:
        g.conn.execute(text(INSERT_NEW_FAN), person_name=fan_name)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/insert_new_review', methods=['POST'])
def insert_new_review():

    person_id = request.form['person_id']
    album_id = request.form['album_id']
    score = request.form['score']
    review_date = request.form['review_date']

    try:
        g.conn.execute(text(INSERT_NEW_REVIEW), person_id=person_id,
                album_id=album_id, score=score, review_date=review_date)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/invalid_action/')
def invalid_action():
    return render_template("invalid_action.html");

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

