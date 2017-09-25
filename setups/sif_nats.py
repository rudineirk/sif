from codecs import open
from os import path

from setuptools import setup

basedir = path.abspath(path.join(path.dirname(__file__), '../'))

with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(basedir, 'VERSION'), encoding='utf-8') as f:
    version = f.read().strip()

setup(
    name='sif-nats',
    version=version,
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
    keywords='sif microservices framework nats',
    packages=['sif_nats'],
    install_requires=[
        'asyncio-nats-client',
        'msgpack-python',
    ],
)
