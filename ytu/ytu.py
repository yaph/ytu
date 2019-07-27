# -*- coding: utf-8 -*-
from urllib.parse import parse_qs, urlparse, unquote


domains = {'youtube.com', 'youtu.be', 'yt.be'}


def get_param_value(purl, name):
    """Get the first value of the given URL parameter from a urllib.parse.ParseResult object.

    Values in dictionary returned by parse_qs are lists."""
    if purl.query:
        return parse_qs(purl.query).get(name, [None]).pop()


def video_id(url, recursion_depth=0, max_recursion_depth=10):
    """Extract and return youtube video ID.

    Assumption: a YouTube video ID is 11 characters long. All manually tested
    video IDs that were shorter resulted in an error. See these discussions:
    http://stackoverflow.com/a/6250619/291931
    https://groups.google.com/forum/?fromgroups=#!topic/youtube-api-gdata/oAztQ3f1tcM
    """

    if recursion_depth > max_recursion_depth:
        return

    vid = None
    purl = urlparse(url)
    path = purl.path.lstrip('/')  # strip leading slash(es)

    if purl.netloc.endswith('youtu.be'):
        vid = path

    elif purl.netloc.endswith('youtube.com'):
        # Check for verify age URLs.
        if path.startswith('verify_age'):
            next_url = get_param_value(purl, 'next_url')
            if next_url:
                # Next URL doesn't contain the host.
                if next_url.startswith('/'):
                    vid = get_param_value(urlparse(unquote(next_url)), 'v')
                # Next URL is an absolute URL.
                else:
                    vid = extract_video_id(unquote(next_url), recursion_depth=recursion_depth + 1)
        # Check for full screen URLs.
        elif path.startswith(('v/', 'embed/')):
            vid = path.split('/')[1]
        # Check for standard watch URLs.
        elif path.startswith('watch'):
            vid = get_param_value(purl, 'v')
        # Check for attribution links.
        elif path.startswith('attribution_link'):
            watch_path = get_param_value(purl, 'u')
            if watch_path:
                vid = get_param_value(urlparse(watch_path), 'v')

    if vid and len(vid) >= 11:
        # Cut off extraneous characters after the ID.
        return vid[:11]


# All these URLs occurred in the reddit submission corpus.
tests = [
    ('http://youtu.be/zoLVUxKCWhY', 'zoLVUxKCWhY'),
    ('http://www.youtube.com/watch?v=VvRC0wxM-yM', 'VvRC0wxM-yM'),
    ('http://www.youtube.com/watch?v=thsc60UTUIE&amp;feature=youtu.be', 'thsc60UTUIE'),
    ('http://www.youtube.com/watch?v=a3asbkY0tTE?', 'a3asbkY0tTE'),
    ('http://www.youtube.com/watch?v=oHg5SJYRHA0???', 'oHg5SJYRHA0'),
    ('http://www.youtube.com/watch?v=55jUNNPT1eMads/4/NaQOUKyR9CY', '55jUNNPT1eM'),
    ('https://www.youtube.com/verify_age?next_url=http%3A//www.youtube.com/watch%3Fv%3DGqj1N9qeWXI%26feature%3Dmfu_in_order%26list%3DUL', 'Gqj1N9qeWXI'),
    ('https://www.youtube.com//watch?v=PQGrIsYUm4c', 'PQGrIsYUm4c'),  # 2 leading slashes in path
    ('https://www.youtube.com/v/j4FNGsNY3nI&amp;amp;rel=0&amp;amp;egm=0&amp;amp;showinfo=0&amp;amp;fs=1', 'j4FNGsNY3nI'),
    ('https://www.youtube.com/embed/mGnyH-SCZpM?autoplay=1&amp;hd=1&amp;KeepThis=true&amp;TB_iframe=true&amp;height=370&amp;width=640?autoplay=1&amp;hd=1', 'mGnyH-SCZpM'),
    ('https://www.youtube.com/verify_age?&amp;next_url=/watch%3Fv%3DsTPsFIsxM3w', 'sTPsFIsxM3w'),
    ('https://www.youtube.com/attribution_link?a=qbb_5VvcvY8&amp;u=%2Fwatch%3Fv%3DFgFeVlw2Ywg%26feature%3Dshare', 'FgFeVlw2Ywg'),
    ('https://www.youtube.com/attribution_link?a=ar77oUQIEOcNs-Wdao4XJw&amp;u=%2Fwatch%3Fv%3D0eXS1NI6Q6Y%26feature%3Dshare', '0eXS1NI6Q6Y'),
    ('https://www.youtube.com/?v=_RSaYVgd7yk', None),
    ('https://www.youtube.com/watch?v=U3M8pXZusQ', None)
]

for t in tests:
    #print(extract_video_id(t[0]), t[1], t[0])
    assert extract_video_id(t[0]) == t[1]
