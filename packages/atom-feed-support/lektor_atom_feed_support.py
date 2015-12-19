# -*- coding: utf-8 -*-
import posixpath
import hashlib
import uuid
from datetime import datetime, date
from lektor.pluginsystem import Plugin
from lektor.context import get_ctx, url_to
from lektor.utils import get_structure_hash

from werkzeug.contrib.atom import AtomFeed
from markupsafe import escape


def get_id(input):
    return uuid.UUID(bytes=hashlib.md5(input).digest(),
                     version=3).urn


def get_item_title(item, field):
    if field in item:
        return item[field]
    return item.record_label


def get_item_body(item, field):
    if field not in item:
        raise RuntimeError('Body field not found: %r' % field)
    with get_ctx().changed_base_url(item.url_path):
        return unicode(escape(item[field]))


def get_item_author(item, field):
    if field in item:
        return unicode(item[field])
    return 'Unknown'


def get_item_updated(item, field):
    if field in item:
        rv = item[field]
    else:
        rv = datetime.utcnow()
    if isinstance(rv, date):
        rv = datetime(*rv.timetuple()[:3])
    return rv


def create_atom_feed(filename='atom.xml',
                     title=None, subtitle=None,
                     link=None, items=None, item_title_field='title',
                     item_body_field='body', item_author_field='author',
                     item_date_field='pub_date'):
    ctx = get_ctx()
    if ctx is None:
        raise RuntimeError('A context is required')
    source = ctx.source
    if source is None:
        raise RuntimeError('Can only generate feeds out of sources.')
    if items is None:
        raise RuntimeError('An item expression is required')

    artifact_name = posixpath.join(source.url_path, filename)
    config_hash = get_structure_hash({
        'filename': filename,
        'title': title,
        'subtitle': subtitle,
        'link': link,
        'items': items,
        'item_title_field': item_title_field,
        'item_body_field': item_body_field,
        'item_author_field': item_author_field,
        'item_date_field': item_date_field,
    })

    # Iterating over the items will resolve dependencies.  As we are very
    # interested in those, we need to capture tem,
    dependencies = set()
    with ctx.gather_dependencies(dependencies.add):
        items = list(items)

    here = posixpath.join(source.url_path, filename)
    feed_url = url_to(here, external=True)
    embed_url = url_to(source, external=True)

    @ctx.sub_artifact(artifact_name, source_obj=ctx.source,
                      sources=list(dependencies),
                      config_hash=config_hash)
    def generate_feed(artifact):
        feed = AtomFeed(
            title=title or 'Feed',
            subtitle=unicode(subtitle or ''),
            subtitle_type=hasattr(subtitle, '__html__') and 'html' or 'text',
            feed_url=feed_url,
            url=embed_url,
            id=get_id(ctx.env.project.id + 'lektor')
        )

        for item in items:
            feed.add(
                get_item_title(item, item_title_field),
                get_item_body(item, item_body_field),
                xml_base=url_to(item, external=True),
                url=url_to(item, external=True),
                content_type='html',
                id=get_id(u'%slektor/%s' % (
                    ctx.env.project.id,
                    item['_path'].encode('utf-8'),
                )),
                author=get_item_author(item, item_author_field),
                updated=get_item_updated(item, item_date_field))

        with artifact.open('wb') as f:
            f.write(feed.to_string().encode('utf-8') + '\n')

    return artifact_name


class AtomFeedSupportPlugin(Plugin):
    name = u'Atom Feed Support'
    description = u'Adds basic Atom feed support to Lektor.'

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals['create_atom_feed'] = create_atom_feed
