import pandas as pd
import os

import googleapiclient.discovery


def get_videos(token=None):

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId="PLBCF2DAC6FFB574DE",
        pageToken=token
    )
    response = request.execute()

    for video in response['items']:
        snippet = video["snippet"]

        data["Title"].append(snippet["title"])
        data["Video ID"].append(snippet["resourceId"]["videoId"])
        data["Published At"].append(snippet["publishedAt"])

        if snippet["thumbnails"]:
            data["Thumbnail"].append(snippet["thumbnails"]["default"]["url"])
        else:
            data["Thumbnail"].append(None)

    if "nextPageToken" in response:
        return get_videos(token=response["nextPageToken"])


# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyCFWXRyybHEGSra3vmTJxonKBa0yVyk9rg"

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

data = {
    "Title": [],
    "Video ID": [],
    "Published At": [],
    "Thumbnail": []
}

# get data on each video in playlist
get_videos()

df = pd.DataFrame(data)

print(df)
