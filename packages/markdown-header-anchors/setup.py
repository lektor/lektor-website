from setuptools import setup

setup(
    name='lektor-markdown-header-anchors',
    version='0.1',
    py_modules=['lektor_markdown_header-anchors'],
    entry_points={
        'lektor.plugins': [
            'markdown-header-anchors = lektor_markdown_header_anchors:MarkdownHeaderAnchorsPlugin',
        ]
    }
)
