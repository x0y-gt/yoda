from setuptools import setup, find_packages

setup(
  name='yoda',
  version='0.1',
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'Click',
    'Plumbum',
  ],
  entry_points='''
    [console_scripts]
    yoda=yoda.main:yoda
  ''',
)
