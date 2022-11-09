from datetime import datetime, timedelta
import json


def clean_up_and_save_recent_interactions(json_response, throttle_time):
    recent_interactions_cleaned_up = []
    with open('recent_interactions.json', 'r+') as openfile:
        recent_interactions = json.load(openfile)
        for item in recent_interactions:
            if item['tweetdatetime'] > int(datetime.timestamp(datetime.now().replace(microsecond=0)))-throttle_time:
                recent_interactions_cleaned_up.append(item)
        print("this is recent interactions cleaned up without the current tweet")
        print(recent_interactions_cleaned_up)
    with open('recent_interactions.json', 'w') as openfile:
        recent_interactions_cleaned_up.append({
            "userid":json_response['data']['author_id'],
            "tweetdatetime":int(datetime.timestamp(datetime.now().replace(microsecond=0))),
            "tweetdatetimeISO":datetime.utcnow().isoformat()
            })
        print(f"\nthese are the recent interactions: {recent_interactions_cleaned_up}\n")
        openfile.write(json.dumps(recent_interactions_cleaned_up, indent=4))
