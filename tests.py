# -*- coding: utf8 -*-
from coverage import coverage
cov = coverage(branch=True, omit=['templates/*',
                                  'tests.py',
                                  'secure_token_gen.py',
                                  'json_reqs.py',
                                  'models.py'])
cov.start()

import os
import unittest
import random
import json
from string import ascii_letters, ascii_uppercase, digits
from datetime import datetime
from twitty import db, User, Message, app
from flask.ext.restless import APIManager


manager = APIManager(app, flask_sqlalchemy_db=db)
basedir = os.path.abspath(os.path.dirname(__file__))


def text_generator():
    return ''.join(random.choice(ascii_uppercase + digits + ascii_letters) for x in range(140))


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:services@127.0.0.1:3306/tests'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_follow_unfollow(self):

        u1 = User(username='izaac', email='izaac@lambda.com', password='izaac1')
        u2 = User(username='cristina', email='cristina@lambda.com', password='cristina1')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().username == 'cristina'
        assert u2.followers.count() == 1
        assert u2.followers.first().username == 'izaac'
        u = u1.unfollow(u2)
        assert u is not None
        db.session.add(u)
        db.session.commit()
        assert u1.is_following(u2) is False
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_delete_message(self):
        # create a user and a message (twitt)
        text = text_generator()
        u = User(username='izaac1', email='izaac1@lambda.com')
        m = Message(text=text, user_id=u.id, pub_date=datetime.utcnow())
        db.session.add(u)
        db.session.add(m)
        db.session.commit()
        # query the message and destroy the SQLAlchemy session
        m = Message.query.get(1)
        assert m.text == text
        db.session.remove()
        # delete the message using a new SQLAlchemy session
        db.session = db.create_scoped_session()
        db.session.delete(m)
        db.session.commit()

    def test_db_content(self):

        manager.create_api(User, methods=['GET'],
                           url_prefix='/get',
                           results_per_page=50,
                           include_columns=['id', 'username', 'email', 'messages'],
                           )
        manager.create_api(User, methods=['POST'], url_prefix='/add')
        manager.create_api(Message, methods=['POST'], url_prefix='/add')
        headers = {'content-type': 'application/json'}
        for i in range(1, 11):
            newuser = {'username': 'user%i' % i,
                       'password': 'pass45%i' % i,
                       'email': 'user%i@c.com' % i}
            r = self.app.post('/add/user', data=json.dumps(newuser), headers=headers)
            self.assertEqual(r.status_code, 201)

        for i in range(1, 101):
            newmessage = {'text': text_generator(),
                          'pub_date': datetime.isoformat(datetime.now()),
                          'user_id': random.randrange(1, 11)}
            r = self.app.post('/add/message', data=json.dumps(newmessage),
                              headers=headers)
            self.assertEqual(r.status_code, 201)

        self.db_relationships()

    def db_relationships(self):
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
            # the actual test
            assert flwr.is_following(flwd) is True


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print "\n\nCoverage Report:\n"
    cov.report()
    print "\nHTML version: " + os.path.join(basedir, "tmp/coverage/index.html")
    cov.html_report(directory='tmp/coverage')
    cov.erase()