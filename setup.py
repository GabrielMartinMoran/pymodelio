from setuptools import setup, find_packages

VERSION = '0.0.4'

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='pymodelio',
    version=VERSION,
    author='Gabriel Martín Moran',
    author_email='moran.gabriel.95@gmail.com',
    description='A simple Python module for performing model validations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/GabrielMartinMoran/pymodelio',
    packages=find_packages(include=['pymodelio', 'pymodelio.*'])
)
