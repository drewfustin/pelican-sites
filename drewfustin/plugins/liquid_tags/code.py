"""
Code Tag
---------
This implements a Liquid-style code tag for Pelican,
based on the octopress image tag [1]_
Syntax
------
{% code /path/to/code [language:X] [lines:X-Y] [:download:] %}
Examples
--------
{% code test/code/code.py %}
{% code
    test/code/code.py
    language:python
    lines:20-30
    :download:
%}
[1] https://github.com/imathis/octopress/blob/master/plugins/image_tag.rb
"""
import re
import os
from .mdx_liquid_tags import LiquidTags

SYNTAX = '{% code /path/to/code [language:python] [lines:X-Y] [:download:] %}'
FORMAT = re.compile(
    r"""
    ^(?:\s+)?                                   # whitespace at beginning
    (?P<src>\S+)                                # src path to file (required)
    (?:\s+)?                                    # whitespace
    (?:(?:language\:(\s+)?)(?P<language>\S+))?  # language (optional)
    (?:\s+)?                                    # whitespace
    (?:(?:lines\:(\s+)?)(?P<lines>\d+\-\d+))?   # lines (optional)
    (?:\s+)?                                    # whitespace
    (?P<download>\:download\:)?                 # flag to include download link
    (?:\s+)?$                                   # whitespace at end
    """, re.VERBOSE)


@LiquidTags.register('code')
def code(preprocessor, tag, markup):
    src = None
    language = None
    lines = None
    line_style = ""

    match = FORMAT.search(markup)
    if match:
        argdict = match.groupdict()
        src = argdict['src']
        language = argdict['language'] or ""
        lines = argdict['lines']
        if lines:
            first_line, last_line = map(int, lines.split('-'))
            line_style = "style='line-start: {};'".format(first_line)
        download = bool(argdict['download'])

    if not src:
        raise ValueError("Error processing input, "
                         "expected syntax: {0}".format(SYNTAX))

    path_dir = preprocessor.configs.getConfig('PATH')
    code_path = os.path.join(path_dir, src)

    if not os.path.exists(code_path):
        raise ValueError("File {0} could not be found".format(code_path))

    with open(code_path) as fh:
        if lines:
            code_lines = fh.readlines()[first_line - 1:last_line]
            code_lines[-1] = code_lines[-1].rstrip()
            code_lines = "".join(code_lines)
        else:
            code_lines = fh.read()

    source = (
        "<figure class='code' {line_style}>\n\n    #!{language}\n    "
        .format(line_style=line_style, language=language)
    )
    source += "\n    ".join(code_lines.split('\n'))
    source += "\n\n"
    if download:
        url = '/'.join((preprocessor.configs.getConfig('SITEURL'), src))
        url = url.replace('\\', '/')
        title = 'download ' + os.path.basename(src)
        source += (
            "<figcaption><a href='{url}'>{title}</a></figcaption>"
            .format(title=title, url=url))
    source += "</figure>"

    return source


# This import allows image tag to be a Pelican plugin
from .liquid_tags import register
