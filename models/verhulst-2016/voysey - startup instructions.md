Please keep the folder structure as is, you'll have to run the model in two steps:

1.  RUN_BMAM.m makes the stimuli and runs the model up until AN. After compilation of trading.so, you can just run this .m file and it should create a NHClicks.mat file in the out folder

2.  then go to the CNIC folder and run the ICwaveratio.m file for the CN and IC model.

# Compilation on windows
`tridiag.so` can successfully be built and run on windows 7 64-bit.

1.  Ensure that cygwin is installed, and that the directory containing `cygwin1.dll` ( normally `C:\cygwin\bin`) is on the windows `$PATH`. 
2.  Ensure that python3 with numpy and scipy is installed and similarly on the path.
3. In the project root directory, open a cygwin bash terminal and : 
  ```bash
  gcc -shared -m32 -o tridiag.so cochlea_utils.c
  ```
  which should exit cleanly and silently.  `tridiag.so` was hanging on Numpy load_library until I upgraded to cygwin 2.4.1.  
