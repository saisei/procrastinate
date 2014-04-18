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

	collection = db['users']
	try:
		user = list(collection.find({"username": request.args['username']}, {"_id": 0})).pop()
	except IndexError:
		print "Cannot find entry in database with username: %s." % request.args['username']
		abort(401)	

	if not user['password'] == request.args['password']:
		abort(401)

	id = user['id']
	if user['type'] == "business":
		collection = db['business']
	else:
		collection = db['clients']

	rtn = list(collection.find({"id": id}, {"_id": 0})).pop() # There's a possibility that pop() will fail if DB is not lined up correctly. In this scenario, wtf...?
	rtn['type'] = user['type'] # Add this back on so UI knows which pane to paint
	return json.dumps(rtn), 200

@app.route('/api/v1.0/schedule', methods = ['GET'])
def get_schedule():
	if not request.args or not 'id' in request.args:
		abort(400)

	collection = db['schedule']
	try:
		schedule = list(collection.find({"id": int(request.args['id'])}, {"_id": 0})).pop()
	except IndexError:
		# WTF? How can this happen?
		print "Cannot find entry in database with id: %s." % request.args['id']
		abort(400) 
	except ValueError:
		print "Converting request field to int failed."
		abort(400)
	except Exception as e:
		print "Unknown exception:", e
		abort(400)
	return json.dumps(schedule), 200

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
