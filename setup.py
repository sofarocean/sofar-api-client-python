import setuptools

with open('README.md', 'r') as file:
    readme_contents = file.read()

setuptools.setup(
    name='pywavefleet',
    version='0.1',
    scripts=[],
    author='Rufus Sofar',
    author_email='sofaroceangithubbot@gmail.com',
    description='Python client for interfacing with the Sofar Wavefleet API to access Spotter Data',
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    url='https://github.com/wavespotter/wavefleet-client-python',
    packages=setuptools.find_packages(),
    namespace_packages=['pywavefleet'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: LICENSE",
        "Operating System :: OS Independent"
    ]
)
