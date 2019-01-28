import os
import logging
import six
from pelican import signals
from pelican.contents import Article, Page
from pelican.generators import ArticlesGenerator
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def images_extraction(instance):
    if type(instance) not in (Article, Page):
        return

    representativeImage = None

    if 'image' in instance.metadata:
        if instance.metadata['image'].startswith('{filename}'):
            path = instance.metadata['image'].replace('{filename}', '')
            if path.startswith('/'):
                path = path[1:]
            else:
                path = instance.get_relative_source_path(
                    os.path.join(instance.relative_dir, path)
                )
            if path not in instance._context['filenames']:
                unquoted_path = path.replace('%20', ' ')

                if unquoted_path in instance._context['filenames']:
                    path = unquoted_path
            linked_content = instance._context['filenames'].get(path)
            if linked_content:
                representativeImage = '/'.join((instance.get_siteurl(), linked_content.url))
                representativeImage = representativeImage.replace('\\', '/')
            else:
                logger.warning(
                    "Unable to find `%s`, skipping url replacement.",
                    instance.metadata['image'].replace('{filename}', ''))
        else:
            representativeImage = instance.metadata['image']

    # Process Summary:
    # If summary contains images, extract one to be the representativeImage and remove images from summary
    soup = BeautifulSoup(instance.summary, 'html.parser')
    images = soup.find_all('img')
    for i in images:
        if not representativeImage:
            representativeImage = i['src']
        i.extract()
    if len(images) > 0:
        # set _summary field which is based on metadata. summary field is only based on article's content and not settable
        instance._summary = six.text_type(soup)

    # If there are no images in summary, look for it in the content body
    if not representativeImage:
        soup = BeautifulSoup(
            instance._update_content(instance._content, instance.get_siteurl()),
            'html.parser')
        imageTag = soup.find('img')
        if imageTag:
            representativeImage = imageTag['src']

    # Set the attribute to content instance
    instance.featured_image = representativeImage


def run_plugin(generators):
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                images_extraction(article)


def register():
    try:
        signals.all_generators_finalized.connect(run_plugin)
    except AttributeError:
        # NOTE: This results in #314 so shouldn't really be relied on
        # https://github.com/getpelican/pelican-plugins/issues/314
        signals.content_object_init.connect(images_extraction)
