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

    return data