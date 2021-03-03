from bs4 import BeautifulSoup as soup
import pandas as pd
import argparse
import os
import sys

import googleapiclient.discovery


def get_videos(youtube, data, playlistId, token=None):
    '''
    Fetches all video data from a playlist using YouTube Data API.
    Saves title, url, date published, and thumbnail urls for each video.
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

        data["Title"].append(snippet["title"])
        data["URL"].append("https://www.youtube.com/watch?v=" + snippet["resourceId"]["videoId"])
        data["Published At"].append(snippet["publishedAt"])

        if snippet["thumbnails"]:
            data["Thumbnail"].append(snippet["thumbnails"]["default"]["url"])
        else:
            data["Thumbnail"].append(None)

    if "nextPageToken" in response:
        return get_videos(youtube=youtube, data=data, playlistId=playlistId, token=response["nextPageToken"])
    else:
        save_data(data)


def local_file():
    '''
    Reads all playlist data in from HTML file.
    Saves video title and url.
    '''
    data = {
        "Title": [],
        "URL": []
    }

    file_name = FLAGS.local_file
    html = soup(open(file_name), "html.parser")
    videos = html.find_all("a", {"id":"video-title"})

    for video in videos:
        data["URL"].append("https://www.youtube.com" + video["href"].split("&list=WL")[0])
        data["Title"].append(video["title"])

    save_data(data)


def save_data(data):
    df = pd.DataFrame(data)

    if FLAGS.no_save:
        print(df)
    else:
        df.to_csv(FLAGS.save_path)


def main():
    if FLAGS.playlist_url:
        # create empty dict to store data
        data = {
            "Title": [],
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
        DEVELOPER_KEY = os.environ.get("YT_DEV_KEY")

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)

        # get data on each video in playlist
        url = FLAGS.playlist_url.split('playlist?list=')[-1]
        get_videos(youtube=youtube, data=data, playlistId=url)
    elif FLAGS.local_file:
        local_file()
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
        help="Prevents saving data to file, prints instead. Overrides --save_path."
    )

    FLAGS, unparsed = parser.parse_known_args()

    main()
    