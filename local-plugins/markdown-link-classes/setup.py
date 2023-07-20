from setuptools import setup

setup(
    name='lektor-markdown-link-classes',
    version='0.1',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    license='MIT',
    py_modules=['lektor_markdown_link_classes'],
    url='http://github.com/lektor/lektor',
    entry_points={
        'lektor.plugins': [
            'markdown-link-classes = lektor_markdown_link_classes:MarkdownLinkClassesPlugin',
        ]
    }
)
