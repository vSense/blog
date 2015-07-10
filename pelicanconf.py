#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'vSense'
SITENAME = 'vSense'
SITEURL = 'http://blog.vsense.fr'

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'fr'
THEME = 'themes/pelican-pure'

DISQUS_SITENAME = 'vsense'
GOOGLE_ANALYTICS = 'UA-33687380-2'

PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['gravatar','share_post']

SUMMARY_MAX_LENGTH = 40

TAGLINE = "Cloud Cloud Cloud, I'm looking for a good time !"
PROFILE_IMAGE_URL = 'http://i.forbesimg.com/media/lists/companies/google_416x416.jpg'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
#LINKS = (('Pelican', 'http://getpelican.com/'),
#         ('Python.org', 'http://python.org/'),
#         ('Jinja2', 'http://jinja.pocoo.org/'),
#         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('github-square', 'https://github.com/vSense'),
        ('linkedin-square', 'https://www.linkedin.com/in/kevinlefevre'),
        ('linkedin-square', 'https://fr.linkedin.com/in/romainguichard'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
