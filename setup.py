import semver
from setuptools import setup
from setuptools import find_packages

version = semver.VersionInfo.parse('0.21.0')

setup(name='purenes',
      version=str(version),
      description='A NES emulator in Python',
      author='Stephen Brady',
      author_email='stephen.brady86@gmail.com',
      install_requires=["typing_extensions==4.1.1"],
      test_requires=[
            "pytest>=7.1.1",
            "pytest-cov==3.0.0",
            "pytest-mock==3.7.0"
      ],
      setup_requires=[
            "semver>=2.13.0",
            "sphinx==4.5.0",
            "furo==2022.3.4"
      ],
      packages=find_packages(exclude=["tests"]),
      )
