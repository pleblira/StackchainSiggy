import json
from datetime import datetime, timedelta

def create_throttle_list(throttle_time):
    throttle_list = []
    with open('recent_interactions.json','r') as openfile:
        recent_interactions = json.load(openfile)
        for item in recent_interactions:
            # print(f"tweetdatetimeISO: {item['tweetdatetimeISO']}")
            # print(f"now timeISO: {datetime.utcnow().isoformat()}")
            if item['tweetdatetime'] > int(datetime.timestamp(datetime.now().replace(microsecond=0)))-throttle_time:
                throttle_list.append({item['userid']})
                # print("tweet less than 5 minutes ago\n")
            # else:
                # print("not from less 5 minutes ago\n")
    # print(f"the throttle list is: {throttle_list}")
    # print(f"the json response is {json_response['includes']['users']['id']}")
    return throttle_list
