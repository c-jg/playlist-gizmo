import pandas as pd
import argparse
import os
import sys

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from watch_later_html import use_local_file


def get_videos(youtube, data, playlistId, token=None):
    '''
    Fetches all video data from a playlist using YouTube Data API.
    Saves title, channel, url, date published, and thumbnail urls for each video.
    '''

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlistId,
        maxResults=50,
        pageToken=token
    )
    response = request.execute()

    for video in response['items']:
        snippet = video["snippet"]

        if snippet["title"] == "Deleted video":
            continue 

        data["Title"].append(snippet["title"])
        data["Channel"].append(snippet["videoOwnerChannelTitle"])
        data["URL"].append("https://www.youtube.com/watch?v=" + snippet["resourceId"]["videoId"])
        data["Published At"].append(snippet["publishedAt"])

        if snippet["thumbnails"]:
            data["Thumbnail"].append(snippet["thumbnails"]["default"]["url"])
        else:
            data["Thumbnail"].append(None)

    if "nextPageToken" in response:
        return get_videos(youtube=youtube, data=data, playlistId=playlistId, 
            token=response["nextPageToken"])
    else:
        return data


def save_data(data):
    df = pd.DataFrame(data)
    num_vids = len(df.index)

    if FLAGS.no_save:
        print(df)
        print(f"Found {num_vids} videos.")
    else:
        df.to_csv(FLAGS.save_path)
        print(f"Saved playlist data ({num_vids} videos) =====> " + FLAGS.save_path)


def main():
    if FLAGS.playlist_url:
        scopes = ["https://www.googleapis.com/auth/youtube"]
        # create empty dict to store data
        data = {
            "Title": [],
            "Channel": [],
            "URL": [],
            "Published At": [],
            "Thumbnail": []
        }
        
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # set up YouTube API call
        api_service_name = "youtube"
        api_version = "v3"

        if FLAGS.public:
            # Build using only API key
            # No user authentication
            DEVELOPER_KEY = os.environ.get("YT_DEV_KEY")

            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=DEVELOPER_KEY)
        else:
            # Get credentials and create an API client
            client_secrets_file = "client_secrets.json"

            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            credentials = flow.run_console()

            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, credentials=credentials)

        # get data on each video in playlist
        url = FLAGS.playlist_url.split('playlist?list=')[-1]
        save_data(get_videos(youtube=youtube, data=data, playlistId=url))
    elif FLAGS.local_file:
        save_data(use_local_file(FLAGS=FLAGS))
    else:    
        raise ValueError("No playlist entered.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--playlist_url',
        type=str,
        help='Full YouTube URL of playlist.'
    )
    parser.add_argument(
        '--save_path',
        type=str,
        default='playlist_videos.csv',
        help='File to save the playlist data to.'
    )
    parser.add_argument(
        '--local_file',
        type=str,
        help='HTML file of playlist.'
    )
    parser.add_argument(
        '--no_save',
        type=bool,
        nargs='?',
        const=True,
        default=False,
        help="Prevents saving data to file, prints instead."
    )
    parser.add_argument(
        '--public',
        type=bool,
        nargs='?',
        const=True,
        default=False,
        help="Disables user authentication. Only usable for exporting/printing public playlists"
    )

    FLAGS, unparsed = parser.parse_known_args()
    main()
    