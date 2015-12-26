from setuptools import setup

setup(
    name='lektor-markdown-admonition',
    version='0.1',
    author=u'Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    license='MIT',
    py_modules=['lektor_markdown_admonition'],
    entry_points={
        'lektor.plugins': [
            'markdown-admonition = lektor_markdown_admonition:MarkdownAdmonitionPlugin',
        ]
    }
)
