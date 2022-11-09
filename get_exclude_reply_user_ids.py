import os

def get_exclude_reply_user_ids(json_response):
    exclude_reply_user_ids = []
    for item in json_response['includes']['users']:
        # print(json_response['data']['author_id'])
        if item['id'] != json_response['data']['author_id']:
            exclude_reply_user_ids.append(item['id'])
    if exclude_reply_user_ids == []:
        exclude_reply_user_ids = None
    else:
        exclude_reply_user_ids = ",".join(exclude_reply_user_ids)
    return exclude_reply_user_ids