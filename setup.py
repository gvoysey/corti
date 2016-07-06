import numpy as np
from Cython.Build import cythonize
from setuptools import setup, find_packages, Extension

# makes __version__ a local variable
exec(open('core/_version.py').read())
# http://python-packaging.readthedocs.org/en/latest/command-line-scripts.html
extensions = [
    Extension("core.zilany2014._zilany2014",
              [
                  "core/zilany2014/_zilany2014.pyx",
                  "core/zilany2014/model_IHC.c",
                  "core/zilany2014/model_Synapse.c",
                  "core/zilany2014/complex.c"
              ]
              )
]

setup(name='corti',
      version=__version__,
      packages=find_packages(),
      package_data={
          'core': ['resources/*',
                   'resources/tone_in_noise/*']
      },
      scripts=['scripts/corti',
               'scripts/stimulus_generator',
               'scripts/tone_in_noise.py'],
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
          'pypet'
      ],
      tests_require=[
          'pytest',
          'hypothesis'
      ],
      test_suite="py.test")
