from setuptools import setup, find_packages

try:
    with open('LICENSE.txt', 'r') as f:
        _license = f.read()
except:
    _license = ''

try:
    with open('README.md', 'r') as f:
        _readme = f.read()
except:
    _readme = ''

setup(
  name='financePy',
  packages=find_packages(),
  version='0.2.1',
  description='+ una provae',
  author='Michelangelo Conserva',
  author_email='mom',
  license=_license,
  long_description=_readme,
  url='no',
  download_url='https://github.com/MichelangeloConserva/prova/releases',
  install_requires=['setuptools', 'pandas', 'requests','quandl','bs4','xlrd','scipy'],
)
