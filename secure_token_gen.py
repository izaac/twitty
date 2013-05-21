__author__ = 'izavaleta'

from flask.ext.login import make_secure_token
import requests
import json

# newuser = {'username': 'user3', 'password': 'pass453', 'email': 'user3@c.com'}
# r = requests.post('http://127.0.0.1:5000/add/user', data=json.dumps(newuser),
#                   headers={'content-type': 'application/json'})

for i in range(1, 11):
    print "User: user%i token: %s " % (i, make_secure_token("user%i" % i, key="deterministic"))
