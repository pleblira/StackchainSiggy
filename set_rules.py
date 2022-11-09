import requests
import json


def set_rules(bearer_oauth):
    sample_rules = [
        {"value": "((#stackchain OR #stackchaintip OR #stackjoin OR #pbstack) -from:stackchainsiggy -is:retweet)"},
        # {"value": "(@fewBOT21 -from:fewBOT21 -is:retweet)"},
    ]
    payload = {"add": sample_rules}
    print(f"payload is {payload}\n\n")
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(f"json dumps for set_rules: {json.dumps(response.json())}\n\n")
