import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = "commoner",
    version = "0.1",
    packages = ['commoner', 'commoner_i',],
    package_dir = {'':'src'},

    entry_points = {

        'console_scripts' : [
            'noop = commoner.scripts:noop',
            'idjango = commoner_i.scripts:manage',
            'renewals = commoner.scripts.send_renewals:main',
            'invites = commoner.scripts.send_invites:main',
            ]
        },

    install_requires = ['setuptools',
                        'Django',
                        'python-openid',
                        'MySQL-python',
                        'PILwoTK',
                        'pycrypto',
                        'pysqlite',
                        'lxml',
                        'rdfadict',
                        'simplejson',
                        'python-dateutil',
                        'South',
                        ],
                        
    dependency_links=['http://download.zope.org/distribution/',
                      'http://labs.creativecommons.org/~nathan/source/'],

    include_package_data = True,
    zip_safe = True,

    author = 'Nathan R. Yergler',
    author_email = 'nathan@creativecommons.org',
    description = '',
    license = 'AGPL 3.0',
    url = 'http://wiki.creativecommons.org/',

    )
