import json
import requests
from get_tweet_gif_url import *
from jinja2 import Template
import boto3

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")


def store_stackjoin(json_response):
    print("running store_stackjoin function")
    # temporarily storing json on a file, it will be later transferred directly through the function, just the two lines below, and indenting the whole function to chnage
    # with open(json_response,'r') as f:
        # json_response = json.load(f)
    tweet_id = json_response["data"]["id"]
    author_id = json_response["data"]["author_id"]
    tweet_message = json_response["data"]["text"]
    for item in json_response['includes']['users']:
        # print (item)
        # print (json_response['data']['author_id'])
        # if ['id'] == json_response['data']['author_id']:
        if item['id'] == '1584380164103872514':
            print (item['id'])
            author_handle = item['username']
    print(f"the author handle is {author_handle}")  
    image_url_dict = []
    img_src_dict = []
    if "media" in json_response["includes"]:
        for index, item in enumerate(json_response['includes']['media']):
            if item['type'] == "animated_gif":
                print('found animated gif')
                image_url = get_tweet_gif_url(tweet_id, "gif")
                print(f"the image URL is {image_url}")
            elif item['type'] == "video":
                print('found video')
                image_url = get_tweet_gif_url(tweet_id, "video")
            else:
                image_url = json_response["includes"]["media"][index]["url"]
                print(f"the image URL is {image_url}")
            r = requests.get(image_url, allow_redirects=True)
            # open("stackjoin_tweets_temp/"+tweet_id+"_image_"+index+1+".jpg",'wb').write(r.content)
            filetype = image_url.rsplit('/', 1)[1].rsplit('.', 1)[1]
            open("stackjoin_tweets_temp/"+tweet_id+"_image_"+str(index+1)+"."+filetype,'wb').write(r.content)
            image_url_dict.append(image_url)
            img_src_dict.append(f"<a href=\"{image_url}\" target=\"_blank\"><img src=\"{image_url}\" style=\"max-width:100px;\"></a>")
            print(image_url_dict)
    else:
        print("no image")
    
    boto3.client('s3').download_file('pleblira', 'stackjoin_tweets/stackjoin_tweets.json', 'stackjoin_tweets/stackjoin_tweets.json')

    with open("stackjoin_tweets/stackjoin_tweets.json",'r+') as openfile:
        try:
            stackjoin_tweets = json.load(openfile)
            print("try")
        except:
            print("except")
            stackjoin_tweets = []
        stackjoin_tweets.append({"tweet_id":tweet_id,"author_handle":author_handle,"author_id":author_id,"tweet_message":tweet_message,"image_url_dict":image_url_dict,"img_src_dict":img_src_dict})
        openfile.seek(0)
        openfile.write(json.dumps(stackjoin_tweets, indent=4))

    s3_upload = boto3.resource(
        's3',
        region_name='us-east-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    content=json.dumps(stackjoin_tweets).encode('utf-8')
    s3_upload.Object('pleblira', 'stackjoin_tweets/stackjoin_tweets.json').put(Body=content,ACL="public-read")


    # turning stackjoin_tweets into html table data
    stackjoin_tweets_table_data = ""
    for index, tweet in enumerate(stackjoin_tweets):
        stackjoin_tweets_table_data += (f"<tr><td>{index+1}</td><td>{tweet[tweet_id]}</td><td>{tweet[author_handle]}</td><td>{tweet[author_id]}</td><td>{tweet[tweet_message]}</td><td>{tweet[image_url_dict]}</td><td>{tweet[str(img_src_dict)].translate({39: None,91: None, 93: None, 44: None})}")
    print(stackjoin_tweets_table_data)
    with open("stackjoin_tweets/stackjoin_tweets_table_data.html",'w') as openfile:
        openfile.write(stackjoin_tweets_table_data)

    with open('stackjoin_tweets/stackjoin_tweets_template.html') as openfile:
        t = Template(openfile.read())
        vals = {"stackjoin_tweets_table_data": stackjoin_tweets_table_data}
    with open('stackjoin_tweets/stackjoin_tweets.html','w') as f:
        f.write(t.render(vals))

    content=t.render(vals)
    s3_upload.Object('pleblira', 'stackjoin_tweets/stackjoin_tweets.html').put(Body=content,ACL="public-read",ContentType='text/html')



# if __name__ == "__main__":
#     store_stackjoin("json_response_with_image.json")




