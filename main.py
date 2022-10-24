import tweepy
import os
from dotenv import load_dotenv, find_dotenv
import requests
import json
from datetime import datetime, timedelta


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")

throttle_time = 120

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    # print(r)
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    # print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(f"json dumps for delete_all_rules: {json.dumps(response.json())}\n\n")


def set_rules():
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "((#stackchain OR #stackchaintip OR #stackjoin) -from:fewBOT21 -is:retweet)"},
        # {"value": "(@fewBOT21 -from:fewBOT21 -is:retweet)"},
    ]
    payload = {"add": sample_rules}
    print(f"payload is {payload}\n\n")
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(f"json dumps for set_rules: {json.dumps(response.json())}\n\n")

def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?expansions=author_id", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(f"the json dumps for json_response {json.dumps(json_response,indent=4)}\n\n")
            throttle_list = create_throttle_list()
            # print(f"json dumps for get_stream: {json.dumps(json_response, indent=4, sort_keys=True)}")
            tweet_message = json_response["data"]["text"]
            if tweet_message.strip()[0:len(tweet_message)-9] == (tweet_message.strip()[0:tweet_message.lower().find("@fewbot21")-8]):
                tweet_message = "Few"
            else:
                tweet_message = tweet_message[tweet_message.lower().find("@fewbot21")+10:]
                replace_dictionary = {"?":"",",":"",":":"","!":"","you":"I",".":""}
                for element_to_replace in replace_dictionary:
                    tweet_message = tweet_message.replace(element_to_replace,replace_dictionary[element_to_replace])
                tweet_message = tweet_message.strip() + "?\n\nFew"
            tweet_id = json_response["data"]["id"]
            # Making all replies "Few" or something else
            # tweet_message = "Few"
            tweet_message = "Acknowledged by Stackchain bot ✅ (proof of concept)"
            print(tweet_message)

            tweet_y = False
            tweet_n = False

            while not tweet_y and not tweet_n:
                if throttle_list == []:
                    print("throttle_list is blank so tweet == true")
                    tweet_y = True
                for throttle_item in throttle_list:
                    print(f"\nthis is an item from throttle_list: {throttle_item}")
                    if json_response['data']['author_id'] in throttle_item:
                    # if item['id'] in throttle_item:
                        print(f"the item id is {json_response['data']['author_id']}")
                        # print(f"the throttle list is {throttle_list}")
                        print("item found in throttle list, don't tweet")
                        tweet_n = True
                    else:
                        print(f"the item id is {json_response['data']['author_id']}")
                        # print(f"the item id is {item['id']}")
                        # print(f"the throttle list is {throttle_list}")
                        print("not found in throttle list")
                if not tweet_n:
                    tweet_y = True
                print(f"tweet_y: {tweet_y}, tweet_n: {tweet_n}")
                print("\n")
            if tweet_y == True:
                print("tweet will go out")
                clean_up_and_save_recent_interactions(json_response)
                tweepy_send_tweet(tweet_message,tweet_id, json_response)
            else:
                print("tweet won't go out and cleaning up recent interactions was skipped")
            # save_to_recent_interactions(json_response)

def create_throttle_list():
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

def clean_up_and_save_recent_interactions(json_response):
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



def tweepy_send_tweet(tweet_message,tweet_id, json_response):
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    exclude_reply_user_ids = get_reply_user_ids(json_response)
    api.update_status(tweet_message,in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True, exclude_reply_user_ids = exclude_reply_user_ids)

def get_reply_user_ids(json_response):
    exclude_reply_user_ids = []
    for item in json_response['includes']['users']:
        print(json_response['data']['author_id'])
        if item['id'] != json_response['data']['author_id']:
            exclude_reply_user_ids.append(item['id'])
    if exclude_reply_user_ids == []:
        exclude_reply_user_ids = None
    else:
        exclude_reply_user_ids = ",".join(exclude_reply_user_ids)
    return exclude_reply_user_ids


def main():
    rules = get_rules()
    delete_all_rules(rules)
    set = set_rules()
    get_stream(set)

if __name__ == "__main__":
    main()
    # clean_up_and_save_recent_interactions(json_response)