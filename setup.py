from setuptools import setup, find_packages
import yummy

install_requires = [
    'Django>=1.4,<1.5',
    'south>=0.7',
]

tests_require = [
    'nose',
    'coverage',
    'mock',
    'PIL',
]

long_description = open('README.rst').read()

setup(
    name='Django-Yummy',
    version=yummy.__versionstr__,
    description='Recipes application based on Django framework',
    long_description=long_description,
    author='Sanoma Media',
    author_email='online-dev@sanoma.cz',
    license='BSD',
    url='https://github.com/SanomaCZ/django-yummy',

    packages=find_packages(
        where='.',
        exclude=('doc', 'tests',)
    ),

    include_package_data=True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=install_requires,

    test_suite='nose.collector',
    tests_require=tests_require,
)
