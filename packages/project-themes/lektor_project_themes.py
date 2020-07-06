# -*- coding: utf-8 -*-

"""Plugin to add Themes page"""

import base64
import os
import traceback
from configparser import ConfigParser
from shutil import copyfile
from typing import List

import requests

from lektor.pluginsystem import Plugin

GITHUB_THEMES_REPO = 'lektor/lektor-themes'
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')


class ProjectThemesPlugin(Plugin):
    """Plugin that generates Themes pages"""

    name = 'Project Themes'
    description = 'Build Themes page'
    COUNTER = 0

    def on_before_build_all(self, builder, **extra):
        extra_flags = getattr(
            builder, "extra_flags", getattr(builder, "build_flags", None)
        )

        build_flag_set = 'themes' in extra_flags
        ProjectThemesPlugin.COUNTER += 1
        print(ProjectThemesPlugin.COUNTER)
        self._create_themes_content(build_flag_set)

    def _create_themes_content(self, build_flag_set):
        """
        Creates content for the themes page

        :param bool build_flag_set: Themes should be built
        """
        path_content = os.path.join(self.env.root_path, 'content')
        path_themes = os.path.join(path_content, 'themes')

        os.makedirs(path_themes, exist_ok=True)

        self._add_contents_lr(path_themes)
        self._add_header(path_content, path_themes)

        if build_flag_set:
            if self._github_token_is_valid():
                self._add_themes(path_themes)
            else:
                self._print_warning("Skipping building Themes page. GITHUB_TOKEN env var not found.")
        else:
            self._print_warning("Skipping building Themes page. `--extra-flag themes` not set.")

    @staticmethod
    def _print_warning(message):
        """
        Print warning message

        :param str message: Message to print
        """
        msg = "\n\n"
        msg += "#" * 78
        msg += "\nWARNING: {}\n".format(message)
        msg += "#" * 78
        msg += "\n\n"
        print(msg)

    @staticmethod
    def _add_contents_lr(path_themes):
        """
        Adds contents.lr file

        :param str path_themes: Path to themes folder
        """
        path = os.path.join(path_themes, 'contents.lr')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('_model: themes')

    @staticmethod
    def _add_header(path_content, path_themes):
        """
        Adds header image to themes pages

        :param str path_content: Path to content folder
        :param str path_themes: Path to themes folder
        """
        path_header_src = os.path.join(path_content, 'header.jpg')
        path_header_dest = os.path.join(path_themes, 'header.jpg')
        copyfile(path_header_src, path_header_dest)

    def _github_token_is_valid(self):
        if not GITHUB_TOKEN:
            self._print_warning("Skipping building Themes page. GITHUB_TOKEN env var not found.")
            return False

        # Check token permissions
        url = "https://api.github.com/repos/{}".format(GITHUB_THEMES_REPO)
        api_get(url)
        return True

    def _add_themes(self, path_themes):
        """
        Add each theme

        :param str path_themes: Path to themes folder
        """
        api_themes = self._get_themes_via_api()

        for t in api_themes:
            name = t['name']
            git_url = t['git_url']
            try:
                theme = _Theme(name, git_url)
            except Exception:  # No exception from a theme should prevent website from building
                self._print_warning("FAILED TO ADD THEME: {}".format(name))
                print("{} - {}".format(name, git_url))
                traceback.print_exc()
            else:
                self._add_single_theme(path_themes, theme)

    @staticmethod
    def _get_themes_via_api():
        """
        Get list of themes from the api

        :return: List of themes
        :rtype: dict
        """
        url = "https://api.github.com/repos/{}/contents/".format(GITHUB_THEMES_REPO)
        api_themes = api_get(url)
        api_themes = [file for file in api_themes if file['name'].startswith('lektor-theme-')]
        return api_themes

    def _add_single_theme(self, path_themes, theme):
        """
        Add a single theme's content

        :param str path_themes: Path to themes folder
        :param _Theme theme: Theme to add
        """
        path_theme_dir = self._add_theme_dir(path_themes, theme.repo_name)
        self._add_theme_contents_lr(path_theme_dir, theme)
        self._add_theme_images(path_theme_dir, theme)

    @staticmethod
    def _add_theme_dir(path_themes, name):
        """
        Add directory for theme

        :param str path_themes: Path to themes folder
        :param str name: Name of folder
        :return: Path to new folder
        :rtype: str
        """
        path = os.path.join(path_themes, name)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def _add_theme_contents_lr(path_theme_dir, theme):
        """
        Add the theme's contents.lr file

        :param str path_theme_dir: Path to theme's folder
        :param _Theme theme: The Theme
        """
        text = ""
        text += "name: {}\n".format(theme.name)
        text += "---\n"
        text += "url: {}\n".format(theme.homepage)
        text += "---\n"
        text += "author: {}\n".format(theme.author_name)
        text += "---\n"
        text += "author_url: {}\n".format(theme.author_homepage)
        text += "---\n"
        text += "cover_image: 1 - homepage.png\n"
        text += "---\n"
        text += "description:\n\n{}".format(theme.description)

        path = os.path.join(path_theme_dir, 'contents.lr')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    def _add_theme_images(self, path_theme_dir, theme):
        """
        Add images from theme

        :param str path_theme_dir: Path to theme's folder
        :param _Theme theme: The Theme
        """
        for image in theme.images:
            name = image['path']
            name = self._get_new_image_name(name)
            api_url = image['url']
            image_bytes = self._download_image(api_url)
            path = os.path.join(path_theme_dir, name)
            with open(path, 'wb') as f:
                f.write(image_bytes)

    @staticmethod
    def _get_new_image_name(name):
        """
        Gets the new name for the image

        :param str name: Current name of image file
        :return: New name of image file
        :rtype: str
        """
        new_names = {
            'homepage.png': '1 - homepage.png',
        }

        return new_names.get(name, name)

    @staticmethod
    def _download_image(api_url):
        """
        Download image

        :param str api_url: API URL of image
        :return: Bytes of image
        :rtype: bytes
        """
        response = api_get(api_url)
        image_bytes = response['content']
        image_bytes = base64.b64decode(image_bytes)
        return image_bytes


