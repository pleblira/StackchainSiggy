import json
import requests
from get_tweet_gif_url import *
from jinja2 import Template
import boto3
from remove_mentions_from_tweet_message import *
from datetime import datetime
import io
from dotenv import load_dotenv, find_dotenv
from pyairtable import Table

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BEARER_TOKEN = os.environ.get("AIRTABLE_BEARER_TOKEN")

def store_stackjoin(json_response, tweet_datetimeISO, stackjoinadd_reporter = "0", stackjoinadd_tweet_message = "", block_height_or_tweet_id="", stackjoin_tweets_or_blocks = "block", dollar_amount=""):
    print("running store_stackjoin function")
    # temporarily storing json on a file, it will be later transferred directly through the function, just the two lines below, and indenting the whole function to chnage
    # with open(json_response,'r') as f:
        # json_response = json.load(f)
    tweet_id = json_response["data"]["id"]
    author_id = json_response["data"]["author_id"]
    tweet_message = remove_mentions_from_tweet_message(json_response["data"]["text"])
    if tweet_datetimeISO == None:
        tweet_datetimeISO = datetime.utcnow().isoformat()
        tweet_datetimeISO = tweet_datetimeISO[0:tweet_datetimeISO.find(".")]
        tweet_timestamp = str(f"{datetime.timestamp(datetime.now().replace(microsecond=0)):.0f}")
    else:
        tweet_timestamp = datetime.strptime(tweet_datetimeISO,'%Y-%m-%dT%H:%M:%S')
        tweet_timestamp = int(datetime.timestamp(tweet_timestamp))
    for item in json_response['includes']['users']:
        # print (item)
        # print (json_response['data']['author_id'])
        # if ['id'] == json_response['data']['author_id']:
        if item['id'] == author_id:
            print (item['id'])
            author_handle = item['username']
    print(f"the author handle is {author_handle}")
    image_url_dict = []
    img_src_dict = []
    airtable_image_files_dict = []
    airtable_gif_files_dict = []
    if "media" in json_response["includes"]:
        for index, item in enumerate(json_response['includes']['media']):
            media_key = item['media_key']
            if item['type'] == "animated_gif":
                print('found animated gif')
                image_url = get_tweet_gif_url(tweet_id, media_key, "gif")
                image_preview_url = get_tweet_gif_url(tweet_id, media_key,  "video")
                print(f"the image URL is {image_url}")
            elif item['type'] == "video":
                print('found video')
                image_url = get_tweet_gif_url(tweet_id, media_key,  "video")
                image_preview_url = get_tweet_gif_url(tweet_id, media_key,  "video")
                tweet_message += " [*Tweet has video attached (videos are unretrievable via API). Open original tweet to access video.]"
            else:
                image_url = json_response["includes"]["media"][index]["url"]
                image_preview_url = image_url
                print(f"the image URL is {image_url}")
            
            #saving tweet images to s3
            if item['type'] == "animated_gif":
                filename = str(index+1)+"_gif"
            else:
                filename = str(index+1)+"_image"
            image_filetype = image_url.rsplit('/', 1)[1].rsplit('.', 1)[1]
            image_preview_filetype = image_preview_url.rsplit('/', 1)[1].rsplit('.', 1)[1]
            s3_upload = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            s3_image_url = 'stackjoin_tweet_images/'+tweet_id+"/"+filename+"."+image_filetype
            s3_image_preview_url = 'stackjoin_tweet_images/'+tweet_id+"/"+filename+"_thumbnail."+image_preview_filetype
            
            # uploading stackjoin image previews to S3 bucket
            print(f"the image preview URL is {image_preview_url}")
            r = requests.get(image_preview_url, allow_redirects=True)
            s3_upload.Object('pleblira',s3_image_preview_url).put(Body=io.BytesIO(r.content), ACL="public-read",ContentType='image/jpeg')

            # uploading stackjoin images to S3 bucket
            print(f"the image URL is {image_url}")
            r = requests.get(image_url, allow_redirects=True)
            s3_upload.Object('pleblira',s3_image_url).put(Body=io.BytesIO(r.content), ACL="public-read",ContentType='image/jpeg')

            # append to image_files_dict for later creating row on Airtable
            if item['type'] == "animated_gif":
                airtable_gif_files_dict.append({"url":image_url,'filename':filename+"."+image_filetype})
            else:
                airtable_image_files_dict.append({"url":image_url,'filename':filename+"."+image_filetype})
       
            # appending url and html tag for embedding to dictionaries which will then be added to the json on S3 and to the html table
            image_url_dict.append(image_url)
            img_src_dict.append(f"<a href=\"/{s3_image_url}\" target=\"_blank\"><img src=\"/{s3_image_preview_url}\" style=\"max-width:100px;\"></a>")
            print(f"the image_url_dict is: {image_url_dict}")
    else:
        print("no image")
    
    # defining airtable_API_import_notes string
    airtable_API_import_notes = ""
    if " [*Tweet has video attached (videos are unretrievable via API). Open original tweet to access video.]" in tweet_message:
        airtable_API_import_notes = "[*Tweet has video attached (videos are unretrievable via API). Open original tweet to access video.]"
    if stackjoinadd_reporter != "0":
        airtable_API_import_notes += stackjoinadd_reporter
    if stackjoinadd_tweet_message != "":
        airtable_API_import_notes += stackjoinadd_tweet_message
    tweet_message_for_airtable_API = tweet_message.replace(" [*Tweet has video attached (videos are unretrievable via API). Open original tweet to access video.]","")

    # creating row or updating row on Airtable
    table = Table(AIRTABLE_API_KEY, "appiNbM9r6Zy7G2ux", stackjoin_tweets_or_blocks)
    if stackjoin_tweets_or_blocks == "blocks":
        stackjoin_tweets_or_blocks = "tblcwUsNLE3AecXpu"
        stackjoin_tweets_or_blocks_filter_term = "block_height"
    else:
        stackjoin_tweets_or_blocks_filter_term = "tweet_id"
        stackjoin_tweets_or_blocks = "tblAHtdeESADDCKGA"
    url = "https://api.airtable.com/v0/appiNbM9r6Zy7G2ux/"+stackjoin_tweets_or_blocks
    if block_height_or_tweet_id == "":
        block_height_or_tweet_id = 21000000
    headers = {"Authorization": "Bearer "+AIRTABLE_BEARER_TOKEN}
    x = requests.get(url, headers=headers, params={'fields[]':[stackjoin_tweets_or_blocks_filter_term], 'filterByFormula':stackjoin_tweets_or_blocks_filter_term+"="+str(block_height_or_tweet_id)}).json()
    # print(json.dumps(x,indent=4))
    print(x)
    if x['records'] == []:
        create_or_update = "create"
    else:
        create_or_update = "update"
        record_id = x['records'][0]['id']

    # checking if block
    if stackjoin_tweets_or_blocks == "tblcwUsNLE3AecXpu": 
        try:
            block_height_or_tweet_id = int(block_height_or_tweet_id.replace("$",""))
        except:
            block_height_or_tweet_id = 21000000
        if create_or_update == "create":
            print('creating')
            table.create({
                "block_height": block_height_or_tweet_id,
                "tweet_id": tweet_id,
                "author_handle": author_handle,
                "author_id": author_id,
                "importing_full_block_message": tweet_message_for_airtable_API,
                "block_summary_image": airtable_image_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "block_timestamp": int(tweet_timestamp),
                "block_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })
        # if updating: 
        elif create_or_update == "update":
            print('updating')
            table = Table(AIRTABLE_API_KEY, 'appiNbM9r6Zy7G2ux', "blocks")
            Table.update(table, record_id=record_id,fields={
                "tweet_id": tweet_id,
                "author_handle": author_handle,
                "author_id": author_id,
                "importing_full_block_message": tweet_message_for_airtable_API,
                "block_summary_image": airtable_image_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "block_timestamp": int(tweet_timestamp),
                "block_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })
    # for stackjoins
    else:
        try:
            dollar_amount = float(dollar_amount.replace("$",""))
            if stackjoinadd_reporter not in "AnthonyDessauer, __overflow_, jc4466, LoKoBTC, BrokenSystem20, pleblira, phathodl, derekmross":
                dollar_amount = 0.0
        except:
            dollar_amount = 0.0
        
        if create_or_update == "create":
            print('creating')
            table.create({
                "tweet_id": tweet_id,
                "dollar_amount": dollar_amount,
                "author_handle": author_handle,
                "author_id": author_id,
                "tweet_message": tweet_message_for_airtable_API,
                "image_files": airtable_image_files_dict,
                "gif_files": airtable_gif_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "tweet_timestamp": int(tweet_timestamp),
                "tweet_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })        # if updating: 
        elif create_or_update == "update":
            print('updating')
            table = Table(AIRTABLE_API_KEY, 'appiNbM9r6Zy7G2ux', "stackjoin_tweets")
            Table.update(table, record_id=record_id,fields={
                "tweet_id": tweet_id,
                "dollar_amount": dollar_amount,
                "author_handle": author_handle,
                "author_id": author_id,
                "tweet_message": tweet_message_for_airtable_API,
                "image_files": airtable_image_files_dict,
                "gif_files": airtable_gif_files_dict,
                "image_url_dict": str(image_url_dict).translate({39: None,91: None, 93: None, 44: None}),
                "tweet_timestamp": int(tweet_timestamp),
                "tweet_datetimeISO": tweet_datetimeISO,
                "img_src_dict": str(img_src_dict).translate({39: None,91: None, 93: None, 44: None}),
                "airtable_API_import_notes": airtable_API_import_notes.strip()
                })

    if stackjoinadd_reporter != "0":
        tweet_message += stackjoinadd_reporter

    #downloading stackjoin_tweets.json from s3 to appen tweet information
    boto3.client('s3').download_file('pleblira', 'stackjoin_tweets/stackjoin_tweets.json', 'stackjoin_tweets/stackjoin_tweets.json')

    with open("stackjoin_tweets/stackjoin_tweets.json",'r+') as openfile:
        try:
            stackjoin_tweets = json.load(openfile)
            print("try")
        except:
            print("except")
            stackjoin_tweets = []
        stackjoin_tweets.append({"tweet_id":tweet_id,"author_handle":author_handle,"author_id":author_id,"tweet_message":tweet_message,"image_url_dict":image_url_dict,"img_src_dict":img_src_dict,"tweet_timestamp":tweet_timestamp,"tweet_datetimeISO":tweet_datetimeISO})
        openfile.seek(0)
        openfile.write(json.dumps(stackjoin_tweets, indent=4))

    # uploading appended json to s3
    s3_upload = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    content=json.dumps(stackjoin_tweets).encode('utf-8')
    s3_upload.Object('pleblira', 'stackjoin_tweets/stackjoin_tweets.json').put(Body=content,ACL="public-read")

    # turning stackjoin_tweets into html table data
    stackjoin_tweets_table_data = ""
    for index, tweet in enumerate(stackjoin_tweets):
        if tweet['image_url_dict'] == []:
            tweet['image_url_dict'] = "no image"
        if tweet['img_src_dict'] == []:
            tweet['img_src_dict'] = "no image"
        if int(datetime.fromtimestamp(int(tweet['tweet_timestamp'])).strftime("%j")) % 2 >0:
            html_row_class = "row-odd-day"
        else:
            html_row_class = "row-even-day"
        stackjoin_tweets_table_data += (f"<tr class=\"{html_row_class}\"><td>{index+1}</td><td><a href=\"https://www.twitter.com/pleblira/status/{tweet['tweet_id']}\" target=\"_blank\">{tweet['tweet_id']}</a></td><td><a href=\"https://twitter.com/{tweet['author_handle']}\" target=\"_blank\">{tweet['author_handle']}</a><br>({tweet['author_id']})</td><td>{tweet['tweet_message']}</td><td>{str(tweet['img_src_dict']).translate({39: None,91: None, 93: None, 44: None})}</td><td style=\"word-break:break-all\">{str(tweet['image_url_dict'])}</td><td>{tweet['tweet_datetimeISO']} <br>({tweet['tweet_timestamp']})</td>")
    # print(stackjoin_tweets_table_data)
    with open("stackjoin_tweets/stackjoin_tweets_table_data.html",'w') as openfile:
        openfile.write(stackjoin_tweets_table_data)

    # updating html template with table data
    with open('stackjoin_tweets/stackjoin_tweets_template.html') as openfile:
        t = Template(openfile.read())
        vals = {"stackjoin_tweets_table_data": stackjoin_tweets_table_data}
    with open('stackjoin_tweets/stackjoin_tweets.html','w') as f:
        f.write(t.render(vals))

    # uploading template to s3
    content=t.render(vals)
    s3_upload.Object('pleblira', 'stackjoin_tweets/stackjoin_tweets.html').put(Body=content,ACL="public-read",ContentType='text/html')



# if __name__ == "__main__":
#     store_stackjoin("json_response_with_image.json")




