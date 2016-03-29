from distutils.core import setup


# makes __version__ a local variable
exec(open('verhulst_runner/_version.py').read())
# http://python-packaging.readthedocs.org/en/latest/command-line-scripts.html
setup(
    name='verhulst-runner',
    version=__version__,
    packages=['verhulst_runner',
              'verhulst_runner.analysis',
              ],
    package_dir={'verhulst_runner': 'verhulst_runner'},
    package_data={'verhulst_runner': ['resources/*']},
    scripts=['scripts/verhulst_model',
             'scripts/stimulus_generator'],
    url='https://github.com/gvoysey/thesis-code',
    license='',
    author='Graham Voysey',
    author_email='gvoysey@bu.edu',
    description='A wrapper around https://github.com/AuditoryBiophysicsLab/verhulst-model-core',
    install_requires=[
        'docopt >= 0.6',
        'matplotlib >= 1.5',
        'numpy >= 1.10',
        'progressbar2 >= 3.6',
        'PyYAML > 3.10'
    ]
)
