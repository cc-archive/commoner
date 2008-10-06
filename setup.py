
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
            'register = commoner.registration.scripts:register',
            'welcome = commoner.registration.scripts:welcome',
            'django = commoner.scripts:manage',
            'noop = commoner.scripts:noop',
            'idjango = commoner_i.scripts:manage',
            ]
        },
    
    install_requires = ['setuptools',
                        'Django',
                        'python-openid',
                        'flup',
                        'MySQL-python',
                        'PILwoTK',
                        'pycrypto',
                        # 'cc.license',
                        ],

    dependency_links=['http://download.zope.org/distribution/',],

    include_package_data = True,
    zip_safe = True,

    author = 'Nathan R. Yergler',
    author_email = 'nathan@creativecommons.org',
    description = '',
    license = 'AGPL 3.0',
    url = 'http://wiki.creativecommons.org/',

    )
