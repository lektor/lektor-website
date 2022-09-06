# -*- coding: utf-8 -*-
import cgi
import re
from email.utils import getaddresses

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


def normalize_url(url):
    """Normalize project home page URLs."""
    # Normalize any URLS to GitHub project repos.
    m = re.match(
        r"""
            https?://(?:www\.)?github\.com
            / (?P<owner>[^/]+)
            / (?P<project>[^/]+?) (?:\.git)
            /? \Z
        """,
        url,
        flags=re.VERBOSE
    )
    if m:
        return "https://github.com/{owner}/{project}".format(**m.groupdict())
    return url


def bc_kluge_emails(data):
    """Remove any display names from "{Author,Maintainer}-Email" metadata field.

    Additionally, if the "Author" metadata is empty, it is filled is with
    any display names extracted from the "Author-Email" field.  (And similarly
    for the "Maintainer" field.)

    According to PEP621_, when both author ``name`` and ``email`` are
    specified in ``pyproject.toml``, both of those wind up in the
    "Author-Email" metadata field. In that case, the "Author" metadata
    field remains empty.

    (While, historically (e.g. in ``setup.py`` based projects), it
    seems to have been common practice to put the author's name in
    "Author" and their email in "Author-Email", the `Core Metadata
    Spec<mdspec_>`_ is not particularly opinionated on whether the
    author name(s) should go into "Author", "Author-Email", or both.)

    Further not that RFC6068_, the current spec for ``mailto:`` URIs
    only wants addr-specs in the mailto URLs.

    .. _PEP621: https://peps.python.org/pep-0621/#authors-maintainers
    .. _mdspec: https://packaging.python.org/en/latest/specifications/core-metadata/#author
    .. _RFC6068: https://datatracker.ietf.org/doc/html/rfc6068
    """
    for name_field, email_field in [
            ("author", "author_email"),
            ("maintainer", "maintainer_email")
    ]:
        addresses = getaddresses([data.get(email_field, "")])
        data[email_field] = ", ".join(
            addrspec for name, addrspec in addresses if addrspec
        )
        if not data.get(name_field):
            data[name_field] = ", ".join(
                name for name, addrspec in addresses if name
            )

class ProjectDataPlugin(Plugin):
    name = 'Project Data'
    description = u'Retrieve project information from PyPI.'

    data = {}

    def render(self, value, content_type=None):
        """Render project description.

        This is taken from
        https://github.com/pypa/warehouse/blob/master/warehouse/filters.py
        to ensure compliance and not reinvent the wheel.  We don't
        want to be creative here.

        """
        content_type, parameters = cgi.parse_header(content_type or '')

        # Get the appropriate renderer
        renderer = _RENDERERS.get(content_type, readme_renderer.txt)

        # Actually render the given value, this will not only render
        # the value, but also ensure that it's had any disallowed
        # markup removed.
        rendered = renderer.render(value, **parameters)

        # If the content was not rendered, we'll render as plaintext
        # instead. The reason it's necessary to do this instead of
        # just accepting plaintext is that readme_renderer will deal
        # with sanitizing the content.
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
        # Erase bad keys that are sometimes returned from the api
        # to handle it in the template.
        # To us, unknown is the same as non-existent.
        for key in self.data:
            val = self.data.get(key)
            if type(val) is str and val.strip() == 'UNKNOWN':
                self.data[key] = ''
        self.data['short_name'] = name.split('lektor-')[1]

        # Rewrite description as rendered description.
        self.data['description'] = self.render(
            self.data['description'], self.data['description_content_type'])
        if not self.data.get('home_page'):
            self.data['home_page'] = f'https://pypi.org/project/{name}/'
        else:
            self.data['home_page'] = normalize_url(self.data['home_page'])

        bc_kluge_emails(self.data)

    def github_data(self, owner=None, repo=None):
        url = 'https://api.github.com/repos/{}/{}'.format(owner, repo)
        response = requests.get(url)
        data = response.json()
        return data

    def project_data(self, name):
        self.package_data(name)
        # github data not currently used. Commented to save build time.
        # if 'github' in self.data.get('home_page'):
        #     owner = self.data['home_page'].split('/')[-2]
        #     repo = self.data['home_page'].split('/')[-1]
        #     self.data['gh'] = self.github_data(owner=owner, repo=repo)
        # TODO: support bitbucket
        return self.data

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals['project_data'] = self.project_data
