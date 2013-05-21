__author__ = 'izaac'
import json
import requests
import random
import string
import datetime
from flask.ext.restless import APIManager
from twitty import User, Message, app, db
#from sqlalchemy.orm import exc
import socket
import os
#from flask.ext.login import make_secure_token

# datetime.datetime.utcnow()
# headers = {'content-type': 'application/json', 'Authorization': '9f1a7e2e3e91db0ee09ba2325d3207073287db7c'}
# r = requests.get('http://127.0.0.1:5000/get/user', headers=headers)
# print r.status_code, r.headers['content-type'], r.content, r.url

# For testing, performance, benchmarking and integration


def text_generator():
    return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_letters) for x in range(140))


def add_users_messages():

    for i in range(1, 11):
        newuser = {'username': 'user%i' % i, 'password': 'pass45%i' % i, 'email': 'user%i@c.com' % i}
        r = requests.post('http://127.0.0.1:5000/add/user', data=json.dumps(newuser),
                          headers={'content-type': 'application/json'})
        print r.status_code, r.headers['content-type'], r.content, r.url

    for i in range(1, 101):
        newmessage = newuser = {'text': text_generator(),
                                'pub_date': datetime.datetime.isoformat(datetime.datetime.now()),
                                'user_id': random.randrange(1, 11)}
        r = requests.post('http://127.0.0.1:5000/add/message', data=json.dumps(newmessage),
                          headers={'content-type': 'application/json'})


def add_content():
    manager = APIManager(app, flask_sqlalchemy_db=db)

    manager.create_api(User, methods=['GET'],
                       url_prefix='/get',
                       results_per_page=50,
                       include_columns=['id', 'username', 'email', 'messages'],
                       )
    manager.create_api(User, methods=['POST'], url_prefix='/add')
    manager.create_api(Message, methods=['POST'], url_prefix='/add')

    add_users_messages()
    myuser_is = None

    test_followers = (3, 8, 2, 2, 7, 5, 1, 9, 3, 4)
    # followed users = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    # Add users follow relations
    i = 1
    for j in test_followers:
        myuser_is = User.query.filter(User.username == 'user%s' % j).one()
        theuser = User.query.filter(User.username == 'user%s' % i).one()
        i += 1
        u = myuser_is.follow(theuser)
        if u is None:
            print dict(message="You can't follow %s" % theuser.username)
        db.session.add(u)
        db.session.commit()

    # test users follow relations from database
    j = 1
    for i in test_followers:
        flwr = User.query.filter(User.id == i).one()
        flwd = User.query.filter(User.id == j).one()
        j += 1

        db.session.add(u)
        db.session.commit()

#app.config['TESTING'] = True
#app.config['CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:services@127.0.0.1:3306/example'

db.drop_all()
db.create_all()
add_content()

#     #print r.status_code, r.headers['content-type'], r.content, r.url
#
# print socket.gethostname()
# print os.urandom(16)
#
# print make_secure_token("user9", key="deterministic")
#
#
# newuser = {'username': 'user10', 'password': 'pass4510', 'email': 'user10@c.com'}
# r = requests.post('http://127.0.0.1:5000/add/user', data=json.dumps(newuser),
#                   headers={'content-type': 'application/json'})
# print r.status_code, r.headers['content-type'], r.content, r.url


# 201 application/json {
#   "username": "user1",
#   "followed": [],
#   "followers": [],
#   "password": "pass451",
#   "messages": [],
#   "email": "user1@c.com",
#   "id": 1
# } http://127.0.0.1:5000/add/user