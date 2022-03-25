import semver
from setuptools import setup
from setuptools import find_packages

version = semver.VersionInfo.parse('0.4.1')

setup(name='purenes',
      version=str(version),
      description='A NES emulator in Python',
      author='Stephen Brady',
      author_email='stephen.brady86@gmail.com',
      install_requires=["numpy==1.21.5", "typing_extensions==4.1.1"],
      test_requires=["pytest>=7.1.1", "pytest-cov==3.0.0"],
      setup_requires=["semver>=2.13.0"],
      packages=find_packages(exclude=["tests"]),
      )
