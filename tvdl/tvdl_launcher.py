import tvdl.src.twitter_video_dl.twitter_video_dl as tvdl
# import argparse

# if __name__ == "__main__":
def twitter_video_dl_launcher(twitter_url, file_name):
    # parser = argparse.ArgumentParser(
    #     description="Download a video from a twitter url and save it as a local mp4 file."
    # )

    # parser.add_argument(
    #     "twitter_url",
    #     type=str,
    #     help="Twitter URL to download.  e.g. https://twitter.com/GOTGTheGame/status/1451361961782906889"
    # )

    # parser.add_argument(
    #     "file_name",
    #     type=str,
    #     help="Save twitter video to this filename. e.g. twittervid.mp4"
    # )

    # args = parser.parse_args()

    file_name = file_name if file_name.endswith(".mp4") else file_name + ".mp4"

    print("launching from tvdl folder")
    tvdl.download_video(twitter_url, file_name)