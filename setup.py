from distutils.core import setup

setup(
    name='verhulst-runner',
    version='',
    packages=['verhulst_runner', 'verhulst_runner.analysis', 'verhulst_runner.utilities',
              'verhulst_runner.utilities.stimulus_generator'],
    url='https://github.com/gvoysey/thesis-code',
    license='',
    author='Graham Voysey',
    author_email='gvoysey@bu.edu',
    description='A wrapper around https://github.com/AuditoryBiophysicsLab/verhulst-model-core'
)
