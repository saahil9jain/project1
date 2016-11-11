#!/usr/bin/env python2.7

"""
This module contains SQL query strings used in the cd collection app
"""

COUNT_TRACKS = (
        "SELECT COUNT (*) "
        "FROM track_contains"
        )

LIST_ARTISTS = (
        "SELECT artist_id, artist_name "
        "FROM artist"
        )

LIST_ALBUMS = (
        "SELECT A.album_id, A.album_title, A2.artist_name, R.company_name, A.release_date "
        "FROM album_releasedby as A, artist as A2, recordcompany as R "
        "WHERE A.company_id=R.company_id AND A.artist_id=A2.artist_id"
        )

LIST_TRACKS = (
        "SELECT T.track_title, T.track_num, A.album_title, A2.artist_name "
        "FROM track_contains as T, album_releasedby as A, artist as A2 "
        "WHERE T.album_id=A.album_id AND A.artist_id=A2.artist_id "
        "ORDER BY T.track_title"
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

