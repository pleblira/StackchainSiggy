import tweepy
import os
from dotenv import load_dotenv, find_dotenv
import requests
import json

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")

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
    # print(f"json dumps for delete_all_rules: {json.dumps(response.json())}")


def set_rules():
    # You can adjust the rules if needed
    sample_rules = [
        # {"value": "(@fewBOT_)", "tag": "fewBOT mention"},
        {"value": "(@fewBOT_ -from:fewBOT_)"},
    ]
    payload = {"add": sample_rules}
    # print(f"payload is {payload}")
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    # print(f"json dumps for set_rules: {json.dumps(response.json())}")

def tweepy_send_tweet(tweet_message,tweet_id):
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    print(tweet_message)
    api = tweepy.API(auth)
    api.update_status(tweet_message,in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)

def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
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
            print(f"json dumps for get_stream: {json.dumps(json_response, indent=4, sort_keys=True)}")
            tweet_message = json_response["data"]["text"]
            tweet_message = tweet_message[tweet_message.lower().find("@fewbot_")+9:]
            replace_dictionary = {"?":"",",":"",":":"","!":"","you":"I"}
            for element_to_replace in replace_dictionary:
                tweet_message = tweet_message.replace(element_to_replace,replace_dictionary[element_to_replace])
            tweet_message = tweet_message + "? Few"
            tweet_id = json_response["data"]["id"]
            tweepy_send_tweet(tweet_message,tweet_id)


def main():
    rules = get_rules()
    delete_all_rules(rules)
    set = set_rules()
    get_stream(set)


if __name__ == "__main__":
    main()