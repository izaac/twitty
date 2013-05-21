from flask import Flask, request, abort,  jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import make_secure_token
from flask.ext.restless import APIManager
from sqlalchemy.orm import validates, exc
from werkzeug.exceptions import Unauthorized
from copy import deepcopy
import os
import socket

APIToken = '9f1a7e2e3e91db0ee09ba2325d3207073287db7c'

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config.from_object(__name__)


def deserialize_datetime(value):
    """
    Deserialize datetime object into string form for JSON processing.
    """
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


class APIUnauthorized(Unauthorized):
    """
    Overrides Unauthorized class to provide a custom 401 message for the twitty API
    """
    description = '401: Needs a valid authentication token'

    def get_headers(self, environ):
        return [('content-type', 'application/json'), ]
abort.mapping.update({401: APIUnauthorized})


def auth_func(**kw):
    """
    Helper function to validate API token for Authentication in the API end points
    """
    if len(request.args.getlist("key")) == 0:
        abort(401)
    if 'key' not in request.args:
        abort(401)
    myuser_is = None
    for i in User.query.yield_per(5):
        if i.get_secure_token() == request.args.getlist("key")[0]:
            myuser_is = i
            break
    print myuser_is
    if myuser_is is None:
        abort(401)
    #if not request.args.getlist("key")[0] == myuser_is.get_secure_token():
    #    abort(401)


# for connecting to pythonanywhere DB
def mysqldb_uri():
    """
    Helper function for determining in which System is the twitty script running
    to provide the corresponding connection string to SQL Alchemy

    """
    uri = None
    machine = socket.gethostname()
    if machine == 'morena' or machine == 'testi':
        uri = "mysql+mysqldb://root:services@127.0.0.1:3306/example"
    else:
        uri = "mysql+mysqldb://izaac:services@mysql.server:3306/izaac$default"
    app.config['SQLALCHEMY_DATABASE_URI'] = uri


def create_tables():
    db.create_all()


def drop_tables():
    db.drop_all()

# manage the database with SQLALchemy once the MySQL URI is configured
db = SQLAlchemy(app)


