#Verhulst Model (Core functionality)

This repository contains the core functionality of the model developed by Dr. Sarah Verhulst (<sarah.verhulst@uni-oldenburg.de>).  It is described in the following publications: 

1.  Verhulst, S., Bharadwaj, H. M., Mehraei, G., Shera, C. A., and Shinn-Cunningham, B. G. (2015). “Functional modeling of the human auditory brainstem response to broadband stimulations,” J. Acoust. Soc. Am., 138, 1637–1659. doi:10.1121/1.4928305
2. Verhulst, S., Dau, T. and Shera, C.A. (2012). Nonlinear time-domain cochlear model for transient stimulation and human otoacoustic emission. Journal of the Acoustical Society of America, 132 (6), 3842-3848.

This repository contains a lightly modified version of this model that was used by Dr. Goldbarg  Mehraei in her dissertation: 

1.  Mehraei, G. (2015). Auditory brainstem response latency in noise as a marker of cochlear synaptopathy Massachusetts Institute of Technology.

**This repository does _not_ include an implementation of the brainstem and midbrain component described in the above publications.**  
For a reference version of that brainstem component, please consult Nelson, P. C., and Carney, L. H. (2004). “A phenomenological model of peripheral and central neural responses to amplitude-modulated tones,” J. Acoust. Soc. Am., 116, 2173. doi:10.1121/1.1784442 . 

An implementation of the Nelson & Carney 2004 component in python is present in @gvoysey's [thesis repository](https://github.com/gvoysey/thesis-code).

## Requirements and Installation
verhulst-model-core is implemented and tested in python >3.4. 
**There is currently no windows support.  Consider using Docker, a mac, or a linux box.**  

To install, using python 3.x, simply `pip install git+https://github.com/AuditoryBiophysicsLab/verhulst-model-core.git@v0.9.3`
## Usage 
Once installed, reference and use as a standard python module: 
```python
import verhulst_model_core
```

This repository is not really meant to run independently of a framework built on top of it; API documentation is not yet complete.

## Subsequent Changes
The code in this repository has been subsequently refactored by Graham Voysey (gvoysey@bu.edu), to incorporate it into a modeling framework being used in his [M.S. thesis](https://github.com/gvoysey/thesis-code) at Boston University.   Changes include: 

1. PEP-8 compliance (somewhat)
2. Addition of `core.py`, a container for tracking operational parameters such as location of starting poles. 
3. Support for a progress bar display during computation of each BM section
4. Minor name changes (e.g., `class cochlea_model` --> `class CochleaModel`).
5. Refactoring into a python package

On 22 March 2016, @gvoysey and @GerardEncina diffed original versions of model code to the code in this model as of [9177c1249] (https://github.com/AuditoryBiophysicsLab/verhulst-model-core/commit/9177c12498bf92790d203a6a87dbe54c39e1f0c4) and found them to be substantively identical.  

Later on 22 March 2016, @gvoysey, per the suggestion of Mehraei, modified [this](https://github.com/AuditoryBiophysicsLab/verhulst-model-core/blob/9177c12498bf92790d203a6a87dbe54c39e1f0c4/ANF_Sarah.py#L20) line to change the threshold difference between low- and high- spontaneous rate fibers to 20dB re 20uPa (from 40 dB). 
## Original versions 
Original, completely unmodified versions of the code exist in the branch [legacy](https://github.com/AuditoryBiophysicsLab/verhulst-model-core/tree/legacy). 
