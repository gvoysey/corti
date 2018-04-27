import numpy as np
from Cython.Build import cythonize
from setuptools import setup, find_packages, Extension
import versioneer

extensions = [
    Extension("corti.zilany2014._zilany2014",
              [
                  "corti/zilany2014/_zilany2014.pyx",
                  "corti/zilany2014/model_IHC.c",
                  "corti/zilany2014/model_Synapse.c",
                  "corti/zilany2014/complex.c"
              ]
              )
]

setup(name='corti',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      packages=find_packages(),
      package_data={
          'corti': ['resources/*',
                    'resources/tone_in_noise/*']
      },
      entry_points={
          'console_scripts': [
              'corti = corti.__main__:main'
              , 'stimulus_generator = corti.stimulus_generator:main'
              , 'tone_in_noise = corti.tone_in_noise:main'
          ]
      },
      url='https://github.com/gvoysey/corti',
      license='GPL',
      ext_modules=cythonize(extensions),
      include_dirs=[np.get_include()],
      author='Graham Voysey',
      author_email='gvoysey@bu.edu',
      description='An auditory modeling environment for the Zilany 2014 periphery, Verhulst 2015 periphery, '
                  'Nelson Carney 2004 brainstem and Carney 2015 brainstem models.',
      install_requires=[
          'docopt >= 0.6',
          'matplotlib >= 1.5',
          'blessed >= 1.14',
          'numpy >= 1.10',
          'progressbar2 >= 3.6',
          'PyYAML > 3.10',
          'pandas',
          'cython',
          'pypet',
      ],
      tests_require=[
          'pytest',
          'hypothesis'
      ],
      test_suite="py.test")
