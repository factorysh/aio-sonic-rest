from setuptools import setup

setup(
    name='sonic_rest',
    author='Mathieu Lecarme',
    version='0.1.0',
    packages=['sonic_rest'],
    keywords=['sonic', 'search', 'asyncio'],
    url='https://github.com/facttorysh/aio-simple-search',
    license='3 terms BSD licence',
    long_description='',
    description='REST for sonic',
    install_requires=[
        'sonic-client',
        'asonic',
        'aiohttp[speedups]',
    ],
    extras_require={
        'tests': ['pytest', 'pytest-aiohttp'],
    },
)
