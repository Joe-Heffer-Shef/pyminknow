import setuptools

with open('README.md') as file:
    readme = file.read()

setuptools.setup(
    name='pyminknow',
    version='0.0.13',
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
        'grpcio~=1.27',
        'protobuf~=3.11',
        'grpcio-tools~=1.28',
    ]
)
