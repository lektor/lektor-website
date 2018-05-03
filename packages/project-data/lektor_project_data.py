# -*- coding: utf-8 -*-
import cgi
import pkg_resources

import readme_renderer.markdown
import readme_renderer.rst
import readme_renderer.txt
import requests

from lektor.pluginsystem import Plugin

_RENDERERS = {
    None: readme_renderer.rst,  # Default if description_content_type is None
    '': readme_renderer.rst,  # Default if description_content_type is None
    'text/plain': readme_renderer.txt,
    'text/x-rst': readme_renderer.rst,
    'text/markdown': readme_renderer.markdown,
}

class ProjectDataPlugin(Plugin):
    name = 'Project Data'
    description = u'Retrieve project information from PyPI.'

    data = {}

    def render(self, value, content_type=None):
        """Taken from https://github.com/pypa/warehouse/blob/master/warehouse/filters.py
        to ensure compliance and not reinvent the wheel. We don't want to be creative here.
        """
        content_type, parameters = cgi.parse_header(content_type or '')

        # Get the appropriate renderer
        renderer = _RENDERERS.get(content_type, readme_renderer.txt)

        # Actually render the given value, this will not only render the value, but
        # also ensure that it's had any disallowed markup removed.
        rendered = renderer.render(value, **parameters)

        # If the content was not rendered, we'll render as plaintext instead. The
        # reason it's necessary to do this instead of just accepting plaintext is
        # that readme_renderer will deal with sanitizing the content.
        if rendered is None:
            rendered = readme_renderer.txt.render(value)

        return rendered


    def package_data(self, name, entry_point=None):
        if not entry_point:
            entry_point = 'https://pypi.org/pypi'
        url = '{}/{}/json'.format(entry_point, name)
        resp = requests.get(url)
        pkg = resp.json()
        self.data.update(pkg['info'])
        # rewrite description as rendered description
        self.data['description'] = self.render(
            self.data['description'], self.data['description_content_type'])

    def github_data(self, owner=None, repo=None):
        url = 'https://api.github.com/repos/{}/{}'.format(owner, repo)
        response = requests.get(url)
        data = response.json()
        return data

    def project_data(self, name):
        self.package_data(name)
        if 'github' in self.data.get('home_page'):
            owner = self.data['home_page'].split('/')[-2]
            repo = self.data['home_page'].split('/')[-1]
            self.data['gh'] = self.github_data(owner=owner, repo=repo)
        # TODO: support bitbucket
        return self.data

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals['project_data'] = self.project_data
