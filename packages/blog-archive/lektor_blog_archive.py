# -*- coding: utf-8 -*-
import posixpath
from datetime import date
from itertools import chain

from werkzeug.utils import cached_property

from lektor.pluginsystem import Plugin
from lektor.sourceobj import VirtualSourceObject
from lektor.build_programs import BuildProgram
from lektor.utils import build_url, parse_path


class BlogArchive(VirtualSourceObject):

    def __init__(self, record, plugin, items=None):
        VirtualSourceObject.__init__(self, record)
        self.plugin = plugin
        self._items = items

    @property
    def path(self):
        return self.record.path + '@blog-archive'

    template_name = 'blog-archive/index.html'

    @property
    def parent(self):
        return self.record

    @cached_property
    def year_archives(self):
        years = set()
        for item in self.record.children:
            pub_date = self.plugin.get_pub_date(item)
            if pub_date:
                years.add(pub_date.year)
        return [BlogYearArchive(self.record, self.plugin,
                                year=year) for year in sorted(years)]

    @property
    def items(self):
        if self._items is not None:
            return self._items
        rv = list(self._iter_items())
        self._items = rv
        return rv

    def _iter_items(self):
        return iter(())

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
        return [(BlogMonthArchive(self.record, self.plugin,
                                  year=d.year, month=d.month), i)
                for d, i in sorted(months.items())]

    def get_archive_url_path(self):
        return self.plugin.get_url_path('archive_path')

    @property
    def url_path(self):
        return build_url(chain([self.record.url_path.strip('/')],
                               self.get_archive_url_path() or ()))


class BlogYearArchive(BlogArchive):
    template_name = 'blog-archive/year.html'

    def __init__(self, record, plugin, items=None, year=None):
        BlogArchive.__init__(self, record, plugin, items)
        self.year = year

    def _iter_items(self):
        for item in self.record.children:
            pub_date = self.plugin.get_pub_date(item)
            if pub_date is not None and \
               pub_date.year == self.year:
                yield item

    @property
    def path(self):
        return '%s@blog-archive/%s' % (
            self.record.path,
            self.year,
        )

    @property
    def parent(self):
        return BlogArchive(self.record, self.plugin)

    @property
    def date(self):
        return date(self.year, 1, 1)

    def get_archive_url_path(self):
        return self.plugin.get_url_path('year_archive_prefix') + [self.year]


class BlogMonthArchive(BlogArchive):
    template_name = 'blog-archive/month.html'

    def __init__(self, record, plugin, items=None, year=None, month=None):
        BlogArchive.__init__(self, record, plugin, items)
        self.year = year
        self.month = month

    def _iter_items(self):
        for item in self.record.children:
            pub_date = self.plugin.get_pub_date(item)
            if pub_date is not None and \
               pub_date.year == self.year and \
               pub_date.month == self.month:
                yield item

    @property
    def path(self):
        return '%s@blog-archive/%s/%s' % (
            self.record.path,
            self.year,
            self.month
        )

    @property
    def parent(self):
        return BlogYearArchive(self.record, self.plugin, year=self.year)

    @property
    def date(self):
        return date(self.year, self.month, 1)

    def get_archive_url_path(self):
        return self.plugin.get_url_path('month_archive_prefix') + [
            self.year, self.month]


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

    def get_url_path(self, name, default='archive'):
        return parse_path(self.get_config().get(name, default))

    def on_setup_env(self, **extra):
        self.env.add_build_program(BlogArchive, BlogArchiveBuildProgram)

        @self.env.virtualpathresolver('blog-archive')
        def blog_archive_resolver(node, pieces):
            if node.path == self.get_blog_path():
                if not pieces:
                    return BlogArchive(node, self)
                elif len(pieces) == 1 and pieces[0].isdigit():
                    return BlogYearArchive(node, self, year=int(pieces[0]))
                elif len(pieces) == 2 and pieces[0].isdigit() \
                        and pieces[1].isdigit():
                    return BlogMonthArchive(node, self, year=int(pieces[0]),
                                            month=int(pieces[1]))

        @self.env.urlresolver
        def archive_urlresolver(node, url_path):
            if node.path != self.get_blog_path():
                return

            archive_index = self.get_url_path('archive_path')
            if url_path == archive_index:
                return BlogArchive(node, self)

            year_prefix = self.get_url_path('year_archive_prefix')
            if url_path[:len(year_prefix)] == year_prefix and \
               url_path[len(year_prefix)].isdigit() and \
               len(url_path) == len(year_prefix) + 1:
                year = int(url_path[len(year_prefix)])
                rv = BlogYearArchive(node, self, year=year)
                if rv.has_any_items:
                    return rv

            month_prefix = self.get_url_path('month_archive_prefix')
            if url_path[:len(month_prefix)] == month_prefix and \
               len(url_path) == len(month_prefix) + 2 and \
               url_path[len(month_prefix)].isdigit() and \
               url_path[len(month_prefix) + 1].isdigit():
                year = int(url_path[len(month_prefix)])
                month = int(url_path[len(month_prefix) + 1])
                rv = BlogMonthArchive(node, self, year=year, month=month)
                if rv.has_any_items:
                    return rv

        @self.env.generator
        def genererate_blog_archive_pages(source):
            if source.path != self.get_blog_path():
                return

            years = {}
            months = {}
            for post in source.children:
                pub_date = self.get_pub_date(post)
                if pub_date:
                    years.setdefault(pub_date.year, []).append(post)
                    months.setdefault((pub_date.year,
                                       pub_date.month), []).append(post)

            yield BlogArchive(source, self)
            for year, items in sorted(years.items()):
                yield BlogYearArchive(source, self, year=year, items=items)
            for (year, month), items in sorted(months.items()):
                yield BlogMonthArchive(source, self, year=year, month=month,
                                       items=items)
