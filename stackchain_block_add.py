import requests
import os
import json
from dotenv import load_dotenv, find_dotenv
import webbrowser
from datetime import datetime
from remove_mentions_from_tweet_message import *
import time
from store_stackjoin import *
import webbrowser
import subprocess

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

bearer_token = os.environ.get("BEARER_TOKEN")

# tweet with quote tweet
# tweet_id = "1608877345078738945"
# tweet with image
# tweet_id = "1608874538867228675"
# tweet with multiple images and quoted tweet
# tweet_id = "1608293581336231937"
# last_tweet = "1603441872336306179"
# stackheight 190
# tweet_id = "1549824810993143808"
# stackheight 185 or so
# tweet_id = "1549817095227002881"
# block currently importing
tweet_id = "1549205333272367106"

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

    

def stackchainblockadd(tweet_id, block_height):
    url = create_url(tweet_id)
    json_response_from_reply = connect_to_endpoint(url)
    for user in json_response_from_reply['includes']['users']:
        if user['id'] == json_response_from_reply['data'][0]['author_id']:
            stackjoinadd_reporter = " [stackjoinadd_reporter: "
            stackjoinadd_reporter += user['username']
            stackjoinadd_reporter += " - ID "+user['id']
    # print(json.dumps(json_response_from_reply, indent=4, sort_keys=True))
    stackjoinadd_tweet_message = " - message: "
    stackjoinadd_tweet_message += remove_mentions_from_tweet_message(json_response_from_reply['data'][0]['text'])

    tweet_id_to_stackjoinadd = "1110302988"
    if 'referenced_tweets' not in json_response_from_reply['data'][0]:
        return None
    for item in json_response_from_reply['data'][0]['referenced_tweets']:
        if item['type'] == "replied_to":
            tweet_id_to_stackjoinadd = item['id']

    json_response_from_tweet_to_stackjoinadd = connect_to_endpoint(create_url(tweet_id_to_stackjoinadd))

    # print(json.dumps(json_response_from_tweet_id, indent=4, sort_keys=True))
    
    # for user in json_response_from_tweet_id['includes']['users']:
    #     if user['id'] == json_response_from_tweet_id['data'][0]['author_id']:
    #         author_handle = user['username']
    
    rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function = {}
    rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data'] = json_response_from_tweet_to_stackjoinadd['data'][0]
    rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['includes'] = json_response_from_tweet_to_stackjoinadd['includes']

    # print(json.dumps(json_response_from_tweet_to_stackjoinadd, indent=4, sort_keys=True))
    # print("\n\n\n")
    # print(json.dumps(rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function, indent=4, sort_keys=True))
    # print(json.dumps(json_response_from_tweet_to_stackjoinadd, indent=4, sort_keys=True))
    tweet_datetimeISO = rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data']['created_at']
    tweet_datetimeISO = tweet_datetimeISO[0:tweet_datetimeISO.find(".")]
    # tweet_message = remove_mentions_from_tweet_message(rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data']['text'])
    # print(f"author handle is {author_handle}")
    # printing function
    # with open("tweets.json", 'r+') as f:
    #     try:
    #         print("try")
    #         retrieved_tweets = json.load(f)
    #     except:
    #         print("except")
    #         retrieved_tweets = []
    #     retrieved_tweets.append({"tweet_id":tweet_id, "author_id":json_response_from_tweet_id['data'][0]['author_id'], "author_handle":author_handle, "tweet_datetimeISO":tweet_datetimeISO, "tweet_message":tweet_message})
    #     f.seek(0)
    #     f.write(json.dumps(retrieved_tweets, indent=4))
    
    rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data']['text'] = remove_mentions_from_tweet_message(rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data']['text'])

    # checking if tweet includes quote tweet and downloading quoted tweet
    if "referenced_tweets" in json_response_from_reply["data"][0]:
        for tweet in json_response_from_reply["data"][0]['referenced_tweets']:
            if tweet['type'] == "quoted":
                quoted_tweet_id = tweet['id']
                json_response_from_quoted_tweet = connect_to_endpoint(create_url(quoted_tweet_id))
                quoted_tweet_author_id = json_response_from_quoted_tweet['data'][0]['author_id']
                # print(json.dumps(json_response_from_quoted_tweet,indent=4))
                if "includes" in json_response_from_quoted_tweet:
                    for item in json_response_from_quoted_tweet['includes']['users']:
                        if item['id'] == quoted_tweet_author_id:
                            print (item['id'])
                            quoted_tweet_author_handle = item['username']
                    if 'media' in json_response_from_quoted_tweet['includes']:
                        if 'includes' not in rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function:
                            rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function["includes"]={}
                            rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['includes']['media']=[]
                        if 'media' not in rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['includes']:
                            rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['includes']['media']=[]
                        for media in json_response_from_quoted_tweet['includes']['media']:
                            rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['includes']['media'].append(media)
                            # pass
                quoted_tweet_message = remove_mentions_from_tweet_message(json_response_from_quoted_tweet["data"][0]["text"])
                # quoted_tweet_message = json_response_from_quoted_tweet["data"][0]["text"]
                # print(quoted_tweet_message)
                # print(quoted_tweet_id)
                rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['data']['text'] += ("\n\n[Quoted Tweet:\n@"+ quoted_tweet_author_handle + " - ID " + quoted_tweet_author_id +"\nTweet ID: "+ quoted_tweet_id + "]\n\n"+quoted_tweet_message)

    # print(json.dumps(rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function['includes'],indent=4))

    # store tweets to local drive
    # store_stackjoin_to_local(rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function, tweet_datetimeISO)

    # store tweets to s3 and airtable
    store_stackjoin(rebuilding_dict_to_make_it_compatible_with_store_stackjoin_function, tweet_datetimeISO, block_height_or_tweet_id=block_height)


if __name__ == "__main__":
    download_twitter_conversation(tweet_id)
    # stackjoin_add("1598477437813260288")






