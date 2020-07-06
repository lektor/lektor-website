from setuptools import setup

setup(
    name='lektor-project-themes',
    version='0.1',
    author='Andrew Shay',
    author_email='andrew.shay@andrewshay.me',
    license='MIT',
    py_modules=['lektor_project_themes'],
    install_requires=[
        'requests',
    ],
    entry_points={
        'lektor.plugins': [
            'project-themes = lektor_project_themes:ProjectThemesPlugin',
        ]
    }
)
