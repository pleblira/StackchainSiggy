import tweepy
import os
from dotenv import load_dotenv, find_dotenv
import requests
import json
from datetime import datetime, timedelta
from bearer_oauth import *
from get_rules import *
from delete_all_rules import *
from set_rules import *
from create_throttle_list import *
from clean_up_and_save_recent_interactions import *
from get_exclude_reply_user_ids import *
from tweepy_send_tweet import *
from get_tweet_message import *

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")

throttle_time = 20


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
            throttle_list = create_throttle_list(throttle_time)
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
            # tweet_message = "Acknowledged by Stackchain bot ✅ (proof of concept)"
            tweet_message = get_tweet_message(json_response, tweet_message)
            print(tweet_message)

            tweet_y = False
            tweet_n = False

            while not tweet_y and not tweet_n:
                # additional check for hashtag on text of the tweet (the API has been serving replies to the actual hashtag tweet, which does not apply)
                if "#stackchain" not in json_response['data']['text'].lower() and "#stackchaintip" not in json_response['data']['text'].lower() and "#stackjoin" not in json_response['data']['text'].lower():
                    print("switching tweet_n to True since text doesn't contain hashtags")
                    tweet_n = True
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
                        print("not found in throttle list")
                if not tweet_n:
                    tweet_y = True
                print(f"tweet_y: {tweet_y}, tweet_n: {tweet_n}")
                print("\n")
            if tweet_y == True:
                print("tweet will go out")
                clean_up_and_save_recent_interactions(json_response, throttle_time)
                tweepy_send_tweet(tweet_message,tweet_id, json_response)
            else:
                print("tweet won't go out and cleaning up recent interactions was skipped")
            # save_to_recent_interactions(json_response)


def main():
    rules = get_rules(bearer_oauth)
    delete_all_rules(rules, bearer_oauth)
    set = set_rules(bearer_oauth)
    get_stream(set)

if __name__ == "__main__":
    main()
    # clean_up_and_save_recent_interactions(json_response)