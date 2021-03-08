class Playlist:
    def __init__(self, playlist_id, youtube):
        self.playlist_id = playlist_id.split('playlist?list=')[-1]
        self.youtube = youtube
        self.data = {
            "Title": [],
            "Channel": [],
            "URL": [],
            "Published At": [],
            "Thumbnail": []
        }
        self.videos_added = 0


    def fetch_videos(self, token=None):
        '''
        Fetches all video data from a playlist using YouTube Data API.
        Saves title, channel, url, date published, and thumbnail urls for each video.
        '''

        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=self.playlist_id,
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
            return self.fetch_videos(token=response["nextPageToken"])

        return self.data


    def add_videos(self, videos):
        '''
        Adds YouTube video(s) to a playlist.

        Args:
            videos: List of video IDs.
        '''

        for video in videos:
            request = self.youtube.playlistItems().insert(
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
            )
            request.execute()
            self.videos_added += 1
        
        print(f"{self.videos_added} videos added to playlist https://www.youtube.com/playlist?list={self.playlist_id}")        


    def export_videos(self):
        '''
        Returns data in format for exporting: video id is returned within full YouTube url.
        '''
        if len(self.data["Title"]) == 0:
            self.fetch_videos()
        self.data["URL"] = [f"https://www.youtube.com/watch?v={i}" for i in self.data["URL"]]

        return self.data 


    def get_video_ids(self):
        '''
        Return list of videos IDs.
        '''

        return self.data["URL"]


    def get_thumbnails(self):
        '''
        Return list of thumbnail URLs
        '''

        return self.data["Thumbnail"]


    def get_channels(self):
        '''
        Returns list of channels. Includes duplicates.
        '''

        return self.data["Channel"] 


    def get_titles(self):
        '''
        Returns list of video titles.
        '''

        return self.data["Title"] 
