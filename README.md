# thesis-code
This repository contains a runtime environment for models of the auditory periphery, brainstem, and midbrain.  It is implemented in Python 3.x, and currently supports OSX and Linux. 

The goal of this work is to explore the effects of Auditory Neuropathy on representations of complex sounds throughout
the early stages of the auditory system. 

The auditory periphery is simulated using the model developed by Verhulst et. al., hosted [here](https://github.com/AuditoryBiophysicsLab/verhulst-model-core). 

The model(s) of the auditory brainstem and midbrain are adapted from Nelson and Carney (2004), Carney (2015), and Zilany and Bruce (2014). 

# Installation 
this repository may be installed "from source" with `pip`, the python package manager: 
```
pip install git+https://github.com/gvoysey/thesis-code.git@<TAG>
```
where `<TAG>` is a valid [release](https://github.com/gvoysey/thesis-code/releases)

or, if you have cloned this repository locally and are running it in a virtual environment (like you should be!):

`env/bin/pip install git+file:///path/to/your/git/repo@mybranch` or `@mytag`. 
# Usage
 - `stimulus_generator --help` configure stimuli from WAV files or generate stimuli configuration templates.
 - `verhulst_model --help` load stimuli, configure model parameters, run model, plot output.
  
# Documentation 
 - Real Soon Now.