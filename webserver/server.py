#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Web server for CD Collection

Gregory Chen    glc2121@columbia.edu
Saahil Jain     sj2675@columbia.edu
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from cd_collection_queries import *

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# URI in the format of: "postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
DATABASEURI = "postgresql://sj2675:huw2z@104.196.175.120/postgres"

# Create db engine that knows how to connect to the URI above
engine = create_engine(DATABASEURI) 

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
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#       @app.route("/foobar/", methods=["POST", "GET"])
# PROTIP: (the trailing / in the path is important)
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
@app.route('/')
def index():

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    # Jinja documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    context = dict(counter = trackCount)

    # render_template looks in the templates/ folder for files.
    return render_template("index.html", **context)

@app.route('/list_all_artists/')
def list_all_artists():

    # list all artists
    try:
        cursor = g.conn.execute(LIST_ALL_ARTISTS)
    except:
        return redirect('/invalid_action/')
    artists = []
    for result in cursor:
        artists.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    context = dict(data = artists, counter=trackCount)
    return render_template("list_all_artists.html", **context)

@app.route('/list_all_albums/')
def list_all_albums():

    try:
        cursor = g.conn.execute(LIST_ALL_ALBUMS)
    except:
        return redirect('/invalid_action/')
    albums = []
    for result in cursor:
        albums.append("#%s: [%s], released by [%s] and [%s] on %s" % (result[0], result[1], result[2], result[3], result[4]))
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    context = dict(data = albums, counter=trackCount)
    return render_template("list_all_albums.html", **context)

@app.route('/list_hottest_albums/')
def list_hottest_albums():

    try:
        cursor = g.conn.execute(FIND_HOTTEST_ALBUMS)
    except:
        return redirect('/invalid_action/')
    albums = []
    for result in cursor:
        albums.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    context = dict(data = albums, counter=trackCount)
    return render_template("list_hottest_albums.html", **context)

@app.route('/list_all_tracks/')
def list_all_tracks():

    cursor = g.conn.execute(LIST_ALL_TRACKS)
    tracks = []
    for result in cursor:
        tracks.append("\"%s\": track %s on [%s]'s album [%s]" % (result[0], result[1], result[2], result[3]))
        try:
            cursor2 = g.conn.execute(text(LIST_CONTRIBUTORS_GIVEN_TRACK), track_num=result[1], album_id=result[4])
        except:
            return redirect('/invalid_action/')
        contributors = []
        for result2 in cursor2:
            tracks.append("---Recording credit: [%s], [%s], [%s], [%s]" % (result2[0], result2[1], result2[2], result2[3]))
        cursor2.close
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    context = dict(data = tracks, counter=trackCount)
    return render_template("list_all_tracks.html", **context)

@app.route('/list_all_recordcompanies/')
def list_all_recordcompanies():

    try:
        cursor = g.conn.execute(LIST_ALL_RECORDCOMPANIES)
    except:
        return redirect('/invalid_action/')
    recordcompanies = []
    for result in cursor:
        recordcompanies.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    try:
        cursor = g.conn.execute(FIND_LARGEST_COMPANY)
    except:
        return redirect('/invalid_action/')
    largestCompany = []
    for result in cursor:
        largestCompany.append("%s" % (result[0]))
    cursor.close()

    context = dict(data = recordcompanies, counter=trackCount, largestCompany=largestCompany)
    return render_template("list_all_recordcompanies.html", **context)

@app.route('/list_all_reviews/')
def list_all_reviews():

    try:
        cursor = g.conn.execute(LIST_ALL_FAN_REVIEWS)
    except:
        return redirect('/invalid_action/')
    fReviews = []
    for result in cursor:
        fReviews.append("%s gave a score of %s/5 to %s on %s" % (result[0], result[1], result[2], result[3]))
    cursor.close()

    try:
        cursor = g.conn.execute(LIST_ALL_CRITIC_REVIEWS)
    except:
        return redirect('/invalid_action/')
    cReviews = []
    for result in cursor:
        cReviews.append("%s gave a score of %s/5 to %s on %s" % (result[0], result[1], result[2], result[3]))
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    context = dict(cData = cReviews, fData = fReviews, counter=trackCount)
    return render_template("list_all_reviews.html", **context)

@app.route('/list_all_users/')
def list_all_users():

    try:
        cursor = g.conn.execute(LIST_ALL_CRITICS)
    except:
        return redirect('/invalid_action/')
    cUsers = []
    for result in cursor:
        cUsers.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    try:
        cursor = g.conn.execute(LIST_ALL_FANS)
    except:
        return redirect('/invalid_action/')
    fUsers = []
    for result in cursor:
        fUsers.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    try:
        cursor = g.conn.execute(FIND_ACTIVE_USERS)
    except:
        return redirect('/invalid_action/')
    activeUsers = []
    for result in cursor:
        activeUsers.append("%s with %s reviews" % (result[0], result[1]))
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    context = dict(fData = fUsers, cData = cUsers, activeUsers = activeUsers, counter=trackCount)
    return render_template("list_all_users.html", **context)

