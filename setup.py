from setuptools import setup, find_packages

REQUIRED_PYTHON = (3, 6, 4)
EXCLUDE_FROM_PACKAGES = []
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
  python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
  packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
  version='0.1',
  description='',
  author='Michelangelo Conserva',
  author_email='michelangelo.conserva@protonmail.com',
  license=_license,
  long_description=_readme,
  url='no',
  download_url='https://github.com/MichelangeloConserva/prova/releases',
  install_requires=['lxml','setuptools', 'pandas', 'requests','quandl','bs4','xlrd','scipy','selenium','matplotlib','html5lib==0.999999999'],
)
