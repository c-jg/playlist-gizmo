from bs4 import BeautifulSoup as soup


def use_local_file(FLAGS):
    '''
    Reads all Watch Later data in from HTML file.
    Saves video titles and urls.
    '''

    data = {
        "Title": [],
        "URL": []
    }

    file_name = FLAGS.local_wl 
    html = soup(open(file_name), "html.parser")
    videos = html.find_all("a", {"id":"video-title"})

    for video in videos:
        data["Title"].append(video["title"])
        data["URL"].append("https://www.youtube.com" + video["href"].split("&list=WL")[0])

    return data