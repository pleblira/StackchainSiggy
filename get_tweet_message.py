import boto3
from dotenv import load_dotenv, find_dotenv
import os
import json
import random

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# def get_tweet_message(json_response,tweet_message):
#     if "#stackchaintip" in json_response['data']['text'].lower():
#         tweet_message = "Fetching the tip is my favorite!!!\nIf I ever lose the tip I get sad. But I can usually find it @StackchainSig"
#     elif "#stackchain" in json_response['data']['text'].lower():
#         tweet_message = "Hello friend! I'm so happy to see you!! Come hang out with Stackchainers at @StackchainSig"
#     elif "#stackjoin" in json_response['data']['text'].lower():
#         tweet_message = "I see your stackjoin!!! I’m gonna go tell the Mempool operators about it!!!"
#     return tweet_message

def get_tweet_message(json_response,tweet_message):
    # tweets_json_filename = "stackjoin.json"
    if "#stackchaintip" in json_response['data']['text'].lower():
        tweets_json_filename = "stackchaintip.json"
    #     # tweet_message = "Fetching the tip is my favorite!!!\nIf I ever lose the tip I get sad. But I can usually find it @StackchainSig"
    elif "#stackchain" in json_response['data']['text'].lower():
        tweets_json_filename = "stackchain.json"
    #     # tweet_message = "Hello friend! I'm so happy to see you!! Come hang out with Stackchainers at @StackchainSig"
    elif "#stackjoin" in json_response['data']['text'].lower():
        tweets_json_filename = "stackjoin.json"
    #     tweet_message = "I see your stackjoin!!! I’m gonna go tell the Mempool operators about it!!!"
    # downloading tweet list from S3 bucket
    boto3.client('s3').download_file('pleblira', tweets_json_filename, 'assets/' + tweets_json_filename)

    # with open('assets/' + tweets_json_filename, 'r+') as openfile:
    with open('assets/stackjoin.json', 'r') as openfile:
        tweet_list = json.load(openfile)
        tweet_message = tweet_list[random.randint(0,len(tweet_list)-1)]['tweet_text']
    return tweet_message

# if __name__ == '__main__':
#     get_tweet_message("a","a")

