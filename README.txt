This is the twitty twitter like API it uses a MySQL backend (description at the bottom):

The API end points are, they need a valid API key as argument to be able to use them:

/user/<username>            GET
/user/<username>/follow     POST
/user/<username>/unfollow   POST
/user/<username>/following  GET
/user/<username>/followers  GET

The API key is passed to the server as ?key=API key

THe API key is generated based on the username, the user can generate one based on a valid user name. This is of course
insecure and in order to reach HMAC compliance we can generate it using the flask server SECRET_KEY, email and username.

For purposes of acceptance testing 10 generic users where generated using the secure_token_gen.py script bundled.
Example output:

User: user1 token: d5ef19c2b1714f87e0042e4f822bf722b30239f7
User: user2 token: 4a7697a738c4b4ad2c4f9b4a3511cb56289f547e
User: user3 token: b324d5755d62a48ad78e15e797cfdbf1760df7e5
User: user4 token: 3a31ee9395163bb7c31c935065ecebb7422f1199
User: user5 token: 047b7df2a1b8e14467754a2ed703541802e73a2a
User: user6 token: d921c6fbb8002b12f240e567f561a277e5f3a328
User: user7 token: 53c84f4e368048ef7540046e55ccb4367ae1f166
User: user8 token: 1190d46b9c50cccb725587e1bf73f04f07c58f50
User: user9 token: 28a35a3a31ab1c80f736a3ceeca7c6161c4c3ca8
User: user10 token: 2634730169a46ff4b7394f18588060fcb2a07c2e

For example:

http://izaac.pythonanywhere.com/user/user10?key=28a35a3a31ab1c80f736a3ceeca7c6161c4c3ca8

Will allow the user to read the twitts of user10 plus the twitts from users user10 is following. The same applies for
the following and followers endpoints. Or a 401 error will be thrown by the server otherwise.

The follow and unfollow features uses the API key to determine the user that is trying to follow the user in the
endpoint URL:

For example:

http://izaac.pythonanywhere.com/user/user10/follow?key=28a35a3a31ab1c80f736a3ceeca7c6161c4c3ca8

The server will determine the user requesting to follow user10 is user9 in the scenario that user9 is not following
user10.

The same API key behavior in the previous example is used for the unfollow feature.

To run the unittests go to the test.py file and start the script.

TODO: Acceptance testing of json schema, there is a write up in the tests_int.py for acceptance/integration. This uses
the 'validictory' python library, most of the tests where manually ran as there is a bug in the library.


The user can visit a live example at:

http://izaac.pythonanywhere.com

10 generic users are present, user1..user10, 100 random generated messages added to the database and the following
relationships in the followers table:

follower_id followed_id
        3, 1
        8, 2
        2, 3
        2, 4
        7, 5
        5, 6
        1, 7
        9, 8
        3, 9
        4, 10


MYSQL Schema:
+-------------------+
| Tables_in_example |
+-------------------+
| followers         |
| message           |
| user              |
+-------------------+

Table followers
===============
follower_id, followed_id
---------------
follower_id      int(11)
followed_id      int(11)

Table message
=============
message_id, text, pub_date, user_id
-------------
message_id       int(11) PK
text             varchar(255)
pub_date         datetime
user_id          int(11)

Table user
==========
id, username, password, email
----------
id               int(11) PK
username         varchar(120)
password         varchar(80)
email            varchar(120)

