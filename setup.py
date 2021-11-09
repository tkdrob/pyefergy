#!/usr/bin/env python
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyefergy',
    version='0.1.5',
    author='Robert Hillis',
    author_email='tkdrob4390@yahoo.com',
    description='An API library for Efergy energy meters.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tkdrob/pyefergy',
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp>=3.4.4',
        'iso4217>=1.2.20150619',
        'pytz',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
