# -*- coding: utf-8 -*-
import re
from lektor.pluginsystem import Plugin


_prefix_re = re.compile(r'^\s*(!{1,4})\s+')

CLASSES = {
    1: 'note',
    2: 'info',
    3: 'tip',
    4: 'warning',
}


class AdmonitionMixin(object):

    def paragraph(self, text):
        match = _prefix_re.match(text)
        if match is None:
            return super(AdmonitionMixin, self).paragraph(text)
        level = len(match.group(1))
        return '<div class="admonition admonition-%s"><p>%s</p></div>' % (
            CLASSES[level],
            text[match.end():]
        )


class MarkdownAdmonitionPlugin(Plugin):
    name = u'Markdown Admonition'
    description = u'Adds admonitions to markdown.'

    def on_markdown_config(self, config, **extra):
        config.renderer_mixins.append(AdmonitionMixin)
