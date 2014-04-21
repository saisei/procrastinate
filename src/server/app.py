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

@app.route('/api/v1.0/business', methods = ['GET'])
def get_business():
	collection = db['business'];
	business = list(collection.find({}, {"_id":0}))
	return json.dumps(business), 200

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

@app.route('/api/v1.0/register_apt', methods = ['POST'])
def register_apt():
	if not request.form or not 'id' in request.form or not 'user' in request.form or not 'timeslot' in request.form:
		abort(400)
	collection = db['business_schedule_queue']
	try:
		doc = ({"id": int(request.form['id']),
				"user_id": int(request.form['user']),
				"timeslot": request.form['timeslot']
		})
		collection.insert(doc)
	except Exception as e:
		print "Unknown exception:", e
		abort(400)
	return json.dumps([]), 202

@app.route('/api/v1.0/waitlist', methods = ['POST'])
def waitlist():
	if not request.form or not 'id' in request.form or not 'user' in request.form or not 'state' in request.form:
		abort(400)
	collection = db['client_schedule_queue']
	try:
		doc = ({"id": int(request.form['id']),
				"user_id": int(request.form['user']),
				"state": request.form['state']
		})
		if len(list(collection.find({"id": int(request.form['id']), "user_id": int(request.form['user'])}))) > 0:
			# update
			collection.update({"id": int(request.form['id']), "user_id": int(request.form['user'])}, {"id": int(request.form['id']), "user_id": int(request.form['user']), "state": request.form['state']}, upsert=False)
			conn.fsync()
		else:
			#create
			collection.insert(doc)
	except Exception as e:
		print "Unknown exception:", e
		abort(400)
	return json.dumps([]), 202

@app.route('/api/v1.0/business_queue', methods = ['GET'])
def get_business_queue():
	if not request.args or not 'id' in request.args:
		abort(400)

	try:
		collection = db['business_schedule_queue']
		queue_items = list(collection.find({"id": int(request.args['id'])}, {"_id": 0}))
		# Also lookup names of the items
		collection = db['clients']
		for item in queue_items:
			user_id = item['user_id']
			name = list(collection.find({"id": user_id}, {"_id": 0, "id": 0})).pop()['name']
			item['username'] = name
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
	return json.dumps(queue_items), 200

@app.route('/api/v1.0/client_queue', methods = ['GET'])
def get_client_queue():
	if not request.args or not 'id' in request.args:
		abort(400)

	try:
		collection = db['client_schedule_queue']
		queue_items = list(collection.find({"id": int(request.args['id'])}, {"_id": 0}))
		# Also lookup names of the items
		collection = db['clients']
		for item in queue_items:
			print item
			user_id = item['user_id']
			name = list(collection.find({"id": user_id}, {"_id": 0, "id": 0})).pop()['name']
			item['username'] = name
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
	return json.dumps(queue_items), 200

@app.route('/api/v1.0/set_apt', methods = ['POST'])
def set_apt():
	if not request.form or not 'id' in request.form or not 'user' in request.form or not 'timeslot' in request.form:
		abort(400)
	try:
		collection = db['clients']
		username = list(collection.find({"id": int(request.form['user'])}, {"_id": 0, "id": 0})).pop()['name']

		collection = db['schedule']
		doc = list(collection.find({"id": int(request.form['id'])}, {"_id": 0, "id": 0})).pop()
		schedule = doc['schedule']
		schedule[request.form['timeslot']][0] = username
		schedule[request.form['timeslot']][1] = "CLOSED"
		collection.update({"id": int(request.form['id'])}, {"id": int(request.form['id']), "schedule": schedule}) # this is shitty, there's got to be a way to update the doc without having to set id field again

		# cleanup queue
		collection = db['business_schedule_queue']
		collection.remove({"id": int(request.form['id']), "timeslot": request.form['timeslot']})
	except Exception as e:
		print "Unknown exception:", e
		abort(400)
	return json.dumps([]), 201

@app.route('/api/v1.0/cancel_apt', methods = ['POST'])
def cancel_apt():
	if not request.form or not 'id' in request.form or not 'timeslot' in request.form:
		abort(400)
	try:
		collection = db['schedule']
		doc = list(collection.find({"id": int(request.form['id'])}, {"_id": 0, "id": 0})).pop()
		schedule = doc['schedule']
		schedule[request.form['timeslot']][0] = ""
		schedule[request.form['timeslot']][1] = "OPEN"
		collection.update({"id": int(request.form['id'])}, {"id": int(request.form['id']), "schedule": schedule}) # this is shitty, there's got to be a way to update the doc without having to set id field again
	except Exception as e:
		print "Unknown exception:", e
		abort(400)
	return json.dumps([]), 201

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug = True)
