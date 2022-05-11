from setuptools import setup
from setuptools import find_packages

__version__ = "0.29.0"

setup(name='purenes',
      version=__version__,
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
            "sphinx==4.5.0",
            "furo==2022.3.4",
            "python-semantic-release==7.28.1"
      ],
      packages=find_packages(exclude=["tests", "tests.*"]),
      )
