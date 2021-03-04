import pandas as pd
import argparse
import os
import sys

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from get_videos import get_videos
from watch_later_html import use_local_file
from create_playlist import create_playlist
from add_to_playlist import add_to_playlist


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
    scopes = [
        "https://www.googleapis.com/auth/youtube"
    ]

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

    # variables for YouTube API
    api_service_name = "youtube"
    api_version = "v3"
    
    if FLAGS.public:
        # Build using only API key
        # No user authentication
        DEVELOPER_KEY = os.environ.get("YT_DEV_KEY")

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)
    elif FLAGS.local_file:
        save_data(use_local_file(FLAGS=FLAGS))
    else:
        # Get credentials and create an API client
        client_secrets_file = "client_secrets.json"

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    if FLAGS.create_playlist:
        # create new playlist 
        create_playlist(youtube, FLAGS.create_playlist, FLAGS.description)

    if FLAGS.export_videos:
        # get data on each video in playlist
        playlist_url = FLAGS.export_videos.split('playlist?list=')[-1]
        save_data(get_videos(youtube=youtube, data=data, playlistId=playlist_url))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--export_videos',
        type=str,
        help='Full YouTube URL of playlist.'
    )
    parser.add_argument(
        '--create_playlist',
        type=str,
        help='Title of created playlist.'
    )
    parser.add_argument(
        '--description',
        type=str,
        default='',
        help='Description for created playlist.'
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
        help='HTML file of Watch Later playlist.'
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
        help="Disables user authentication. Only for exporting/printing public playlists"
    )

    FLAGS, unparsed = parser.parse_known_args()
    main()
    