# followers relationship table, this is linked by the User model in its followed relationship
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(db.Model):
    """
    User Database Model
    includes:
    id
    username
    password
    email
    messages: relationship with the Message table
    followed: relationship with the Followers table
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(length=120), unique=True)
    password = db.Column(db.String(length=80))
    email = db.Column(db.String(length=120), unique=True)
    messages = db.relationship("Message", backref="user", lazy="dynamic")
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address

    def follow(self, user):
        """
        add items from the followed relationship, sqlalchemy takes care of managing the association table.
        """
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        """
        remove items from the followed relationship, sqlalchemy takes care of managing the association table.
        """
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        """
        Helper method to determine if a user being added or removed is already in our following/followed relationship
        """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_messages(self):
        """
        Returns the query results from the following query:

        SELECT message.message_id AS message_message_id, message.text AS message_text,
                message.pub_date AS message_pub_date, message.user_id AS message_user_id
        FROM message JOIN followers ON followers.followed_id = message.user_id OR followers.follower_id= message.user_id
        WHERE followers.follower_id = :follower_id_1 ORDER BY message.pub_date DESC
        """

        return Message.query.join(followers,
                                  ((followers.c.followed_id == Message.user_id)
                                   | (followers.c.follower_id == Message.user_id)))\
            .filter(followers.c.follower_id == self.id)\
            .order_by(Message.pub_date.desc())

    def followed_messages_search(self, search):
        """
        Returns the query results from the following query, when the search argument is present:

        SELECT message.message_id AS message_message_id, message.text AS message_text,
                message.pub_date AS message_pub_date, message.user_id AS message_user_id
        FROM message JOIN followers ON followers.followed_id = message.user_id OR followers.follower_id= message.user_id
        WHERE followers.follower_id = :follower_id_1 AND message.text LIKE :text_1 ORDER BY message.pub_date DESC

        SQLAlchemy does the necessary string escaping.
        """

        return Message.query.join(followers,
                                  ((followers.c.followed_id == Message.user_id)
                                   | (followers.c.follower_id == Message.user_id)))\
            .filter(followers.c.follower_id == self.id)\
            .filter(Message.text.like(search))\
            .order_by(Message.pub_date.desc())

    def following(self):
        """
        SELECT user.id AS user_id, user.username AS user_username,
               user.password AS user_password, user.email AS user_email
        FROM user JOIN followers ON followers.follower_id = user.id
        WHERE followers.follower_id =
        """
        return User.query.join(followers, (followers.c.followed_id == User.id))\
            .filter(followers.c.follower_id == self.id)

    def its_followers(self):
        """
        SELECT user.id AS user_id, user.username AS user_username,
               user.password AS user_password, user.email AS user_email
        FROM user JOIN followers ON followers.follower_id = user.id
        WHERE followers.followed_id =
        """
        return User.query.join(followers, (followers.c.follower_id == User.id))\
            .filter(followers.c.followed_id == self.id)

    def get_secure_token(self):
        """
        Returns a secure token for each user generated from its user name.

        In order to get HMAC compliance this can be modified to be generatd from:
        username + email + SECRET_KEY
        make_secure_token(self.username + self.email + SECRET_KEY, key='deterministic')
        """
        return make_secure_token(self.username, key='deterministic')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'username': self.username,
            'messages': self.serialize_many2many,
            'email': self.email
        }

    @property
    def serialize_many2many(self):
        """
        Return object's relations in easily serializeable format.
        Calls many2many's serialize property.
        """
        return [item.serialize for item in self.many2many]


class Message(db.Model):

    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(length=255))
    pub_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'message_id': self.message_id,
            'pub_date': deserialize_datetime(self.pub_date),
            'text': self.text,
            'user_id': self.user_id
        }


@app.route('/user/<username>/', methods=['GET'])
def timeline(username):

    auth_func()

    try:
        theuser = User.query.filter(User.username == username).one()
    except exc.NoResultFound:
        return jsonify(dict(message="User %s not found" % username))

    if len(request.args.getlist("search")) > 0:

        search = request.args.getlist("search")

        if len(search[0]) > 0:
            twitts = theuser.followed_messages_search(search[0]).all()
        elif len(search[0]) > 140:
            return jsonify(dict(message="Search must be less than 140 characters"))
        else:
            twitts = theuser.followed_messages().all()
    else:
        twitts = theuser.followed_messages().all()

    return jsonify(messages=[i.serialize for i in twitts])


@app.route('/user/<username>/follow/', methods=['POST'])
def user_follow(username):

    auth_func()

    try:
        theuser = User.query.filter(User.username == username).one()
    except exc.NoResultFound:
        return jsonify(dict(message="User %s not found" % username))

    token = theuser.get_secure_token()
    sessiontoken = request.args.getlist("key")[0]

    if token == sessiontoken:
        return jsonify(dict(message="You can't follow yourself"))
    else:
        myuser_is = None
        for i in User.query.yield_per(5):
            if i.get_secure_token() == sessiontoken:
                myuser_is = i
                break
        if myuser_is is None:
            return jsonify(dict(message="A user with that token doesn't exist anymore: %s" % sessiontoken))
        u = myuser_is.follow(theuser)
        if u is None:
            return jsonify(dict(message="You can't follow %s" % username))

        db.session.add(u)
        db.session.commit()

        # example: user9 started following: user2
        return jsonify(dict(message="%s started following: %s" %
                                    (myuser_is.username, username)))


@app.route('/user/<username>/unfollow/', methods=['POST'])
def user_unfollow(username):

    auth_func()

    try:
        theuser = User.query.filter(User.username == username).one()
    except exc.NoResultFound:
        return jsonify(dict(message="User %s not found" % username))

    token = theuser.get_secure_token()
    sessiontoken = request.args.getlist("key")[0]

    if token == sessiontoken:
        return jsonify(dict(message="You can't unfollow yourself"))
    else:
        myuser_is = None
        for i in User.query.yield_per(5):
            if i.get_secure_token() == sessiontoken:
                myuser_is = i
                break
        if myuser_is is None:
            return jsonify(dict(message="A user with that token doesn't exist anymore: %s" % sessiontoken))
        u = myuser_is.unfollow(theuser)

        if u is None:
            return jsonify(dict(message="You can't unfollow %s" % username))

        db.session.add(u)
        db.session.commit()

        return jsonify(dict(message="%s is now not following: %s" %
                                    (myuser_is.username, username)))


@app.route('/user/<username>/followers/', methods=['GET'])
def user_followers(username):

    auth_func()

    try:
        theuser = User.query.filter(User.username == username).one()
    except exc.NoResultFound:
        return jsonify(dict(message="User %s not found" % username))

    followers = theuser.its_followers().all()

    if followers is None:
        return jsonify(dict(message="No one is following %s" % username))

    data = {}
    followers_list = []
    for i in followers:
        data['id'] = i.id
        data['username'] = i.username
        followers_list.append(deepcopy(data))

    return jsonify(dict(its_followers=followers_list))


@app.route('/user/<username>/following/', methods=['GET'])
def user_following(username):

    auth_func()

    try:
        theuser = User.query.filter(User.username == username).one()
    except exc.NoResultFound:
        return jsonify(dict(message="User %s not found" % username))

    following = theuser.following().all()

    if following is None:
        return jsonify(dict(message="%s is following no one." % username))
    data = {}
    following_list = []
    for i in following:
        data['id'] = i.id
        data['username'] = i.username
        following_list.append(deepcopy(data))

    return jsonify(dict(user_is_following=following_list))

manager = APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(User, methods=['GET'],
                   url_prefix='/get',
                   results_per_page=50,
                   include_columns=['id', 'username', 'email', 'messages'],
                   )
manager.create_api(User, methods=['POST'], url_prefix='/add')
manager.create_api(Message, methods=['POST'], url_prefix='/add')
headers = {'content-type': 'application/json'}

@app.route('/', methods=['GET'])
def hello_world():
    return 'twitty API server, please use auth token to use the end-points.'


if __name__ == '__main__':

    mysqldb_uri()
    #drop_tables()
    create_tables()
    app.run()