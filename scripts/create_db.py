from pymongo import Connection

import base64
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

BUSINESS = [(1, 'Hair Studio 919', 'styling919'), (2, 'Mike\'s Auto Shop', 'mikeshop')]
SCHEDULE = {1: INITIAL_SCHEDULE, 
            2: INITIAL_SCHEDULE
           }

if __name__ == "__main__":
	conn = Connection()
	db = conn['procrastinate']
	
    # Create business w/ schedules
	collection = db['business']
	collection.ensure_index('username', unique=True)
    
    # Build document
	for id, name, username in BUSINESS:
		schedule = SCHEDULE[id]
		if id == 2: # for business #2, open up two appointments
			schedule['09:00'] = "OPEN"
			schedule['11:30'] = "OPEN"
			schedule['16:30'] = "OPEN"
			

		doc = ({"id": id, 
                "name": name,
                "schedule": schedule,
				"username": username,
				"password": base64.b64encode("password")
              })
		collection.insert(doc)
