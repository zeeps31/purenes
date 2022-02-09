from setuptools import setup
from setuptools import find_packages

setup(name='nespy',
      version='0.1.0',
      description='A NES emulator in Python',
      author='Stephen Brady',
      author_email='stephen.brady86@gmail.com',
      packages=find_packages(exclude=["tests"]),
      )
