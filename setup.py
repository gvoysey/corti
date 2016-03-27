from setuptools import setup

# makes __version__ a local variable
exec(open('verhulst_runner/_version.py').read())
# http://python-packaging.readthedocs.org/en/latest/command-line-scripts.html
setup(
    name='verhulst-runner',
    version=__version__,
    packages=['verhulst_runner', 'verhulst_runner.analysis', 'verhulst_runner.utilities',
              'verhulst_runner.utilities.stimulus_generator'],

    url='https://github.com/gvoysey/thesis-code',
    license='',
    author='Graham Voysey',
    author_email='gvoysey@bu.edu',
    description='A wrapper around https://github.com/AuditoryBiophysicsLab/verhulst-model-core'
)
