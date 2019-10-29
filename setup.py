import os
from codecs import open

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'readme.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(
  name='exnihilo',
  version='0.0.1',
  description='DSL for procedural content generation and worldbuilding',
  long_description=long_description,
  url='http://github.com/dariusf/exnihilo',
  author='Darius Foo',
  author_email='darius.foo.tw@gmail.com',
  license='MIT',
  packages=find_packages(),
  include_package_data=True,
  entry_points={
    'console_scripts': [
      'exnihilo=exnihilo.cli:main'
    ]
  },
  install_requires=[
    'clyngor'
  ]
)
