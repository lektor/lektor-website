import re
from lektor.pluginsystem import Plugin
from markupsafe import escape
from mistune import __version__ as mistune_version


_class_re = re.compile(r'\s+:([a-zA-Z0-9_-]+)')


def split_classes(text):
    classes = []
    def _handle_match(match):
        classes.append(match.group(1))
        return ''
    text = _class_re.sub(_handle_match, text).replace('\\:', ':')
    return text, classes


def render_link(link, text, title=None):
    text, classes = split_classes(text)
    if link.startswith('javascript:'):
        link = ''
    attr = [f'href="{escape(link)}"']
    if title:
        attr.append(f'title="{escape(title)}"')
    if classes:
        attr.append(f'class="{" ".join(map(escape, classes))}"')
    return f"<a {' '.join(attr)}>{text if text else link}</a>"


if mistune_version.startswith("0."):
    class LinkClassesMixin(object):
        def link(renderer, link, title, text):
            return render_link(link, text, title)
else:
    class LinkClassesMixin(object):
        def link(renderer, link, text="", title=None):
            return render_link(link, text, title)


class MarkdownLinkClassesPlugin(Plugin):
    name = 'Markdown Link Classes'
    description = 'Adds the ability to add classes to links.'

    def on_markdown_config(self, config, **extra):
        config.renderer_mixins.append(LinkClassesMixin)
