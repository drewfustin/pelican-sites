# The MIT License (MIT)
#
# Copyright (c) 2018 Drew Fustin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Code Line Number Fixer
-------------------
This plugin:
- Allows for code to start on a line number different than 1
- It strips the line-start element of the style attached to a figure.code element
"""

import re
import markdown
from pelican import signals
from bs4 import BeautifulSoup


class _CodeLineNumbersPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        pattern = re.compile(
            r"^(?P<indent>\s+)(?:\#\!)(?:\S+)?(?:\s+)(?P<line_start>start:\d+)(?:\S+)?$")

        out_lines = []
        in_code_block = False
        indent = None

        while lines:
            line = lines.pop(0)
            if in_code_block:
                if len(line) > 0 and not line.startswith(indent):
                    out_lines.append('')
                    out_lines.append("</figure>")
                    out_lines.append('')
                    in_code_block = False
            else:
                match = pattern.search(line)
                if match:
                    argdict = match.groupdict()
                    indent = argdict['indent']
                    line_start = int(argdict['line_start'].replace('start:', ''))
                    out_lines.append(
                        "<figure class='code' style='line-start: {};'>"
                        .format(line_start))
                    out_lines.append('')
                    line = line.replace(argdict['line_start'], '').rstrip()
                    in_code_block = True

            out_lines.append(line)

        return out_lines


class CodeLineNumbers(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('fix_line_nos', _CodeLineNumbersPreprocessor(self), ">html_block")


def initialized(gen):
    if not gen.settings.get('MARKDOWN'):
        from pelican.settings import DEFAULT_CONFIG
        gen.settings['MARKDOWN'] = DEFAULT_CONFIG['MARKDOWN']

    if CodeLineNumbers not in gen.settings['MARKDOWN']:
        gen.settings['MARKDOWN'].setdefault('extensions', []).append(CodeLineNumbers())


def content_object_init(instance):
    if instance._content is not None:
        content = instance._content
        soup = BeautifulSoup(content, "html.parser")

        if 'figure' in content:
            pattern = re.compile(r"line-start:(.+?);")
            for fig in soup.find_all('figure', class_='code', style=pattern):
                match = pattern.search(fig.attrs['style'])
                if match:
                    line_start = int(match.group(1).strip())
                    fig.attrs['style'] = pattern.sub('', fig.attrs['style']).strip()
                    if not fig.attrs['style']:
                        fig.attrs.pop('style', None)
                else:
                    continue
                for div in fig.find_all('div', class_='linenodiv'):
                    pre = div.find('pre')
                    line_nos = pre.string
                    new_line_nos = ''
                    for line in line_nos.split('\n'):
                        new_line_nos += str(int(line) + line_start - 1) + '\n'
                    pre.string = new_line_nos

        instance._content = soup.decode()
        # If beautiful soup appended html tags.
        if instance._content.startswith('<html>'):
            instance._content = instance._content[12:-14]


def register():
    signals.content_object_init.connect(content_object_init)
    signals.initialized.connect(initialized)
