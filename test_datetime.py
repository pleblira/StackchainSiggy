from datetime import datetime

tweet_timestamp = str(f"{datetime.timestamp(datetime.now().replace(microsecond=0)):.0f}")

# print(tweet_timestamp)

tweet_datetimeISO = "2022-12-02T00:35:43.000Z"

tweet_datetimeISO = tweet_datetimeISO[0:tweet_datetimeISO.find(".")]

tweet_timestamp = datetime.strptime(tweet_datetimeISO,'%Y-%m-%dT%H:%M:%S')
tweet_timestamp = int(datetime.timestamp(tweet_timestamp))
print(tweet_timestamp)

# ts = datetime.timestamp(iso_format)