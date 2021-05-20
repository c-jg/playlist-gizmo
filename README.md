# Playlist Transfer 
## Playlist Transfer is a tool for creating, modifying, exporting, and transferring YouTube playlists.

![](Screen%20Shot%202021-03-07%20at%2011.04.23%20PM.png)

## Setup
1. Install dependencies
2. Authorize YouTube Data API v3 in Google Cloud Platform Console 
3. Create API key and add to environment

To save videos from a public playlist in a CSV, run the following command:
```
python src/main.py --public --export_videos https://www.youtube.com/playlist?list=PLuUrokoVSxlcgocBXbDF76yWd3YKWpOH9 --save_path top_200_songs.csv
```

To move videos among multiple accounts:
* Create OAuth 2.0 Client ID (Desktop Client) and include client secrets file
* Add desired Google accounts to Test Users

Example usage to add videos from playlist on one account to another:
```
python src/main.py --move <URL of playlist on Account 1> --to <URL of playlist on Account 2>
```
All videos in Playlist 1 will be added to Playlist 2.


Example usage to add videos from CSV to playlist on YouTube account:
```
python src/main.py --move my_old_playlist_videos.csv --to <URL of new playlist>
```

Creating an empty playlist can be done by running the command:
```
python src/main.py --create_playlist <NAME OF PLAYLIST>
```
The optional `--description` flag can be used to add a description to the playlist.

## Additional
### Export Watch Later Playlist
* Watch Later playlists can be exported by saving the HTML page and running the following command:
```
python src/main.py --local_wl <path to HTML file>
```
