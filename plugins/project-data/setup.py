from setuptools import setup

setup(
    name='lektor-project-data',
    version='0.1',
    author='Joseph Nix',
    author_email='nixjdm@terminallabs.com',
    license='MIT',
    py_modules=['lektor_project_data'],
    install_requires=[
        'requests',
        'readme_renderer[md]',
    ],
    entry_points={
        'lektor.plugins': [
            'project-data = lektor_project_data:ProjectDataPlugin',
        ]
    }
)
