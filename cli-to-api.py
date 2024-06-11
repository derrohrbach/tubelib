import yt_dlp

def cli_to_api(*opts):
    default = yt_dlp.parse_options([]).ydl_opts
    diff = {k: v for k, v in yt_dlp.parse_options(opts).ydl_opts.items() if default[k] != v}
    if 'postprocessors' in diff:
        diff['postprocessors'] = [pp for pp in diff['postprocessors'] if pp not in default['postprocessors']]
    return diff
    
from pprint import pprint

pprint(cli_to_api('--convert-thumbnails', 'jpg'))  # Change according to your need