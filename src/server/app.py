#!flask/bin/python
from flask import Flask, request, abort
from pymongo import Connection
from bson import json_util

import copy
import json

app = Flask(__name__)
conn = Connection()
db = conn['procrastinate']

@app.route('/api/v1.0/login', methods = ['GET'])
def login():
	if not request.args or not 'username' in request.args or not 'password' in request.args:
		abort(400)
	collection = db['business']
	try:
		user = list(collection.find({"username": request.args['username']}, {"_id": 0})).pop()
	except IndexError:
		abort(401)	

	if not user['password'] == request.args['password']:
		abort(401)

	rtn = copy.deepcopy(user)
	# pop off password field
	del rtn['password']
	return json.dumps(rtn), 201

@app.route('/api/v1.0/business', methods = ['GET'])
def get_biz():
	collection = db['business']
	documents = list(collection.find({}, {"_id": 0}))
	return json.dumps(documents)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug = True)
