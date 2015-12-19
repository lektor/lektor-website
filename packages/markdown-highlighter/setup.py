from setuptools import setup

setup(
    name='lektor-markdown-highlighter',
    version='0.1',
    py_modules=['lektor_markdown_highlighter'],
    entry_points={
        'lektor.plugins': [
            'markdown-highlighter = lektor_markdown_highlighter:MarkdownHighlighterPlugin',
        ]
    },
    install_requires=[
        'Pygments',
    ]
)
