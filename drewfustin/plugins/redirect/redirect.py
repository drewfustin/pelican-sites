# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
import logging
from urllib.parse import urlparse
import json

from pelican import signals

logger = logging.getLogger(__name__)


class RedirectGenerator(object):
    TEMPLATE = """
    <!DOCTYPE html><html><head><meta charset="utf-8" />
    <meta http-equiv="refresh" content="0; url={destination}" />
    </head></html>
    """

    def __init__(self, context, settings, path, theme, output_path, *args):
        self.path = path
        self.output_path = output_path
        self.redirects_file = settings.get('REDIRECTS_JSON', None)

    def create_redirect(self, redirect):
        alias = os.path.join(self.output_path, redirect['slug'])

        try:
            os.makedirs(alias)
        except OSError:
            pass

        alias_file = os.path.join(alias, 'index.html')

        with open(alias_file, 'w') as fd:
            destination = redirect['url']
            # if schema is empty then we are working with a local path
            if not urlparse(destination).scheme:
                # if local path is missing a leading slash then add it
                if not destination.startswith('/'):
                    destination = '/{0}'.format(destination)
            fd.write(self.TEMPLATE.format(destination=destination))

    def generate_output(self, writer):
        if not self.redirects_file:
            return
        redirects_file = os.path.join(self.path, self.redirects_file)
        if not os.path.isfile(redirects_file):
            return

        with open(redirects_file, encoding='utf-8') as redirects_file:
            redirects = json.loads(redirects_file.read())

        for redirect in redirects:
            self.create_redirect(redirect)


def get_generators(generators):
    return RedirectGenerator


def register():
    signals.get_generators.connect(get_generators)
