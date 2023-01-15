import requests
import json
import re
import urllib.parse
import os

GUEST_TOKEN_ENDPOINT = "https://api.twitter.com/1.1/guest/activate.json"
STATUS_ENDPOINT = "https://twitter.com/i/api/graphql/"

QUOTED_VALUE = re.compile("[\"']([^\"']+)[\"']")
MP4_PART = re.compile("/.+\.mp4|/.+m4s$")
VIDEO_BASE = "https://video.twimg.com"
CONTAINER_PATTERN = re.compile("['\"](http[^'\"]+&container=fmp4)")
MISSING_VARIABLE_PATTERN = re.compile("Query violation: Variable '([^']+)'")
MISSING_FEATURE_PATTERN = re.compile("The following features cannot be null: ([a-zA-Z_0-9, ]+)")
RETRY_COUNT = 5

def send_request(url, session_method, headers):
    response = session_method(url, headers=headers, stream=True)

    response_json = ""
    try:
        response_json = response.json()
    except:
        response_json = "Failed to parse json from response."

    assert response.status_code == 200, f"Failed request to {url}.  {response.status_code} {response_json}.  Please submit an issue including this information."
    result = [line.decode("utf-8") for line in response.iter_lines()]
    return "".join(result)


def exploratory_request(url, method, headers, video_id):
    # find the folder that __file__ is in
    folder = os.path.dirname(__file__)
    request_details_file = os.path.join(folder, "RequestDetails.json")

    # load json from the file
    with open(request_details_file, "r") as f:
        request_details = json.load(f)

    json_features = request_details["features"]
    json_variables = request_details["variables"]
    
    features = urllib.parse.quote_plus(json.dumps(json_features, separators=(',', ':')))
    json_variables["focalTweetId"] = video_id

    variables = urllib.parse.quote_plus(json.dumps(json_variables, separators=(',', ':')))

    status_params = f"TweetDetail?variables={variables}&features={features}"

    response = method(url + status_params, headers=headers)
    result = "".join([line.decode("utf-8") for line in response.iter_lines()])

    if response.status_code == 200:
        return result
    
    for _ in range(RETRY_COUNT):
        missing_vaiables = MISSING_VARIABLE_PATTERN.findall(result)
        missing_features = MISSING_FEATURE_PATTERN.findall(result)

        if missing_features:
            missing_features = missing_features[0].split(", ")

        if missing_vaiables or missing_features:
            for variable in missing_vaiables:
                json_variables[variable] = True
            
            for feature in missing_features:
                json_features[feature] = True

            features = urllib.parse.quote_plus(json.dumps(json_features, separators=(',', ':')))
            variables = urllib.parse.quote_plus(json.dumps(json_variables, separators=(',', ':')))
            status_params = f"TweetDetail?variables={variables}&features={features}"

            response = method(url + status_params, headers=headers)
            result = "".join([line.decode("utf-8") for line in response.iter_lines()])

            # If the second response works then it means the variables or features we added are good.
            if response.status_code == 200:
                # save the updated variables and features
                with open(request_details_file, "w") as f:
                    del json_variables["focalTweetId"]
                    json.dump({"features": json_features, "variables": json_variables}, f, indent=4)

                # It worked - no need for additional retries.
                print(f"Success on retry {_}")
                break

    return result

def search_json(j, target_key, result):
    if type(j) == dict:
        for key, value in j.items():
            if key == target_key:
                if type(value) == list:
                    result.extend(value)
                else:
                    result.append(value)
            search_json(value, target_key, result)

    if type(j) == list:
        for item in j:
            search_json(item, target_key, result)

    return result


def merge_files(f1, f2):
    for line in f2:
        f1.write(line)

    return f1


def download_video_parts(parts, fname):
    with open(fname, "wb") as video_file:
        paths = []
        for part in parts:
            paths.extend(MP4_PART.findall(part))

        for path in paths:
            full_path = f"{VIDEO_BASE}{path}"
            resp = requests.get(full_path, stream=True)
            assert resp.status_code == 200, f"Failed requesting {full_path}.  Please try again or report this as an issue. {resp}"
            merge_files(video_file, resp.raw)


