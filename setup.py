from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sif',
    version='0.0.1a0',
    description='Microservices framework with the soul of a wolf',
    long_description=long_description,
    url='https://github.com/rudineirk/sif',
    author='Rudinei Goi Roecker',
    author_email='rudinei.roecker@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='sif microservices framework',
    packages=find_packages(exclude=[
        'contrib',
        'docs',
        'tests',
        'examples',
    ]),
)
