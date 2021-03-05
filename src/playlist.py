class Playlist:
    def __init__(self, playlist_id, youtube):
        self.playlist_id = playlist_id
        self.youtube = youtube
        self.data = {
            "Title": [],
            "Channel": [],
            "URL": [],
            "Published At": [],
            "Thumbnail": []
        }
        self.videos_added = 0


    def fetch_videos(self, playlist_id, token=None):
        '''
        Fetches all video data from a playlist using YouTube Data API.
        Saves title, channel, url, date published, and thumbnail urls for each video.
        '''
        youtube = self.youtube

        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=token
        )
        response = request.execute()

        for video in response['items']:
            snippet = video["snippet"]

            if snippet["title"] == "Deleted video":
                continue 

            self.data["Title"].append(snippet["title"])
            self.data["Channel"].append(snippet["videoOwnerChannelTitle"])
            self.data["URL"].append(snippet["resourceId"]["videoId"])
            self.data["Published At"].append(snippet["publishedAt"])

            if snippet["thumbnails"]:
                self.data["Thumbnail"].append(snippet["thumbnails"]["default"]["url"])
            else:
                self.data["Thumbnail"].append(None)

        if "nextPageToken" in response:
            return self.fetch_videos(playlist_id=playlist_id, 
                token=response["nextPageToken"])

        return self.data


    def req_callback(self, request_id, response, exception):
        '''
        Callback for batch request.
        '''

        if exception is None:
            self.videos_added += 1
            print("Success")


    def add_videos(self, playlist_id, videos):
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
                        "playlistId": self.playlist_id,
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
        
        print(f"{self.videos_added} videos added to playlist https://www.youtube.com/playlist?list={self.playlist_id}")        


    def export_videos(self):
        '''
        
        '''
        if len(self.data["Title"]) == 0:
            self.fetch_videos(self.playlist_id)
        self.data["URL"] = [f"https://www.youtube.com/watch?v={i}" for i in self.data["URL"]]

        return self.data 


    def get_video_ids(self):
        '''

        '''
        self.video_ids = self.data["URL"]

        return self.videos_ids 


    def get_thumbnails(self):
        '''

        '''
        self.thumbnails = self.data["Thumbnail"]

        return self.thumbnails


    def get_channels(self):
        '''

        '''
        self.channels = self.data["Channel"]

        return self.channels 
