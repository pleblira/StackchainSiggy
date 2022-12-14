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
from store_stackjoin import *
from stackjoin_add import *
import time

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")

throttle_time = 60

def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?expansions=author_id,attachments.media_keys&media.fields=url", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code == 429:
        print("ran into error 429 so waiting for 60 seconds for connection to be reset")
        time.sleep(60)
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    if response.status_code != 200 and response.status_code != 429:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(f"\n\n\n\n\n--- --- --- INCOMING TWEET --- --- ---\n")
            print(f"the json dumps for json_response {json.dumps(json_response,indent=4)}\n\n")
            # checking if it's a stackjoin to store it
            if "#stackjoin" in json_response['data']['text'].lower() and "#stackjoinadd" not in json_response['data']['text'].lower():
                print("found #stackjoin on tweet, activating store_stackjoin function")
                store_stackjoin(json_response,tweet_datetimeISO=None)
            else:
                print("didn't find #stackjoin on tweet, so not activating the store_stackjoin function")
            tweet_id = json_response["data"]["id"]
            if "#stackjoinadd" in json_response['data']['text'].lower():
                print("found #stackjoinadd on tweet, activating stackjoin_add function")
                json_response_from_stackjoinadd = stackjoin_add(tweet_id)
                if json_response_from_stackjoinadd != None:
                    store_stackjoin(json_response_from_stackjoinadd[0],json_response_from_stackjoinadd[1],json_response_from_stackjoinadd[2], json_response_from_stackjoinadd[3])
            else:
                print("didn't find #stackjoinadd on tweet, so not activating the stackjoin_add function")
            throttle_list = create_throttle_list(throttle_time)
            # print(f"json dumps for get_stream: {json.dumps(json_response, indent=4, sort_keys=True)}")
            tweet_message = json_response["data"]["text"]
            # tweets have been disabled and bot has been operating silently. Disabled function below so it doesn't have to access AWS to pull tweet message list every time
            # tweet_message = get_tweet_message(json_response, tweet_message)
            # print(tweet_message)

            tweet_y = False
            tweet_n = False

            while not tweet_y and not tweet_n:
                # additional check for hashtag on text of the tweet (the API has been serving replies to the actual hashtag tweet, which does not apply)
                if "#stackchain" not in json_response['data']['text'].lower() and "#stackchaintip" not in json_response['data']['text'].lower() and "#stackjoin" not in json_response['data']['text'].lower() and "#pbstack" not in json_response['data']['text'].lower() and "#stackjoinadd" not in json_response['data']['text'].lower():
                    print("switching tweet_n to True since text doesn't contain hashtags")
                    tweet_n = True
                # set tweet_n to True if no attachments on tweet
                # if json_response['data']['attachments'] == {}:
                #     tweet_n = True
                if json_response['data']['author_id'] == "1419655667112108032":
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
                if "#stackjoin" not in json_response['data']['text'].lower():
                    tweet_n = True
            if tweet_y == True:
                if "#stackjoin" in json_response['data']['text'].lower():
                    # tweets have been disabled and bot has been operating silently. Disabled get_tweets function so it doesn't have to access AWS to pull tweet message list every time. If to reactivate tweeting, need to reactivate get_tweets function
                    # print("tweet has been disabled for now")
                    print("tweet will go out")
                    tweet_message = "???? Stackjoin Recorded to the Mempool ??????"
                    tweepy_send_tweet(tweet_message, tweet_id, json_response)
                # tweepy_send_tweet(tweet_message,tweet_id, json_response)
                clean_up_and_save_recent_interactions(json_response, throttle_time)
            else:
                print("tweet won't go out and cleaning up recent interactions was skipped")
                print("tweet replies for hashtags besides #stackjoin and #stackjoinadd have been disabled for now")


def main():
    rules = get_rules(bearer_oauth)
    delete_all_rules(rules, bearer_oauth)
    set = set_rules(bearer_oauth)
    get_stream(set)

if __name__ == "__main__":
    main()
    # clean_up_and_save_recent_interactions(json_response)