__author__ = 'izaac'
import validictory
import json
import requests


# Validator following the http://json-schema.org guidelines using the python validictory library
# This is for integration and acceptance test

schema_following = {
    "type": "object",
    "properties": {
        "user_is_following": {
            "type": "array",
            "items": [
                {"type": "object",
                 "properties": {
                     "username": {"type": "string"},
                     "id": {"type": "integer"}
                 }
                 }
            ]
        }
    }
}

schema_followers = {
    "type": "object",
    "properties": {
        "its_followers": {
            "type": "array",
            "items": [
                {"type": "object",
                 "properties": {
                     "username": {"type": "string"},
                     "id": {"type": "integer"}
                 }
                 }
            ]
        }
    }
}

schema_message = {
    "type": "object",
    "properties": {
        "message": {"type": "string"}
    }
}
# Known validictory module issue about the _data is not of type object
# https://github.com/sunlightlabs/validictory/issues/49
# TODO: Follow up bug for validation/regression
schema_twitt = {
    "type": "object",
    "properties": {
        "messages": {
            "type": "array",
            "items": [
                {"type": "object",
                 "properties": {
                     "text": {"type": "string"},
                     "pub_date": {
                         "type": "array",
                         "items": [
                             {"type": "string"},
                             {"type": "string"}
                         ]
                     }
                 }
                 }
            ]
        }
    }
}


def validate_json():
    headers = {'content-type': 'application/json'}
    #test following
    r = requests.get('http://127.0.0.1:5000/user/user1/following?key=d5ef19c2b1714f87e0042e4f822bf722b30239f7',
                     headers=headers)

    try:
        validictory.validate(r.content, schema_following)
    except ValueError, error:
        print error



########################################################
# /user/<username>/following
# {
#   "its_followers": [
#     {
#       "username": "user8",
#       "id": 8
#     }
#   ]
# }
#json_followers = json.loads('{"its_followers": [{"username": "user8", "id": 8}]}')


########################################################
# Generic json message
# {
#   "message": "<String>"
# }

#json_message = json.loads('{"message": "You can\'t follow user2"}')



########################################################
# /user/<username>
# {
#   "messages": [
#     {
#       "text": "example message",
#       "pub_date": [
#         "2013-05-08",
#         "07:59:13"
#       ],
#       "message_id": 98,
#       "user_id": 3
#     }
# }

#
# dump_twitt = json.dumps('{"messages": [ { "text": "example text", \
#                         "pub_date": ["2013-05-08", "07:59:13" ], \
#                         "message_id": 98, "user_id": 3 }}')
# json_twitt = json.loads(dump_twitt)
#
#
# try:
#     validictory.validate(json_twitt, schema_twitt)
# except ValueError, error:
#     print errro



