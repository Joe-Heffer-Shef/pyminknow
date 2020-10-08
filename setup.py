"""
To build from source:

python setup.py sdist bdist_wheel
twine upload dist/* --skip-existing
"""

import setuptools

with open('README.md') as file:
    readme = file.read()

setuptools.setup(
    name='pyminknow',
    version='1.0.4',
    author="Joe Heffer",
    author_email="j.heffer@sheffield.ac.uk",
    description="This service mimics a Nanopore minKNOW gene sequencing device by using its gRPC interface.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Joe-Heffer-Shef/pyminknow",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'minknow-api~=4.0',
    ],
)
