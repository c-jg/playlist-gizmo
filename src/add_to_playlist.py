def req_callback(request_id, response, exception):
    '''
    Callback for batch request.
    '''

    global videos_added
    if exception is None:
        videos_added += 1
        print("ok")


def add_to_playlist(youtube, playlist_id, videos):
    '''
    Adds YouTube video(s) to a playlist.

    Args:
        youtube: YouTube API build.
        playlist_id: Playlist ID to add videos to.
        videos: List of video IDs.
    '''
    
    batch = youtube.new_batch_http_request()

    for video in videos:
        batch.add(
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                    "playlistId": playlist_id,
                    "position": 0,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video
                    }
                    }
                }
            ), callback=req_callback
        )

    batch.execute()
    
    print(f"{videos_added} videos added to playlist https://www.youtube.com/playlist?list={playlist_id}")


videos_added = 0
