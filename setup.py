import semver
from setuptools import setup
from setuptools import find_packages

version = semver.VersionInfo.parse('0.2.0')

setup(name='purenes',
      version=str(version),
      description='A NES emulator in Python',
      author='Stephen Brady',
      author_email='stephen.brady86@gmail.com',
      setup_requires=["semver>=2.13.0"],
      packages=find_packages(exclude=["tests"]),
      )
