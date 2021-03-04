def create_playlist(youtube, title, description):
    '''
    Creates an empty playlist on authenticated user's channel.
    Authenticated user must have a YouTube channel, otherwise
    the operation will fail.
    '''

    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )

    response = request.execute()

    print(response)

    print(f"\nPlaylist `{title}` has been created.")