#!/usr/bin/env python2.7

"""
This module contains SQL query strings used in the cd collection app
"""

COUNT_TRACKS = (
        "SELECT COUNT (*) "
        "FROM track_contains"
        )

LIST_ALL_ARTISTS = (
        "SELECT artist_id, artist_name "
        "FROM artist"
        )

LIST_ALL_ALBUMS = (
        "SELECT A.album_id, A.album_title, A2.artist_name, R.company_name, A.release_date "
        "FROM album_releasedby as A, artist as A2, recordcompany as R "
        "WHERE A.company_id=R.company_id AND A.artist_id=A2.artist_id"
        )

LIST_ALL_TRACKS = (
        "SELECT T.track_title, T.track_num, A2.artist_name, A.album_title, A.album_id "
        "FROM track_contains as T, album_releasedby as A, artist as A2 "
        "WHERE T.album_id=A.album_id AND A.artist_id=A2.artist_id "
        "ORDER BY T.track_title"
        )

LIST_CONTRIBUTORS_GIVEN_TRACK = (
        "SELECT A.artist_name, R.role, R.recording_location, R.recording_date "
        "FROM artist as A, records as R "
        "WHERE R.track_num=(:track_num) AND R.album_id=(:album_id) AND R.artist_id=A.artist_id"
        )

LIST_ALBUMS_GIVEN_ARTIST = (
        "SELECT A.album_id, A.album_title, R.company_name, A.release_date "
        "FROM album_releasedby AS A, recordcompany as R "
        "WHERE A.artist_id = (:artist_id) AND A.company_id=R.company_id"
        )

GET_ARTIST_NAME_BY_ARTIST_ID = (
        "SELECT A.artist_name "
        "FROM artist as A "
        "WHERE A.artist_id=(:artist_id)"
        )

LIST_TRACKS_GIVEN_ALBUM_ID= (
        "SELECT T.track_num, T.track_title "
        "FROM track_contains as T "
        "WHERE T.album_id=(:album_id) "
        )

GET_ALBUM_NAME_GIVEN_ID = (
        "SELECT A.album_title "
        "FROM album_releasedby as A "
        "WHERE A.album_id=(:album_id)"
        )

INSERT_NEW_RECORDCOMPANY = "INSERT INTO recordcompany VALUES (DEFAULT, :company_name)"

INSERT_NEW_ARTIST = (
        "INSERT INTO artist VALUES (DEFAULT, (:artist_name)); "
        "INSERT INTO employs1 VALUES ((:company_id), (SELECT MAX(artist_id) FROM artist))"
        )

INSERT_NEW_ALBUM = (
        "INSERT INTO album_releasedby "
        "VALUES (DEFAULT, (:album_title), (:release_date), (:company_id), (:artist_id)) "
        )

INSERT_NEW_TRACK = (
        "INSERT INTO track_contains "
        "VALUES ((:track_num), (:track_title), (:duration_secs), (:album_id))"
        )

INSERT_NEW_RECORDING_CREDIT = (
        "INSERT INTO records "
        "VALUES ((:recording_date), (:recording_location), (:role), (:artist_id), (:track_num), (:album_id))"
        )

INSERT_NEW_ARTIST_RECORDCOMPANY_EMPLOYMENT = "INSERT INTO employs1 VALUES ((:company_id), (:artist_id))"