def download_video(video_url, file_name):
    # if file_name ends in .mp4 leave it alone otherwise add .mp4

    video_ids = re.findall("status/([0-9]+)", video_url)

    assert len(video_ids) == 1, f"Did not understand your twitter URL.  Example: https://twitter.com/james_a_rob/status/1451958941886435329"
    video_id = video_ids[0]

    with requests.Session() as session:
        headers = {}

        # One of the js files from original url holds the bearer token and query id.
        container = send_request(video_url, session.get, headers)
        js_files = re.findall("src=['\"]([^'\"()]*js)['\"]", container)

        bearer_token = None
        query_id = None
        # Search the javascript files for a bearer token and TweetDetail queryId
        for f in js_files:
            file_content = send_request(f, session.get, headers)
            bt = re.search(
                '["\'](AAA[a-zA-Z0-9%-]+%[a-zA-Z0-9%-]+)["\']', file_content)

            ops = re.findall('\{queryId:"[a-zA-Z0-9_]+[^\}]+"', file_content)
            query_op = [op for op in ops if "TweetDetail" in op]

            if len(query_op) == 1:
                query_id = re.findall('queryId:"([^"]+)"', query_op[0])[0]

            if bt:
                bearer_token = bt.group(1)

        assert bearer_token, f"Did not find bearer token.  Are you sure you used the right URL? {video_url}"
        assert query_id, f"Did not find query id.  Are you sure you used the right twitter URL? {video_url}"

        headers['authorization'] = f"Bearer {bearer_token}"

        guest_token_resp = send_request(
            GUEST_TOKEN_ENDPOINT, session.post, headers)
        guest_token = json.loads(guest_token_resp)['guest_token']
        assert guest_token, f"Did not find guest token.  Probably means the script is broken.  Please submit an issue.  Include this message in your issue: {video_url}"
        headers['x-guest-token'] = guest_token

        status_resp = exploratory_request(
            f"{STATUS_ENDPOINT}{query_id}/", session.get, headers, video_id)

        status_json = json.loads(status_resp)
        
        legacies = search_json(status_json, "legacy", [])
        legacy = [l for l in legacies if "id_str" in l and l["id_str"] == video_id]

        assert legacy and len(legacy) == 1, f"Did not find video.  Please confirm you are using the correct link.  If your link is correct please report this as an issue including this message.  {video_url}"

        legacy = legacy[0]

        variants = search_json(legacy, "variants", [])
        variants = [v for v in variants if 'bitrate' in v]

        if variants:
            # Find the highest bitrate variant
            variants.sort(key=lambda x: x['bitrate'], reverse=True)
            variant = variants[0]

            video_data = requests.get(variant["url"]).content

            with open(file_name, "wb") as f:
                f.write(video_data)
        else:
            # Some tweets have a "legacy" format that this handles
            container_urls = CONTAINER_PATTERN.findall(status_resp)
            video_containers = []

            for container in container_urls:
                video_details = send_request(container, session.get, headers)
                video_suffixes = re.findall(
                    "(/[a-zA-Z0-9_?\/\.]*=fmp4)", video_details)

                resolutions = []
                for vs in video_suffixes:
                    resolution = re.findall("([0-9]+)x([0-9]+)", vs)[0]
                    resolutions.append((vs, int(resolution[0]) * int(resolution[1])))
                    resolutions.sort(key=lambda x: x[1])

                if len(resolutions) > 0:
                    video_containers.append(resolutions[-1])

            video_containers = set(video_containers)
            assert video_containers, f"Did not find video container.  Probably means the script is broken.  Please submit an issue.  Include this message in your issue: {video_url}"

            if len(video_containers) == 1:
                vc = video_containers.pop()
                parts = send_request(f"{VIDEO_BASE}{vc[0]}", session.get, headers).split("#")

                download_video_parts(
                    parts,
                    file_name
                )
            else:   

                for i, vc in enumerate(video_containers):
                    parts = send_request(f"{VIDEO_BASE}{vc[0]}", session.get, headers).split("#")

                    download_video_parts(
                        parts,
                        f"{i}-{file_name}"
                    )
