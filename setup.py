# -*- encoding: utf-8 -*-
import setuptools

with open('README.md', 'r') as file:
    readme_contents = file.read()

setuptools.setup(
    name='pysofar',
    version='0.1.6',
    license='Apache 2 Licesnse',
    install_requires=[
        'requests',
        'python-dotenv'
    ],
    description='Python client for interfacing with the Sofar Wavefleet API to access Spotter Data',
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    author='Rufus Sofar',
    author_email='sofaroceangithubbot@gmail.com',
    url='https://github.com/wavespotter/wavefleet-client-python',

    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    project_urls={
        'Sofar Ocean Site': 'https://www.sofarocean.com',
        'Spotter About': 'https://www.sofarocean.com/products/spotter',
        'Spotter Data FAQ': 'https://www.sofarocean.com/posts/spotter-data-subscription-and-storage',
        'Sofar Dashboard': 'https://spotter.sofarocean.com/',
        'Sofar Api FAQ': 'https://spotter.sofarocean.com/api'
    }
)
