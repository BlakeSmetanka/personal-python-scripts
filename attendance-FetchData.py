import copy
from datetime import datetime
import json
import time
import urllib3

def fetch_data():
    
    # Initialize HTTP client
    http = urllib3.PoolManager()
    
    # Make request and format response
    r = http.request('GET', 'https://tmi.twitch.tv/group/user/mizkif/chatters')
    response = json.loads(r.data)
    
    # Retrieve chatter information
    chatters = response['chatters']
    chatter_count = int(response['chatter_count'])
    
    # Leave early if the broadcaster is absent
    if len(chatters['broadcaster']) == 0:
        print ('Streamer offline, not leaving early though.')
    
    # Parse the data and get the current chatters
    chatter_list = formatChatterList(chatters, chatter_count)
    
    # Chatters who were here 2 minutes previously
    previous_chatters = {}
    with open('./attendance-app/attendance-app-previous-chatters.json', 'r') as file:
        previous_chatters = json.loads(file.read())
    
    # Update the temporary list
    with open('attendance-app/attendance-app-previous-chatters.json', 'w') as file:
        file.write(json.dumps(chatters))
    
    # Load the previous time totals
    previous_times = {}
    with open('attendance-app/attendance-app-time-totals.json', 'r') as file:
        previous_times = json.loads(file.read())
    
    newest_list = copy.deepcopy(previous_times)
    
    for chatter in chatter_list:
        if not chatter in previous_times:
            # Insert a new chatter with 2 minutes
            newest_list[chatter] = {
                'role': chatter_list[chatter]['role'],
                'total_minutes': 2
            }
        else:
            # Increment the existing time
            newest_list[chatter]['total_minutes'] = newest_list[chatter]['total_minutes'] + 2
    
    with open('attendance-app/attendance-app-time-totals.json', 'w') as file:
        file.write(json.dumps(newest_list))

    return True

def formatChatterList(chatters, chatter_count):
    
    broadcaster = chatters['broadcaster']
    vips = chatters['vips']
    moderators = chatters['moderators']
    staff = chatters['staff']
    admins = chatters['admins']
    global_mods = chatters['global_mods']
    viewers = chatters['viewers']
    
    print('Chatters: ' + str(chatter_count))
    if(len(broadcaster) > 0):
        print('Broadcaster: ' + broadcaster[0])
    
    batch_list = {}
    for chatter in broadcaster:
        batch_list[chatter]= {'role': 'broadcaster'}
        
    for chatter in vips:
        batch_list[chatter]= {'role': 'vip'}
    
    for chatter in moderators:
        batch_list[chatter]= {'role': 'moderator'}
    
    for chatter in staff:
        batch_list[chatter]= {'role': 'staff'}
    
    for chatter in admins:
        batch_list[chatter]= {'role': 'admin'}
    
    for chatter in global_mods:
        batch_list[chatter]= {'role': 'global_mod'}
    
    for chatter in viewers:
        batch_list[chatter]= {'role': 'viewer'}
    
    return batch_list

startup_time = datetime.now()
startup_minutes = startup_time.minute
startup_seconds = startup_time.second

startup_minutes_until_update = 1 - startup_minutes % 2
startup_seconds_until_update = 60 - startup_seconds

startup_seconds_to_sleep = startup_minutes_until_update * 60 + startup_seconds_until_update

print('WELCOME AT ' + startup_time.strftime("%H:%M:%S") + '. WILL BEGIN ON THE NEXT EVEN MINUTE, SLEEPING ' + str(startup_seconds_to_sleep) + ' SECONDS...')

time.sleep(startup_seconds_to_sleep)

# Count for developer to read in console
count = 1
while True:
    print('-------- TIME: ' + datetime.now().strftime("%H:%M:%S") + ' --------')
    print('BEGIN LOOP ' + str(count))
    fetch_data()

    # TODO: Evaluate the current time
    current_time = datetime.now()
    current_minutes = current_time.minute
    current_seconds = current_time.second

    minutes_until_update = 1 - current_minutes % 2
    seconds_until_update = 60 - current_seconds

    seconds_to_sleep = minutes_until_update * 60 + seconds_until_update

    print('END LOOP ' + str(count) + ' AT ' + current_time.strftime("%H:%M:%S") + '. SLEEPING ' + str(seconds_to_sleep) + ' SECONDS...')

    time.sleep(seconds_to_sleep)
    count = count + 1