from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    README = readme_file.read()


setup(name='fetchcode',
    version='0.0.1',
    description='Smart and reliable library to download code from HTTP, FTP and VCS URL',
    long_description=README,
    license='Apache-2.0',
    packages=find_packages(),
    author='nexb and others',
    url='https://github.com/nexb/fetchcode'
)