@app.route('/list_all_publications/')
def list_all_publications():

    try:
        cursor = g.conn.execute(LIST_ALL_PUBLICATIONS)
    except:
        return redirect('/invalid_action/')
    publications = []
    for result in cursor:
        publications.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    context = dict(Data = publications, counter=trackCount)
    return render_template("list_all_publications.html", **context)

@app.route('/list_albums_given_artist', methods=['POST'])
def list_albums_given_artist():

    artist_id = request.form['artist_id']

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    try:
        cursor = g.conn.execute(text(GET_ARTIST_NAME_BY_ARTIST_ID), artist_id=artist_id)
    except:
        return redirect('/invalid_action/')
    artist_name = []
    for result in cursor:
        artist_name.append("%s" % (result[0]))
    cursor.close()

    try:
        cursor = g.conn.execute(text(LIST_ALBUMS_GIVEN_ARTIST), artist_id=artist_id)
    except:
        return redirect('/invalid_action/')
    albums = []
    for result in cursor:
        albums.append("#%s: [%s], released by [%s] on %s" % (result[0], result[1], result[2], result[3]))
    cursor.close()

    context = dict(counter=trackCount, artist_name=artist_name, data=albums)
    return render_template("list_albums_given_artist.html", **context)

@app.route('/list_critics_given_publication', methods=['POST'])
def list_critics_given_publication():

    pub_id = request.form['pub_id']

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    try:
        cursor = g.conn.execute(text(GET_PUB_NAME_BY_PUB_ID), pub_id=pub_id)
    except:
        return redirect('/invalid_action/')
    pub_name = []
    for result in cursor:
        pub_name.append("%s" % (result[0]))
    cursor.close()

    try:
        cursor = g.conn.execute(text(LIST_CRITICS_GIVEN_PUBLICATION), pub_id=pub_id)
    except:
        return redirect('/invalid_action/')
    critics = []
    for result in cursor:
        critics.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    context = dict(counter=trackCount, pub_name=pub_name, data=critics)
    return render_template("list_critics_given_publication.html", **context)

@app.route('/list_tracks_given_artist', methods=['POST'])
def list_tracks_given_artist():

    artist_id = request.form['artist_id']

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    try:
        cursor = g.conn.execute(text(GET_ARTIST_NAME_BY_ARTIST_ID), artist_id=artist_id)
    except:
        return redirect('/invalid_action/')
    artist_name = []
    for result in cursor:
        artist_name.append("%s" % (result[0]))
    cursor.close()

    try:
        cursor = g.conn.execute(text(LIST_TRACKS_GIVEN_ARTIST), artist_id=artist_id)
    except:
        return redirect('/invalid_action/')
    tracks = []
    for result in cursor:
        tracks.append("#%s: track %s in %s, seconds: %s, recording location: %s, recording date: %s, role: %s" % (result[0], result[1], result[2], result[3], result[4], result[5], result[6]))
    cursor.close()

    context = dict(counter=trackCount, artist_name=artist_name, data=tracks)
    return render_template("list_tracks_given_artist.html", **context)

@app.route('/list_artists_given_recordcompany_id', methods=['POST'])
def list_artists_given_recordcompany_id():

    company_id = request.form['company_id']

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    try:
        cursor = g.conn.execute(text(GET_COMPANY_NAME_BY_COMPANY_ID), company_id=company_id)
    except:
        return redirect('/invalid_action/')
    company_name = []
    for result in cursor:
        company_name.append("%s" % (result[0]))
    cursor.close()

    try:
        cursor = g.conn.execute(text(LIST_ARTISTS_GIVEN_COMPANY), company_id=company_id)
    except:
        return redirect('/invalid_action/')
    artists = []
    for result in cursor:
        artists.append("#%s: [%s]" % (result[0], result[1]))
    cursor.close()

    context = dict(counter=trackCount, company_name=company_name, data=artists)
    return render_template("list_artists_given_recordcompany_id.html", **context)

@app.route('/list_tracks_given_album_id', methods=['POST'])
def list_tracks_given_album_id():

    album_id = request.form['album_id']

    try:
        cursor = g.conn.execute(COUNT_TRACKS)
    except:
        return redirect('/invalid_action/')
    trackCount = (cursor.first()[0])
    cursor.close()

    try:
        cursor = g.conn.execute(text(GET_ALBUM_NAME_GIVEN_ID), album_id=album_id)
    except:
        return redirect('/invalid_action/')
    album_title = cursor.first()[0]

    try:
        cursor = g.conn.execute(text(LIST_TRACKS_GIVEN_ALBUM_ID), album_id=album_id)
    except:
        return redirect('/invalid_action/')
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

@app.route('/insert_new_critic_publication_employment', methods=['POST'])
def insert_new_critic_publication_employment():

    critic_id = request.form['person_id']
    pub_id = request.form['pub_id']

    try: 
        if g.conn.execute(text(CHECK_IS_CRITIC), person_id=critic_id).rowcount == 0:
            return redirect('/invalid_action/')
    except:
        return redirect('/invalid_action/')

    try:
        g.conn.execute(text(INSERT_NEW_CRITIC_PUBLICATION_EMPLOYMENT),
                person_id=critic_id, pub_id=pub_id)
        return redirect('/')
    except:
        return redirect('/invalid_action/')

@app.route('/invalid_action/')
def invalid_action():
    return render_template("invalid_action.html");


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

