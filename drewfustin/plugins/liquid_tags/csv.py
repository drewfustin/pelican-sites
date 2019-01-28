"""
CSV Tag
---------
This implements a Liquid-style csv tag for Pelican,
based on the octopress image tag [1]_
Syntax
------
{% csv /path/to/csv [lines:X-Y] [:no_header:] [:download:] %}
Examples
--------
{% csv test/data/data.csv %}
{% csv
    test/data/data.csv
    lines:20-30
    :download:
%}
[1] https://github.com/imathis/octopress/blob/master/plugins/image_tag.rb
"""
import re
import os
import csv as csv_mod
from .mdx_liquid_tags import LiquidTags

SYNTAX = '{% csv /path/to/csv [lines:X-Y] [:no_header:] [:download:] %}'
FORMAT = re.compile(
    r"""
    ^(?:\s+)?                                   # whitespace at beginning
    (?P<src>\S+)                                # src path to file (required)
    (?:\s+)?                                    # whitespace
    (?:(?:lines\:(\s+)?)(?P<lines>\d+\-\d+))?   # lines (optional)
    (?:\s+)?                                    # whitespace
    (?P<no_header>\:no_header\:)?               # flag if there is no header line
    (?:\s+)?                                    # whitespace
    (?P<download>\:download\:)?                 # flag to include download link
    (?:\s+)?$                                   # whitespace at end
    """, re.VERBOSE)


@LiquidTags.register('csv')
def csv(preprocessor, tag, markup):
    src = None
    lines = None
    header = None
    first_line = 1
    last_line = -1

    match = FORMAT.search(markup)
    if match:
        argdict = match.groupdict()
        src = argdict['src']
        lines = argdict['lines']
        if lines:
            first_line, last_line = map(int, lines.split('-'))
        no_header = bool(argdict['no_header'])
        download = bool(argdict['download'])

    if not src:
        raise ValueError("Error processing input, "
                         "expected syntax: {0}".format(SYNTAX))

    path_dir = preprocessor.configs.getConfig('PATH')
    csv_path = os.path.join(path_dir, src)

    if not os.path.exists(csv_path):
        raise ValueError("File {0} could not be found".format(csv_path))

    with open(csv_path, 'r') as csv_file:
        csv_content = [row for row in csv_mod.reader(csv_file)]
        n_cols = len(csv_content[0])
        if not no_header:
            header = csv_content.pop(0)
        data = csv_content[first_line - 1:last_line]

    source = "<table class='csv'>"
    if header:
        source += "<thead><tr>"
        source += "<th>" + "</th><th>".join(header) + "</th>"
        source += "</tr></thead>"
    source += "<tbody>"
    for row in data:
        source += "<tr>"
        source += "<td>" + "</td><td>".join(row) + "</td>"
        source += "</tr>"
    source += "</tbody></table>"
    if download:
        url = '/'.join((preprocessor.configs.getConfig('SITEURL'), src))
        url = url.replace('\\', '/')
        title = 'download ' + os.path.basename(src)
        source += (
            "<p class='caption'><a href='{url}'>{title}</a></p>"
            .format(n_cols=n_cols, title=title, url=url))

    return source


# This import allows image tag to be a Pelican plugin
from .liquid_tags import register
