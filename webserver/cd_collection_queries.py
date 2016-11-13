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

LIST_ALL_CRITICS = (
        "SELECT P.person_id, P.person_name "
        "FROM critic as C, person as P "
        "WHERE C.person_id=P.person_id"
        )

LIST_ALL_FANS = (
        "SELECT P.person_id, P.person_name "
        "FROM fan as F, person as P "
        "WHERE F.person_id=P.person_id"
        )

LIST_ALL_PUBLICATIONS = (
        "SELECT pub_id, pub_name "
        "FROM publication "
        )

LIST_ALL_RECORDCOMPANIES = (
        "SELECT company_id, company_name "
        "FROM recordcompany"
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

LIST_TRACKS_GIVEN_ARTIST = (
        "SELECT T.track_title, T.track_num, A.album_title, T.duration_secs, R.recording_date, R.recording_location, R.role "
        "FROM track_contains AS T, records AS R, album_releasedby AS A "
        "WHERE R.artist_id = (:artist_id) AND T.album_id = R.album_id AND T.track_num = R.track_num AND A.album_id = R.album_id"
        )

LIST_ARTISTS_GIVEN_COMPANY = (
        "SELECT A.artist_id, A.artist_name "
        "FROM employs1 AS E, artist as A "
        "WHERE E.company_id = (:company_id) AND E.artist_id = A.artist_id"
        )

LIST_CRITICS_GIVEN_PUBLICATION = (
        "SELECT P.person_id, P.person_name "
        "FROM employs2 AS E, person as P "
        "WHERE E.pub_id = (:pub_id) AND E.person_id = P.person_id"
        )

GET_ARTIST_NAME_BY_ARTIST_ID = (
        "SELECT A.artist_name "
        "FROM artist as A "
        "WHERE A.artist_id=(:artist_id)"
        )

LIST_ALL_CRITIC_REVIEWS = (
        "SELECT P.person_name, R.score, A.album_title, R.review_date "
        "FROM person as P, reviews as R, album_releasedby as A, critic as C  "
        "WHERE R.person_id=P.person_id AND R.album_id=A.album_id AND R.person_id=C.person_id"
        )

LIST_ALL_FAN_REVIEWS = (
        "SELECT P.person_name, R.score, A.album_title, R.review_date "
        "FROM person as P, reviews as R, album_releasedby as A, fan as F  "
        "WHERE R.person_id=P.person_id AND R.album_id=A.album_id AND R.person_id=F.person_id"
        )

GET_COMPANY_NAME_BY_COMPANY_ID = (
        "SELECT C.company_name "
        "FROM recordcompany as C "
        "WHERE C.company_id=(:company_id)"
        )

GET_PUB_NAME_BY_PUB_ID = (
        "SELECT P.pub_name "
        "FROM publication as P "
        "WHERE P.pub_id=(:pub_id)"
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

INSERT_NEW_CRITIC = (
        "INSERT INTO person VALUES (DEFAULT, (:person_name)); "
        "INSERT INTO critic VALUES ((SELECT MAX(person_id) FROM person))"
        )

INSERT_NEW_FAN = (
        "INSERT INTO person VALUES (DEFAULT, (:person_name)); "
        "INSERT INTO fan VALUES ((SELECT MAX(person_id) FROM person))"
        )

INSERT_NEW_REVIEW = "INSERT INTO reviews VALUES ((:person_id), (:album_id), (:score), (:review_date))"

CHECK_IS_CRITIC = "SELECT * FROM critic AS C WHERE C.person_id=(:person_id)"

INSERT_NEW_CRITIC_PUBLICATION_EMPLOYMENT = "INSERT INTO employs2 VALUES ((:person_id), (:pub_id))"

FIND_LARGEST_COMPANY = (
        "SELECT co.company_name "
        "FROM recordcompany as co "
        "WHERE co.company_id = ( SELECT Temp1.company_id "
                                "FROM   ( SELECT E.company_id, COUNT(*) AS employeecount "
                                        "FROM Employs1 as E "
                                        "GROUP BY E.company_id ) AS Temp1 "
                                "WHERE  Temp1.employeecount = ( SELECT MAX(Temp2.employeecount) "
                                                "FROM ( SELECT E.company_id, COUNT(*) AS employeecount "
                                                        "FROM Employs1 as E "
                                                        "GROUP BY E.company_id ) AS Temp2 ))"
        )

FIND_HOTTEST_ALBUMS = (
        "SELECT DISTINCT A.album_id, A.album_title "
        "FROM reviews as R, album_releasedby as A "
        "WHERE R.album_id = A.album_id AND R.score = 5"
        "ORDER BY A.album_id ASC"
        )

