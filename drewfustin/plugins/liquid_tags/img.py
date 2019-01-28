"""
Image Tag
---------
This implements a Liquid-style image tag for Pelican,
based on the octopress image tag [1]_
Syntax
------
{% img [http[s]:/]/path/to/image [width:X] [height:Y]
    [alt:"alt text"] [title:"title text"] [caption:"caption text"] [credit:"credit text"] %}
Examples
--------
{% img https://octodex.github.com/images/stormtroopocat.png width:400 %}
{% img https://octodex.github.com/images/stormtroopocat.png caption:"This is the caption" %}
{% img
    https://octodex.github.com/images/stormtroopocat.png
    width:400
    height:400
    alt:"Stormtroopocat"
    title:"Stormtroopocat"
    caption:"This is the caption"
    credit:"This is the credit"
%}
[1] https://github.com/imathis/octopress/blob/master/plugins/image_tag.rb
"""
import re
from .mdx_liquid_tags import LiquidTags

SYNTAX = (
    '{% img [http[s]:/]/path/to/image [width:X] [height:Y] '
    '[alt:"alt text"] [title:"title text"] [caption:"caption text"] [credit:"credit text"] %}')
FORMAT = re.compile(
    r"""
    ^(?:\s+)?                                             # whitespace at beginning
    (?P<src>\S+)                                          # src path to file (required)
    (?:\s+)?                                              # whitespace
    (?:(?:width:)(?P<width>\d+))?                         # width (optional)
    (?:\s+)?                                              # whitespace
    (?:(?:height:)(?P<height>\d+))?                       # height (optional)
    (?:\s+)?                                              # whitespace
    (?:(?:alt:[\"'])(?P<alt>[^\"']+))?(?:[\"'])?          # alt (optional)
    (?:\s+)?                                              # whitespace
    (?:(?:title:[\"'])(?P<title>[^\"']+))?(?:[\"'])?      # title (optional)
    (?:\s+)?                                              # whitespace
    (?:(?:caption:[\"'])(?P<caption>[^\"']+))?(?:[\"'])?  # caption (optional)
    (?:\s+)?                                              # whitespace
    (?:(?:credit:[\"'])(?P<credit>[^\"']+))?(?:[\"'])?    # credit (optional)
    (?:\s+)?$                                             # whitespace at end
    """, re.VERBOSE)


@LiquidTags.register('img')
def img(preprocessor, tag, markup):
    src = None
    width = None
    height = None
    alt = None
    title = None
    caption = None
    credit = None

    match = FORMAT.search(markup)

    if match:
        argdict = match.groupdict()
        src = argdict['src']
        width = argdict['width']
        height = argdict['height']
        alt = argdict['alt'] or " "
        title = argdict['title']
        caption = argdict['caption']
        credit = argdict['credit']

    if not src:
        raise ValueError("Error processing input, "
                         "expected syntax: {0}".format(SYNTAX))

    source = "<figure class='img'><img src='{src}' alt='{alt}'".format(src=src, alt=alt)
    if title:
        source += " title='{title}'".format(title=title)
    if width:
        source += " width='{width}px'".format(width=width)
    if height:
        source += " height='{height}px'".format(height=height)
    source += ">"
    if credit:
        source += "<div class='credit'>{credit}</div>".format(credit=credit)
    if caption:
        source += "<figcaption>{caption}</figcaption>".format(caption=caption)
    source += "</figure>"

    return source


# This import allows image tag to be a Pelican plugin
from .liquid_tags import register
