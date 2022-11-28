import requests
import os
import json
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")


def create_url(tweet_id):
    tweet_fields = "tweet.fields=attachments,author_id,created_at,entities,id,text&media.fields=preview_image_url,url&expansions=attachments.media_keys"
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


def get_tweet_gif_url(tweet_id, media_key, gif_or_video):
    url = create_url(tweet_id)
    json_response = connect_to_endpoint(url)
    for index, item in enumerate(json_response["includes"]["media"]):
        if item['media_key'] == media_key:
            preview_image_url = json_response['includes']['media'][index]['preview_image_url']
            if gif_or_video == "video":
                print(json_response)
                return preview_image_url
            gif_url = 'https://video.twimg.com/tweet_video/'+str(preview_image_url.rsplit('/', 1)[1].split('.', 1)[0])+".mp4"
    print(json_response)
    print(json.dumps(json_response, indent=4, sort_keys=True))
    return gif_url

# if __name__ == "__main__":
#     get_tweet_gif_url("1597118405114744833","7_1597118304434507777","video")

