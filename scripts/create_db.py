from pymongo import Connection

import base64
import copy
import sys

TIME = []
for x in range(9,19):
    for y in ['00', '30']:
        if x < 10:
			TIME.append('0%s:%s' % (x,y))
        else:
            TIME.append('%s:%s' % (x,y))

INITIAL_TIME_STATE = ['CLOSED'] * 20
INITIAL_SCHEDULE=dict(zip(TIME, INITIAL_TIME_STATE))

BUSINESSES = [(1, 'Hair Studio 919', 'styling919'), (2, 'Mike\'s Auto Shop', 'mikeshop')]
CLIENTS = [(1, 'Alex', 'alex'), (2, 'Dave', 'dave'), (3, 'Jay', 'jay'), (4, 'Jenna', 'jenna'), (5, 'Leif', 'leif'), (6, 'Matt', 'matt')]
SCHEDULE = {1: copy.deepcopy(INITIAL_SCHEDULE), 
            2: copy.deepcopy(INITIAL_SCHEDULE)
           }

# Hardcode schedule opening for business #1
SCHEDULE[1]['09:00'] = "OPEN"
SCHEDULE[1]['11:30'] = "OPEN"
SCHEDULE[1]['16:30'] = "OPEN"

if __name__ == "__main__":
	conn = Connection()
	db = conn['procrastinate']
	
    # Create business
	collection = db['business']
	collection.ensure_index('id', unique=True)
    
    # Build document
	for id, name, username in BUSINESSES:
		doc = ({"id": id, 
                "name": name
              })
		collection.insert(doc)

	# Create client
	collection = db['clients']
	collection.ensure_index('id', unique=True)
    
    # Build document
	for id, name, username in CLIENTS:
		doc = ({"id": id, 
                "name": name
              })
		collection.insert(doc)

	# Create users
	collection = db['users']
	collection.ensure_index('username', unique=True)
    
    # Build document
	for id, name, username in BUSINESSES:
		doc = ({"id": id, 
                "username": username,
                "password": base64.b64encode("password")
              })
		collection.insert(doc)
	for id, name, username in CLIENTS:
		doc = ({"id": id, 
                "username": username,
                "password": base64.b64encode(username)
              })
		collection.insert(doc)

	# Create schedule
	collection = db['schedule']
	collection.ensure_index('id', unique=True)
    
    # Build document
	for id, name, username in BUSINESSES:
		schedule = SCHEDULE[id]
		print id, schedule

		doc = ({"id": id, 
                "schedule": schedule
              })
		collection.insert(doc)