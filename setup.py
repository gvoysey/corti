from distutils.core import setup

setup(
    name='verhulst-model-core',
    version='0.9.0',
    packages=['verhulst_model_core'],
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
