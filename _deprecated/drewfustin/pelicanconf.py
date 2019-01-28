#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u'Drew Fustin'
SITENAME = u'Drew Fustin'
SITEURL = 'http://www.drewfustin.com'
TIMEZONE = 'America/Chicago'
THEME = './theme/notebook-simpler'
SUMMARY_MAX_LENGTH = 50
AVATAR = '/theme/images/avatar.jpg'
DESCRIPTION = "Data Scientist: <a href='http://spothero.com/'>SpotHero</a> <br>PhD: <a href='http://uchicago.edu'>University of Chicago</a> <br>Residency: <a href='https://en.wikipedia.org/wiki/History_of_Chicago'>Chicago</a> <br><a href='http://drewfustin.com/about/'>About Me</a>"

ARTICLE_URL = '{slug}'
ARTICLE_SAVE_AS = '{slug}/index.html'


# DEFAULTS
DEFAULT_LANG = 'en'
DEFAULT_CATEGORY = 'misc'
DEFAULT_DATE = 'fs'
DEFAULT_DATE_FORMAT = '%d %b %Y'
DEFAULT_PAGINATION = False


# FEEDS
FEED_ALL_ATOM = "feeds/all.atom.xml"
TAG_FEED_ATOM = "feeds/tag/%s.atom.xml"


# PLUGINS
PLUGIN_PATHS = ['../pelican-plugins']
# PLUGINS = ['liquid_tags.notebook', 'liquid_tags.include_code',
#             'liquid_tags.img', 'liquid_tags.video']

CODE_DIR = 'code'
NOTEBOOK_DIR = 'notebooks'
EXTRA_HEADER = open('_nb_header.html').read().decode('utf-8')

STATIC_PATHS = ['images', 'code', 'notebooks', 'extra', 'html']
EXTRA_PATH_METADATA = {'extra/robots.txt': {'path': 'robots.txt'},}
READERS = {"html": None}

# Additional
DISQUS_SITENAME = "drewfustin"
GOOGLE_ANALYTICS = "UA-59064911-1"
DOMAIN = "drewfustin.com"

# Twitter Cards
TWITTER_CARDS = True
TWITTER_NAME = "drewfustin"
