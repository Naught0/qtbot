import requests
import os
import json
import pafy

with open("data/apikeys.json") as f:
    yt_api_key = json.load(f)["youtube"]

api_uri = "https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&type=video&key={}"


def get_video_info(query: str, title_append="", num_results=1, thumb_quality=0) -> dict:
    """ 
    Retrives video ID from the youtube API 

    query: Regular ol' search string

    title_append: for appending things to the title of the video
        e.g. If you're using Plex Media Server and trailers must
        be labeled with '-trailer'

    num_results: int 1 - 5 (youtube gives 5 results per page)

    thumb_quality: 0 - 2 (highest to lowest quality)
    """

    # Youtube API returns 5 results per page
    if not isinstance(num_results, int) or (1 < num_results > 5):
        raise ValueError(
            "Number of results must be an int between 1 and 5 inclusive.")

    # There are only 3 thumb qualities
    if not isinstance(thumb_quality, int) or (0 < thumb_quality > 2):
        raise ValueError(
            "Thumb quality must be an int between 0 and 2 inclusive.")

    # 0: High
    # 1: Medium
    # 2: Default (low)
    thumb_quality_list = ["high", "medium", "default"]

    # Queries must be space delimited
    query = query.replace(" ", "+")

    # Call to youtube snippet API
    call_result = requests.get(api_uri.format(query, yt_api_key)).json()

    if call_result["pageInfo"]["totalResults"] == 0:
        raise LookupError("No results found matching query.")

    if call_result["pageInfo"]["totalResults"] < num_results:
        num_results = call_result["pageInfo"]["totalResults"]
        print("[NOTIFY] Total Youtube results less than desired input. Found {} video(s).".format(num_results))

    # Store gathered information in a dict
    result_dict = {}

    # The Dictionary format is as follows:
    # video_index :
    #   video_id -> video's youtube ID
    #   title -> title + appended string (optional)
    #   description -> video description
    #   views -> video views
    #   video_url -> url to youtube video
    #   thumb_url -> url of thumbnail of selected quality
    for x in range(num_results):
        result_dict[x] = {
            "video_id": call_result["items"][x]["id"]["videoId"],
            "title": call_result["items"][x]["snippet"]["title"] + title_append,
            "description": call_result["items"][x]["snippet"]["description"],
            "views": _get_video_views(_get_watch_url(call_result["items"][x]["id"]["videoId"])),
            "video_url": _get_watch_url(call_result["items"][x]["id"]["videoId"]),
            "thumb_url": call_result["items"][x]["snippet"]["thumbnails"][thumb_quality_list[thumb_quality]]["url"]
        }

    return result_dict


def _get_watch_url(video_id: str) -> str:
    """ Creates watchable / downloadable URL from video's ID """

    return "https://www.youtube.com/watch?v={}".format(video_id)


def _get_video_views(video_url):
    video = pafy.new(video_url)

    return video.viewcount

# This will get video resolution, extension and size
# def get_file_info(video_url):
#     video = pafy.new(video_url)
#     streams = video.streams
#     stream_dict = {}
#     for s in streams:
#         stream_dict[s.resolution] = {"type": s.extension, "size": s.get_filesize()}

#     return stream_dict


def download_video(video_url, video_title, directory=os.getcwd()):
    """ Uses pafy to download the video """

    video = pafy.new(video_url)
    hq_video = video.getbest(preftype="mp4")

    # This bit is ugly but it works so ¯\_(ツ)_/¯
    hq_video.download(filepath=directory + video_title +
                      "." + hq_video.extension, quiet=False)
