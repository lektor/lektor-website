# -*- coding: utf-8 -*-
import posixpath
from datetime import date

from werkzeug.utils import cached_property

from lektor.pluginsystem import Plugin
from lektor.sourceobj import VirtualSourceObject
from lektor.build_programs import BuildProgram
from lektor.context import get_ctx


def get_path_segments(str):
    pieces = str.split('/')
    if pieces == ['']:
        return []
    return pieces


def push_path(pieces, item):
    if item:
        pieces.append(unicode(item))


class BlogArchive(VirtualSourceObject):

    def __init__(self, parent, plugin, items=None, year=None, month=None):
        VirtualSourceObject.__init__(self, parent)
        self.plugin = plugin
        self._items = items
        self.year = year
        self.month = month

    @property
    def date(self):
        if self.year is None:
            raise AttributeError()
        return date(self.year, self.month or 1, 1)

    @property
    def year_archive(self):
        if self.year is None:
            raise AttributeError()
        if self.month is None:
            return self
        return BlogArchive(self.parent, self.plugin, year=self.year)

    @property
    def archive_index(self):
        if self.year is None:
            return self
        return BlogArchive(self.parent, self.plugin)

    @cached_property
    def year_archives(self):
        if self.year is not None:
            return []
        years = set()
        for item in self.parent.children:
            pub_date = self.plugin.get_pub_date(item)
            if pub_date:
                years.add(pub_date.year)
        return [BlogArchive(self.parent, self.plugin,
                            year=year) for year in sorted(years)]

    @property
    def items(self):
        if self.year is None:
            return []
        if self._items is not None:
            return self._items
        rv = list(self._iter_items())
        self._items = rv
        return rv

    def _iter_items(self):
        for item in self.parent.children:
            pub_date = self.plugin.get_pub_date(item)
            if pub_date is None:
                continue
            if pub_date.year == self.year and \
               (self.month is None or pub_date.month == self.month):
                yield item

    @property
    def has_any_items(self):
        if self._items is not None:
            return bool(self._items)
        for item in self._iter_items():
            return True
        return False

    @property
    def items_by_months(self):
        months = {}
        for item in self.items:
            pub_date = self.plugin.get_pub_date(item)
            months.setdefault(date(pub_date.year, pub_date.month, 1),
                              []).append(item)
        return [(BlogArchive(self.parent, self.plugin,
                             year=d.year, month=d.month), i)
                for d, i in sorted(months.items())]

    @property
    def url_path(self):
        prefix = self.parent.url_path.strip('/')
        pieces = []
        if prefix:
            pieces.append(prefix)
        if self.year is None:
            push_path(pieces, self.plugin.get_archive_index_path())
        elif self.month is None:
            push_path(pieces, self.plugin.get_month_archive_prefix())
            push_path(pieces, self.year)
        else:
            push_path(pieces, self.plugin.get_year_archive_prefix())
            push_path(pieces, self.year)
            push_path(pieces, self.month)
        return '/%s/' % '/'.join(pieces)

    @property
    def template_name(self):
        if self.year is None:
            return 'blog-archive/index.html'
        if self.month is None:
            return 'blog-archive/year.html'
        return 'blog-archive/month.html'


class BlogArchiveBuildProgram(BuildProgram):

    def produce_artifacts(self):
        self.declare_artifact(
            posixpath.join(self.source.url_path, 'index.html'),
            sources=list(self.source.iter_source_filenames()))

    def build_artifact(self, artifact):
        artifact.render_template_into(self.source.template_name,
                                      this=self.source)


class BlogArchivePlugin(Plugin):
    name = u'Blog Archive'
    description = u'Adds archives to a blog.'

    def get_pub_date(self, post):
        key = self.get_config().get('pub_date_field', 'pub_date')
        return post[key]

    def get_blog_path(self):
        return self.get_config().get('blog_path', '/blog')

    def get_archive_index_path(self):
        return self.get_config().get('archive_path', 'archive').strip('/')

    def get_year_archive_prefix(self):
        return self.get_config().get('year_archive_prefix', 'archive').strip('/')

    def get_month_archive_prefix(self):
        return self.get_config().get('month_archive_prefix', 'archive').strip('/')

    def on_setup_env(self, **extra):
        blog_path = self.get_blog_path()
        self.env.add_build_program(BlogArchive, BlogArchiveBuildProgram)

        def get_blog_archive():
            pad = get_ctx().pad
            blog = pad.get(blog_path)
            if blog is not None:
                return BlogArchive(blog, self)
        self.env.jinja_env.globals['get_blog_archive'] = get_blog_archive

        @self.env.urlresolver
        def archive_resolver(node, url_path):
            if node.path != blog_path:
                return

            archive_index = get_path_segments(self.get_archive_index_path())
            if url_path == archive_index:
                return BlogArchive(node, self)

            year_prefix = get_path_segments(self.get_year_archive_prefix())
            month_prefix = get_path_segments(self.get_month_archive_prefix())

            year = None
            month = None

            if url_path[:len(year_prefix)] == year_prefix and \
               url_path[len(year_prefix)].isdigit() and \
               len(url_path) == len(year_prefix) + 1:
                year = int(url_path[len(year_prefix)])
            elif (url_path[:len(month_prefix)] == month_prefix and
                  len(url_path) == len(month_prefix) + 2 and
                  url_path[len(month_prefix)].isdigit() and
                  url_path[len(month_prefix) + 1].isdigit()):
                year = int(url_path[len(month_prefix)])
                month = int(url_path[len(month_prefix) + 1])
            else:
                return None

            rv = BlogArchive(node, self, year=year, month=month)
            if rv.has_any_items:
                return rv

        @self.env.generator
        def genererate_blog_archive_pages(source):
            if source.path != blog_path:
                return

            blog = source

            years = {}
            months = {}
            for post in blog.children:
                pub_date = self.get_pub_date(post)
                if pub_date:
                    years.setdefault(pub_date.year, []).append(post)
                    months.setdefault((pub_date.year,
                                       pub_date.month), []).append(post)

            yield BlogArchive(blog, self)
            for year, items in sorted(years.items()):
                yield BlogArchive(blog, self, year=year, items=items)
            for (year, month), items in sorted(months.items()):
                yield BlogArchive(blog, self, year=year, month=month,
                                  items=items)
