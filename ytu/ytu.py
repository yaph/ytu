# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, urlparse, unquote, ParseResult
from typing import Optional


domains = {'youtube.com', 'youtu.be', 'yt.be'}


def param_value(parsed_url: ParseResult, name: str) -> Optional[str]:
    """Get the first value of the given URL parameter from a urllib.parse.ParseResult object.

    Values in dictionary returned by parse_qs are lists."""
    if parsed_url.query:
        return parse_qs(parsed_url.query).get(name, ['']).pop()
    return None


def is_youtube(url: str) -> bool:
    """Test whether the given URL belongs to one of the recognized YouTube domains."""

    host = urlparse(url.strip()).netloc
    for domain in domains:
        if host == domain or host.endswith('.' + domain):
            return True
    return False


def video_id(url: str, recursion_depth: int = 0, max_recursion_depth: int = 10) -> Optional[str]:
    """Extract and return YouTube video ID.

    Assumption: a YouTube video ID is 11 characters long. All manually tested
    video IDs that were shorter resulted in an error. See these discussions:
    http://stackoverflow.com/a/6250619/291931
    https://groups.google.com/forum/?fromgroups=#!topic/youtube-api-gdata/oAztQ3f1tcM
    """

    if recursion_depth > max_recursion_depth:
        return None

    vid = None
    purl = urlparse(url)
    path = purl.path.lstrip('/')  # strip leading slash(es)

    if purl.netloc.endswith('youtu.be'):
        vid = path

    elif purl.netloc.endswith('youtube.com'):
        # Check for verify age URLs.
        if path.startswith('verify_age'):
            next_url = param_value(purl, 'next_url')
            if next_url:
                # Next URL doesn't contain the host.
                if next_url.startswith('/'):
                    vid = param_value(urlparse(unquote(next_url)), 'v')
                # Next URL is an absolute URL.
                else:
                    vid = video_id(unquote(next_url), recursion_depth=recursion_depth + 1)
        # Check for full screen URLs.
        elif path.startswith(('v/', 'embed/')):
            vid = path.split('/')[1]
        # Check for standard watch URLs.
        elif path.startswith('watch'):
            vid = param_value(purl, 'v')
        # Check for attribution links.
        elif path.startswith('attribution_link'):
            watch_path = param_value(purl, 'u')
            if watch_path:
                vid = param_value(urlparse(watch_path), 'v')

    if vid and len(vid) >= 11:
        # Cut off extraneous characters after the ID.
        return vid[:11]
    return None