from setuptools import setup, find_packages
from pymodelio import __version__

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='pymodelio',
    version=__version__,
    author='Gabriel Martín Moran',
    author_email='moran.gabriel.95@gmail.com',
    description='A simple Python module for defining domain models and performing validations against them',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/GabrielMartinMoran/pymodelio',
    packages=find_packages(include=['pymodelio', 'pymodelio.*'])
)
