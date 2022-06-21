__author__ = "Viraj Kanwade"
__email__ = "virajk.oib@gmail.com"
__copyright__ = "Copyright 2022, Viraj Kanwade"

import os
from setuptools import setup, find_packages

this_dir = os.path.abspath(os.path.dirname(__file__))
REQUIREMENTS = filter(None, open(os.path.join(this_dir, 'requirements.txt')).read().splitlines())

setup(
    name='wsh_async',
    author=__author__,
    author_email=__email__,
    license="MIT",
    url="https://wsh_async.readthedocs.org",
    zip_safe=False,
    entry_points = {
        'console_scripts': ['wsh_async=wsh_async.wsh_async:wsh_async_run'],
    },
    version='0.0.1',
    install_requires=list(REQUIREMENTS),
    classifiers=[k for k in open('CLASSIFIERS').read().split('\n') if k],
    description='An interactive WebSocket shell',
    long_description=open('README').read() + open('CHANGELOG').read(),
    packages=find_packages(exclude=["tests*"])
)