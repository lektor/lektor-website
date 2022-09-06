from setuptools import setup

setup(
    name='lektor-jinja-globals',
    author="Jeff Dairiki",
    author_email="dairiki@dairiki.org",
    description="Custom Jinja globals and filters for lektor-website",
    keywords="Lektor plugin",
    license="MIT",
    py_modules=["lektor_jinja_globals"],
    version='0.1',
    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
    ],
    entry_points={
        'lektor.plugins': [
            'jinja-globals = lektor_jinja_globals:JinjaGlobalsPlugin',
        ]
    }
)
