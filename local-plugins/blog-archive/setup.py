from setuptools import setup

setup(
    name='lektor-blog-archive',
    version='0.1',
    author=u'Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    license='MIT',
    py_modules=['lektor_blog_archive'],
    entry_points={
        'lektor.plugins': [
            'blog-archive = lektor_blog_archive:BlogArchivePlugin',
        ]
    }
)
