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
import json
import pandas as pd
import numpy as np
from .mdx_liquid_tags import LiquidTags

SYNTAX = '{% pandas [save:/path/to/save] [lines:X] pandas_code %}'
FORMAT = re.compile(
    r"""
    ^(?:\s+)?                                 # whitespace at beginning
    (?:(?:lines\:(\s+)?)(?P<lines>\d+))?      # number of lines to display (equivalent to .head(X))
    (?:\s+)?                                  # whitespace
    (?:(src\:(\s+)?)(?P<src>\{.*\}))?         # src dict, key: pd str, val: path (opt)
    (?:\s+)?                                  # whitespace
    (?P<indent>(?<=\n)\s+)                    # whitespace that indents pandas code
    (?P<code>.*)$                             # valid pandas code
    """, re.DOTALL | re.VERBOSE)

@LiquidTags.register('pandas')
def pandas(preprocessor, tag, markup):
    lines = None
    indent = None
    code = None
    shortened = False

    match = FORMAT.search(markup)

    if not match:
        raise ValueError("Error processing input, "
                         "expected syntax: {0}".format(SYNTAX))

    argdict = match.groupdict()
    lines = argdict['lines']
    indent = argdict['indent']
    code = argdict['code']
    try:
        src = json.loads(argdict['src'] or "{}")
    except json.decoder.JSONDecodeError as e:
        print('Malformed JSON in LiquidTags pandas: {}'.format(argdict['src']))
        raise e

    # Display the pandas code being run

    source = "<figure class='code pandas'>\n\n{}#!python\n".format(indent)
    source += indent + code + "\n\n</figure>\n\n"

    # Run the code to get the results
    path_dir = preprocessor.configs.getConfig('PATH')
    for pd_src, file_src in src.items():
        data_path = os.path.join(path_dir, file_src)
        code = code.replace(pd_src, data_path)

    if not lines:
        lines = preprocessor.configs.getConfig('DEFAULT_PANDAS_LINES')

    df = eval(code)
    if int(lines) < len(df):
        shortened = True
    df = df.head(int(lines))

    source += "<table class='csv pandas'>"
    # Column header
    source += "<thead>"
    for i in range(df.columns.nlevels):
        source += "<tr class='col'>"
        # source += "<th class='idx'></th>" * (df.index.nlevels - 1)
        source += "<th class='idx last' colspan={}>".format(df.index.nlevels)
        source += str(df.columns.get_level_values(i).name or '')
        source += "</th>"
        names = ['' if name is None else str(name) for name in df.columns.get_level_values(i)]
        source += "<th>" + "</th><th>".join(names) + "</th>"
        source += "</tr>"
    # Index header
    if any(df.index.names):
        source += "<tr class='idx'>"
        names = ['' if name is None else str(name) for name in df.index.names]
        if len(names) > 1:
            source += "<th class='idx'>"
            source += "</th><th class='idx'>".join(names[:-1])
            source += "</th>"
        source += "<th class='idx last'>{}</th>".format(names[-1])
        source += "<th colspan={}></th>".format(df.columns.size)
        source += "</tr>"
    source += "</thead>"
    # Data
    source += "<tbody>"
    for i in range(df.index.size):
        source += "<tr>"
        if isinstance(df.index, pd.MultiIndex):
            names = ['' if name is None else str(name) for name in df.iloc[i].name]
            source += "<th class='idx'>"
            source += "</th><th class='idx'>".join(names[:-1])
            source += "</th>"
        else:
            names = [str(df.iloc[i].name)]
        source += "<th class='idx last'>{}</th>".format(names[-1])
        source += "<td>" + "</td><td>".join(df.iloc[i].astype(str)) + "</td>"
        source += "</tr>"
    if shortened:
        source += "<tr>"
        source += "<th class='idx'></th>" * (df.index.nlevels - 1)
        source += "<th class='idx last'></th>"
        source += "<td colspan={}>...</td>".format(df.columns.size)
        source += "</tr>"
    source += "</tbody>"
    source += "</table>"

    return source


# This import allows image tag to be a Pelican plugin
from .liquid_tags import register
