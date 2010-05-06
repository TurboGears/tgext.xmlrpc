# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='tgext.xmlrpc',
    version='0.6',
    description='TurboGears XMLRPC Controller',
    author='Michael J. Pedersen',
    author_email='m.pedersen@icelus.org',
    url='http://bitbucker.org/pedersen/tgext.xmlrpc',
    install_requires=[
        "TurboGears2 >= 2.1b2",
        "decorator",
        ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['tgext'],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    message_extractors={'tgextxmlrpc': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},
    entry_points="""
    
    """,
)