def api_get(url):
    """
    Get API response

    :param str url: URL to get
    :return: JSON response
    :rtype: dict
    """
    try:
        github_token = os.environ['GITHUB_TOKEN']
    except KeyError:
        raise Exception("Cannot access GitHub API without token. Add env var 'GITHUB_TOKEN'")

    headers = {
        'Authorization': "token {}".format(github_token),
        'Cache-Control': "no-cache",
    }
    response = requests.get(url, headers=headers)
    _check_api_response(response)
    return response.json()


def _check_api_response(response):
    """Checks API response and raises exception if it failed"""
    if not response.ok:
        if response.status_code == 401:
            print("Error 401: GITHUB_TOKEN does not have correct permissions. {}".format(response.text))
        else:
            print(
                "GitHub API call failed when building Themes.\n"
                "Check URL and verify GITHUB_TOKEN env var is correct with valid permissions.\n{}".format(response.text)
            )
    response.raise_for_status()


class _Theme(object):
    """A single theme"""

    def __init__(self, repo_name, api_url):
        """
        init

        :param str repo_name: Name of repo
        :param str api_url: API url for repo
        """
        self.repo_name = repo_name
        self.api_url = api_url
        self.api_response = api_get(api_url)
        self.listing = self.api_response['tree']  # type: dict
        self.images = self._load_images()  # type: List[dict]

        self.ini = self._load_ini()  # type: ConfigParser
        theme_data = self.ini['theme']
        self.name = theme_data['name']  # type: str
        self.description = theme_data['description']  # type: str
        self.homepage = theme_data['homepage']  # type: str
        author_data = self.ini['author']
        self.author_name = author_data['name']  # type: str
        self.author_homepage = author_data['homepage']  # type: str

    def __repr__(self):
        return "<Theme {}>".format(self.name)

    def _load_images(self):
        """
        Loads image info from the API

        :return: Data of images
        :return: list[dict]
        """
        try:
            images_api = [l for l in self.listing if l['path'] == 'images' and l['type'] == 'tree'][0]
        except IndexError:
            raise IndexError("Theme did not contain images folder.\n{}".format(self.listing))

        api_url = images_api['url']
        images = api_get(api_url)['tree']
        accepted_extensions = ('png', 'jpg', 'jpeg')
        images = [image for image in images if image['path'].split('.')[-1] in accepted_extensions]
        self._assert_required_images(images)
        return images

    @staticmethod
    def _assert_required_images(images):
        """
        Raises exception if minimum required image do not exist

        :param list[dict] images: Data of images
        """
        required_images = ['homepage.png']

        for image_name in required_images:
            try:
                [i for i in images if i['path'] == image_name][0]
            except IndexError:
                raise IndexError("Theme does not contain image '{}'".format(image_name))

    def _load_ini(self):
        """
        Load theme's ini file

        :return: Loaded config
        :rtype: ConfigParser
        """
        try:
            ini_api = [l for l in self.listing if l['path'] == 'theme.ini' and l['type'] == 'blob'][0]
        except IndexError:
            raise IndexError("Theme did not contain theme.ini.\n{}".format(self.listing))

        api_url = ini_api['url']

        base64_content = api_get(api_url)['content']
        content = base64.b64decode(base64_content)
        content = content.decode('utf-8')
        config = ConfigParser()
        config.read_string(content)
        return config
