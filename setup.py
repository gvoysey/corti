from distutils.core import setup

# makes __version__ a local variable
exec(open('verhulst_model_core/_version.py').read())

setup(
    name='verhulst-model-core',
    version=__version__,
    packages=['verhulst_model_core'],
    package_dir={'verhulst_model_core': 'verhulst_model_core'},
    package_data={'verhulst_model_core': ['resources/*']},
    url='https://github.com/AuditoryBiophysicsLab/verhulst-model-core',
    license='',
    author='Sarah Verhulst',
    author_email='sarah.verhulst@uni-oldenburg.de',
    description='A nonlinear time-domain cochlear model for transient stimulation and human otoacoustic emission',
    install_requires=[
        'blessings >= 1.6',
        'numpy >= 1.10',
        'scipy >= 0.16',
        'progressbar2 > 3.6',
    ]

)
