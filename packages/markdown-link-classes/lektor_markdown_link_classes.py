import re
from lektor.pluginsystem import Plugin
from markupsafe import escape


_class_re = re.compile(r'\s+:([a-zA-Z0-9_-]+)')


def split_classes(text):
    classes = []
    def _handle_match(match):
        classes.append(match.group(1))
        return ''
    text = _class_re.sub(_handle_match, text).replace('\\:', ':')
    return text, classes


class MarkdownLinkClassesPlugin(Plugin):
    name = 'Markdown Link Classes'
    description = 'Adds the ability to add classes to links.'

    def on_markdown_config(self, config, **extra):
        class LinkClassesMixin(object):
            def link(renderer, link, title, text):
                text, classes = split_classes(text)
                if link.startswith('javascript:'):
                    link = ''
                attr = ['href="%s"' % escape(link)]
                if title:
                    attr.append('title="%s"' % escape(title))
                if classes:
                    attr.append('class="%s"' % ' '.join(
                        escape(x) for x in classes))
                return '<a %s>%s</a>' % (' '.join(attr), text)
        config.renderer_mixins.append(LinkClassesMixin)
