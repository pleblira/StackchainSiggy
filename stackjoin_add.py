import requests
import os
import json
from dotenv import load_dotenv, find_dotenv
import webbrowser
from datetime import datetime
from remove_mentions_from_tweet_message import *


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")


def create_url(tweet_id):
    tweet_fields = "tweet.fields=referenced_tweets,attachments,author_id,created_at,entities,id,text&media.fields=preview_image_url,url&expansions=attachments.media_keys,author_id"
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    ids = "ids="+tweet_id
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs
    url = "https://api.twitter.com/2/tweets?{}&{}".format(ids, tweet_fields)
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def stackjoin_add(tweet_id):
    url = create_url(tweet_id)
    json_response_from_reply = connect_to_endpoint(url)
    for user in json_response_from_reply['includes']['users']:
        if user['id'] == json_response_from_reply['data'][0]['author_id']:
            stackjoinadd_reporter = " [stackjoinadd_reporter: "
            stackjoinadd_reporter += user['username']
            stackjoinadd_reporter += " - ID "+user['id']
    tweet_id_to_stackjoinadd = "1110302988"
    # print(json.dumps(json_response_from_reply, indent=4, sort_keys=True))
    stackjoinadd_tweet_message = " - message: "
    stackjoinadd_tweet_message += remove_mentions_from_tweet_message(json_response_from_reply['data'][0]['text'])
    # print(stackjoinadd_tweet_message)
    # print(json_response_from_reply['data'][0]['referenced_tweets'][0]['id'])
    if 'referenced_tweets' not in json_response_from_reply['data'][0]:
        return None
    for item in json_response_from_reply['data'][0]['referenced_tweets']:
        if item['type'] == "replied_to":
            tweet_id_to_stackjoinadd = item['id']
    # webbrowser.open('https://twitter.com/halfin/status/'+tweet_id_to_add_to_mempool)
    # return gif_url
    json_response_from_tweet_to_stackjoinadd = connect_to_endpoint(create_url(tweet_id_to_stackjoinadd))
    # print(json.dumps(json_response_from_tweet_to_stackjoinadd, indent=4, sort_keys=True))
    # print("\n\n\n")
    rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function = {}
    rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data'] = json_response_from_tweet_to_stackjoinadd['data'][0]
    rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['includes'] = json_response_from_tweet_to_stackjoinadd['includes']
    # print(json.dumps(rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function, indent=4, sort_keys=True))
    # print(json.dumps(json_response_from_tweet_to_stackjoinadd, indent=4, sort_keys=True))
    tweet_datetimeISO = rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data']['created_at']
    tweet_datetimeISO = tweet_datetimeISO[0:tweet_datetimeISO.find(".")]
    print (stackjoinadd_reporter)
    return rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function, tweet_datetimeISO, stackjoinadd_reporter, stackjoinadd_tweet_message

if __name__ == "__main__":
    stackjoin_add("1600692890807971840")
    # stackjoin_add("1598477437813260288")

