#!flask/bin/python
from flask import Flask
from pymongo import Connection
from bson import json_util

import json

app = Flask(__name__)
conn = Connection()
db = conn['procrastinate']

@app.route('/api/v1.0/business', methods = ['GET'])
def get_biz():
	collection = db['business']
	documents = list(collection.find({}, {"_id": 0}))
	return json.dumps(documents)

if __name__ == '__main__':
    app.run(debug = True)
