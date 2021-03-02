import pandas as pd
import argparse
import os
import sys

import googleapiclient.discovery


def get_videos(playlistId, token=None):

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlistId,
        pageToken=token
    )
    response = request.execute()

    for video in response['items']:
        snippet = video["snippet"]

        data["Title"].append(snippet["title"])
        data["Video ID"].append("https://www.youtube.com/watch?v=" + snippet["resourceId"]["videoId"])
        data["Published At"].append(snippet["publishedAt"])

        if snippet["thumbnails"]:
            data["Thumbnail"].append(snippet["thumbnails"]["default"]["url"])
        else:
            data["Thumbnail"].append(None)

    if "nextPageToken" in response:
        return get_videos(playlistId=playlistId, token=response["nextPageToken"])


if __name__ == '__main__':

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # set up YouTube API call
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get("YT_DEV_KEY")

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    # create empty dict to store data
    data = {
        "Title": [],
        "Video ID": [],
        "Published At": [],
        "Thumbnail": []
    }

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--playlist_url',
        type=str,
        default='',
        help='Full YouTube URL of playlist.'
    )
    parser.add_argument(
        '--save_path',
        type=str,
        default='playlist_videos.csv',
        help='File to save the playlist data to.'
    )

    FLAGS, unparsed = parser.parse_known_args()

    # get data on each video in playlist
    url = FLAGS.playlist_url.split('playlist?list=')[-1]
    get_videos(playlistId=url)

    df = pd.DataFrame(data)

    # save data to CSV file at location specified 
    df.to_csv(FLAGS.save_path)
