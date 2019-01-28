"""
Vega Tag
---------
This implements a Liquid-style vega tag for Pelican,
based on the octopress image tag [1]_
Syntax
------
{% vega /path/to/plot/code [:altair:] [caption:"text"] [credit:"text"]
   [style:/path/to/style/json] [kwargs:{valid/json/dictionary}] %}
/path/to/plot/code is relative to the PATH (typically content/ folder)
Examples
--------
{% plot
    test/plots/horsepower_vs_mpg.html
    caption:"This is the caption"
    credit:"This is the credit"
    style:static/json/vega.json
    kwargs: {"x": [1, 2, 3], "y": [4, 5, 6]}
%}
[1] https://github.com/imathis/octopress/blob/master/plugins/image_tag.rb
"""
import re
import json
import os
import uuid
import importlib.util
from .mdx_liquid_tags import LiquidTags

SYNTAX = ('{% vega /path/to/plot/code [:altair:] [caption:"text"] [credit:"text"] '
          '[style:/path/to/style/json] [kwargs:{valid/json/dictionary}] %}')
FORMAT = re.compile(
    r"""
    ^(?:\s+)?                                                       # whitespace at beginning
    (?P<src>\S+)                                                    # path to src file (req)
    (?:\s+)?                                                        # whitespace
    (?P<altair>\:altair\:)?                                         # flag if src is altair code
    (?:\s+)?                                                        # whitespace
    (?:(?:caption\:(\s+)?[\"\'])(?P<caption>[^\"\']+))?(?:[\"\'])?  # caption (opt)
    (?:\s+)?                                                        # whitespace
    (?:(?:credit\:(\s+)?[\"\'])(?P<credit>[^\"\']+))?(?:[\"\'])?    # credit (opt)
    (?:\s+)?                                                        # whitespace
    (?:(?:style\:(\s+)?)(?P<style>\S+))?                            # path to Vega config (opt)
    (?:\s+)?                                                        # whitespace
    (?:(kwargs\:(\s+)?)(?P<kwargs>\{.*\}))?                         # kwargs into src (opt)
    (?:\s+)?$                                                       # whitespace at end
    """, re.VERBOSE)


@LiquidTags.register('vega')
def vega(preprocessor, tag, markup):
    src = None
    caption = None
    credit = None
    style = None

    match = FORMAT.search(markup)

    if not match:
        raise ValueError("Error processing input, "
                         "expected syntax: {0}".format(SYNTAX))

    argdict = match.groupdict()
    src = argdict['src']
    altair = bool(argdict['altair'])
    caption = argdict['caption']
    credit = argdict['credit']
    style = argdict['style']

    try:
        kwargs = json.loads(argdict['kwargs'] or "{}")
        for key, val in kwargs.items():
            # Allows linking to content on your site (e.g. data sources for the plot)
            if '{SITEURL}' in val:
                kwargs[key] = val.replace('{SITEURL}', preprocessor.configs.getConfig('SITEURL'))
    except json.decoder.JSONDecodeError as e:
        print('Malformed JSON in LiquidTags plot: {}'.format(argdict['kwargs']))
        raise e

    path_dir = preprocessor.configs.getConfig('PATH')
    plot_path = os.path.join(path_dir, src)

    if not os.path.exists(plot_path):
        raise ValueError("File {0} could not be found".format(plot_path))

    # Get JSON specifying the Vega spec to be embedded
    if altair:
        spec = importlib.util.spec_from_file_location(
            os.path.basename(plot_path).split('.')[0], plot_path)
        plotter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plotter)
        vega_spec = json.loads(plotter.generate_plot(**kwargs))
    else:
        with open(plot_path) as vega_json:
            # Dictionaries have lots of {} characters, which makes string formatting hard
            # This replaces any {} characters surrounding keys in kwargs with the values in kwargs
            #   while leaving all other {} alone
            vega_spec = json.loads(
                re.sub(
                    "(?<!(?<!\{)\{(?!\{)(" + '|'.join(kwargs.keys()) + "))(?<!\})\}(?!\})",
                    "}}",
                    re.sub(
                        "(?<!\{)\{(?!\{)(?!(" + '|'.join(kwargs.keys()) + ")(?<!\})\}(?!\}))",
                        "{{",
                        vega_json.read()
                    )
                ).format(**kwargs)
            )

    # Adds Vega style config components from a provided style JSON object
    # If the vega_spec explicitly contains config components, don't overwrite these with those
    #   found in the style JSON object, but otherwise amend new config components provided in style
    if not style:
        style = preprocessor.configs.getConfig('DEFAULT_VEGA_STYLE')
    theme_dir = preprocessor.configs.getConfig('THEME')
    style_path = os.path.join(theme_dir, style)
    with open(style_path) as style_json:
        vega_config = json.load(style_json)

    if vega_config:
        if 'config' not in vega_spec:
            vega_spec['config'] = {}
        for key in vega_spec['config']:
            if key in vega_config:
                vega_spec['config'][key] = {**vega_config[key], **vega_spec['config'][key]}
        for key in vega_config.keys() - vega_spec['config'].keys():
            vega_spec['config'][key] = vega_config[key]

    # Fix some escaping nonsense
    vega_spec = str(vega_spec).replace('>', '\>')

    # Wrap the Vega spec in the vegaEmbed js script tags and the desired HTML tags
    source = "<figure class='plot'>"
    source += """
        <div id='{id}'></div>
        <script type="text/javascript">
          var spec = {spec};
          var opt = {{"renderer": "canvas", "actions": false}};
          vegaEmbed("#{id}", spec, opt);
        </script>
        """.format(id='viz-' + str(uuid.uuid4()), spec=vega_spec)
    if credit:
        source += "<div class='credit'>{credit}</div>".format(credit=credit)
    if caption:
        source += "<figcaption>{caption}</figcaption>".format(caption=caption)
    source += "</figure>"

    return source


# This import allows image tag to be a Pelican plugin
from .liquid_tags import register
