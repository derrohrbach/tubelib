import yt_dlp
import os
import json
import os.path
import xml.etree.ElementTree as ElementTree
import datetime

channel_dir = "channels"
out_dir = "out"
work_dir = "tmp"

img_extensions = ["jpg", "jpeg"]

def run_channel(channel_config_path): 
    print("Parsing channel", channel_config_path)
    channel_config_file = open(channel_config_path, "r+")
    channel_config = json.load(channel_config_file)
    channel_config.setdefault('last_sync', None) 
    channel_config.setdefault('last_video_count', 0)
    meta_dir = download_new_meta(channel_config["url"], channel_config["last_sync"])
    channel_info_file = open(os.path.join(meta_dir, "00000.info.json"))
    channel_info = json.load(channel_info_file)
    channel_dir = update_channel_data(channel_config, channel_info)
    copy_thumb(os.path.join(meta_dir, "00000"), os.path.join(channel_dir, "poster"))
    channel_config['last_sync'] = datetime.date.today().isoformat()
    channel_config_file.seek(0)
    json.dump(channel_config, channel_config_file)

def update_channel_data(channel_config, channel_info):
    channel_config.setdefault("dir_name", channel_info["channel"])
    channel_dir = os.path.join(out_dir, channel_config["dir_name"])
    os.makedirs(channel_dir, exist_ok=True)
    xml_root = ElementTree.Element("tvshow")
    ElementTree.SubElement(xml_root, "title").text = channel_info["channel"]
    ElementTree.ElementTree(xml_root).write(os.path.join(channel_dir, "tv_show.nfo"), "utf-8", xml_declaration=True)
    return channel_dir

def copy_thumb(prefix, target_prefix):
    # Remove old thumb
    for ext in img_extensions:
        if os.path.isfile(target_prefix + "." + ext):
            os.remove(target_prefix + "." + ext)
    # Copy new thumb
    for ext in img_extensions:
        if os.path.isfile(prefix + "." + ext):
            os.rename(prefix + "." + ext, target_prefix + "." + ext)
            break

def download_new_meta(url, start_date):
    for f in os.listdir(work_dir):
        os.remove(os.path.join(work_dir, f))
    opts = {
        "writethumbnail": True,
        "allow_playlist_files": True,
        "skip_download": True,
        "writeinfojson": True,
        "break_on_reject": True,
        "outtmpl": "tmp/%(autonumber)s",
        "cookiefile": "cookie.txt",
        "postprocessors": [
            {
                "format": "jpg",
                "key": "FFmpegThumbnailsConvertor",
                "when": "before_dl"
            }
        ]
    }
    if start_date is not None:
        opts["daterange"] = yt_dlp.utils.DateRange(datetime.date.fromisoformat(start_date).strftime("%Y%m%d"))
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            ydl.download(url)
        except yt_dlp.utils.RejectedVideoReached:
            print("End of videos reached")
    return work_dir

channel_files = [os.path.join(channel_dir, path) for path in os.listdir(channel_dir) if os.path.isfile(os.path.join(channel_dir, path))]

for channel in channel_files:
    run_channel(channel)
