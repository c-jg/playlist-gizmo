import argparse
import os
import sys

import pandas as pd

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from playlist import Playlist
from watch_later_html import use_local_file
from create_playlist import create_playlist


def save_data(data):
    '''
    Handles output of data dictionary by converting to dataframe and
    either printing or saving to .csv file.
    '''

    df = pd.DataFrame(data)
    num_vids = len(df.index)

    if FLAGS.no_save:
        print(df)
        print(f"Found {num_vids} videos.")
    else:
        df.to_csv(FLAGS.save_path)
        print(f"Saved playlist data ({num_vids} videos) =====> " + FLAGS.save_path)


def build_youtube(auth):
    '''
    Connects to YouTube Data API.

    Uses OAuth 2.0 if auth=True
    '''

    scopes = ["https://www.googleapis.com/auth/youtube"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # variables for YouTube API
    api_service_name = "youtube"
    api_version = "v3"

    if auth:
        client_secrets_file = "client_secrets.json"

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
    else:
        DEVELOPER_KEY = os.environ.get("YT_DEV_KEY")

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)
    
    return youtube 


def main():

    if FLAGS.local_wl:
        # export or print Watch Later playlist from local HTML file 
        return save_data(use_local_file(FLAGS=FLAGS))
    
    if FLAGS.move:
        if FLAGS.move.endswith(".csv"):
            df = pd.read_csv(FLAGS.move)
            urls = df["URL"].str.split("=").str[1]

            print("\nAUTHORIZE DESTINATION ACCOUNT:")
            destination = Playlist(playlist_id=FLAGS.to, youtube=build_youtube(auth=True))
            
            # add videos to destination playlist
            return destination.add_videos(urls)
        else:
            print("\nAUTHORIZE ORIGIN ACCOUNT:")
            origin = Playlist(playlist_id=FLAGS.move, youtube=build_youtube(auth=True))
            origin.fetch_videos()

            print("\nAUTHORIZE DESTINATION ACCOUNT:")
            destination = Playlist(playlist_id=FLAGS.to, youtube=build_youtube(auth=True))

            # add videos to destination playlist 
            return destination.add_videos(origin.get_video_ids())

    if FLAGS.public:
        # Build using only API key - no user authentication
        youtube = build_youtube(auth=False)
    else:
        # Get credentials and set up API
        youtube = build_youtube(auth=True)

    if FLAGS.create_playlist:
        # create new playlist 
        create_playlist(youtube, FLAGS.create_playlist, FLAGS.description)

    if FLAGS.export_videos:
        # get data on each video in playlist
        exp_playlist = Playlist(playlist_id=FLAGS.export_videos, youtube=youtube)
        save_data(data=exp_playlist.export_videos())


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
        '--local_wl',
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
    parser.add_argument(
        '--move',
        type=str,
        help='Playlist URL of playlist to transfer.'
    )
    parser.add_argument(
        '--to',
        type=str,
        help='Playlist URL of desired destination.'
    )

    FLAGS, unparsed = parser.parse_known_args()
    if len(sys.argv) > 1:
        main()
    else:
        print("No arguments entered.")
    