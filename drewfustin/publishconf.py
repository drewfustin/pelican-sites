#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import pelican
import os
from inspect import getsourcefile

AUTHOR = 'Drew Fustin'
SITENAME = 'Drew Fustin'
EMAIL_ADDRESS = 'drewfustin@gmail.com'
SITE_DESCRIPTION = 'Articles written by Drew Fustin'
KEYWORDS = ['Python', 'Data Science', 'Data']
SITEURL = 'http://drewfustin.com'
GITHUB_SITE_REPO = 'https://github.com/drewfustin/drewfustin.github.io'
PELICAN_VERSION = pelican.__version__

# Accounts
GOOGLE_ANALYTICS = 'UA-59064911-1'

# Style
THEME = 'themes/automaton'
BANNER_COLOR = '#000'
HEADSHOT_LINK = SITEURL + '/about'
HEADSHOT_URL = SITEURL + '/static/img/headshot.png'
# List of (url, FontAwesome class)
BANNER_LINKS = [
    (SITEURL, 'fas fa-home'),
    ('https://github.com/drewfustin', 'fab fa-github'),
    ('https://twitter.com/drewfustin', 'fab fa-twitter'),
    ('https://www.linkedin.com/in/drewfustin', 'fab fa-linkedin'),
    ('mailto:' + EMAIL_ADDRESS, 'fas fa-envelope'),
    ('https://calendly.com/drewfustin', 'far fa-calendar-plus')
]

DIRECT_TEMPLATES = [
    'index',
    'search',
    '404'
]

# Time/Location
TIMEZONE = 'America/Chicago'
DEFAULT_LANG = 'en'
DEFAULT_DATE = 'fs'
DEFAULT_DATE_FORMAT = '%Y-%m-%d (%A)'

# Default metadata
DEFAULT_METADATA = {
    'status': 'published'
}

# Paths
PATH = 'content'
PAGE_PATHS = ['pages']
ARTICLE_EXCLUDES = ['_skeleton', 'static']
STATIC_EXCLUDES = ['_skeleton']

THIS_DIRECTORY = os.path.abspath(getsourcefile(lambda: 0).rpartition('/')[0])
ARTICLE_PATHS = [
    x.name for x in os.scandir(THIS_DIRECTORY + '/' + PATH)
    if x.is_dir() and x.name not in ARTICLE_EXCLUDES and x.name not in PAGE_PATHS
]
STATIC_PATHS = [
    x.name for x in os.scandir(THIS_DIRECTORY + '/' + PATH)
    if x.is_dir() and x.name not in STATIC_EXCLUDES and x.name not in PAGE_PATHS
]

# Output structure
ARTICLE_SAVE_AS = '{slug}/index.html'
ARTICLE_URL = '{slug}'
DRAFT_SAVE_AS = 'drafts/{slug}/index.html'
DRAFT_URL = 'drafts/{slug}'
PAGE_SAVE_AS = '{slug}/index.html'
PAGE_URL = '{slug}'
CATEGORY_SAVE_AS = ''
TAG_SAVE_AS = ''
AUTHOR_SAVE_AS = ''
ARCHIVES_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
TAGS_SAVE_AS = ''

# Feeds
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Misc
DEFAULT_PAGINATION = False
DELETE_OUTPUT_DIRECTORY = False
RELATIVE_URLS = False
DISPLAY_CATEGORIES_ON_MENU = False

# Plugins
PLUGIN_PATHS = ['./plugins']
PLUGINS = [
    'sitemap',
    'tipue_search',
    'render_math',
    'table_overflow',
    'representative_image',
    'simple_footnotes',
    'md_inline_extension',
    'code_linenos',
    'liquid_tags.img',
    'liquid_tags.code',
    'liquid_tags.vega',
    'liquid_tags.csv',
    'liquid_tags.pandas',
    'redirect'
]

# Plugin Settings
MATH_JAX = {
    'align': 'left',
    'indent': '2em',
    'source': "'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js'"
}
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.9,
        'pages': 0.5,
        'indexes': 0.1
    },
    'changefreqs': {
        'articles': 'weekly',
        'pages': 'monthly',
        'indexes': 'daily'
    }
}
MD_INLINE = {
    '^': ('vertical-align: super; font-size: 0.8em;',),
    '~': ('vertical-align: sub; font-size: 0.8em;',),
}
DEFAULT_IMAGE = 'static/img/blank.png'
DEFAULT_VEGA_STYLE = 'static/json/vega.json'
DEFAULT_PANDAS_LINES = 5
REDIRECTS_JSON = 'redirects.json'
