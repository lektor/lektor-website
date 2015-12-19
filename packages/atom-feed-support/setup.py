from setuptools import setup

setup(
    name='lektor-atom-feed-support',
    version='0.1',
    author=u'Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    license='MIT',
    py_modules=['lektor_atom_feed_support'],
    entry_points={
        'lektor.plugins': [
            'atom-feed-support = lektor_atom_feed_support:AtomFeedSupportPlugin',
        ]
    }
)
