# -*- coding: utf-8 -*-
from qypi.api import QyPI

from lektor.pluginsystem import Plugin

class ProjectDataPlugin(Plugin):
    name = 'Project Data'
    description = u'Retrieve project information from PyPI.'

    data = {}

    def package_data(self, name, entry_point=None):
        if not entry_point:
            entry_point = 'https://pypi.org/pypi'
            
        q = QyPI(entry_point)
        pkg = q.get_package(name)
        self.data.update(pkg['info'])
    
    def project_data(self, name):
        self.package_data(name)
        # self.github_data
        # self.bitbucket_data
        return self.data
    
    def on_setup_env(self, **extra):
        self.env.jinja_env.globals['project_data'] = self.project_data
