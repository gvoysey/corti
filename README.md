Verhulst Model (Core functionality)
=======

This repository contains the core functionality of the model developed by Dr. Sarah Verhulst (<sarah.verhulst@uni-oldenburg.de>).  It is described in the following publications: 

1.  Verhulst, S., Bharadwaj, H. M., Mehraei, G., Shera, C. A., and Shinn-Cunningham, B. G. (2015). “Functional modeling of the human auditory brainstem response to broadband stimulations,” J. Acoust. Soc. Am., 138, 1637–1659. doi:10.1121/1.4928305
2. Verhulst, S., Dau, T. and Shera, C.A. (2012). Nonlinear time-domain cochlear model for transient stimulation and human otoacoustic emission. Journal of the Acoustical Society of America, 132 (6), 3842-3848.

This repository contains the version of this code that was used by Dr. Goldbarg  Mehraei in her dissertation: 

1.  Mehraei, G. (2015). Auditory brainstem response latency in noise as a marker of cochlear synaptopathy Massachusetts Institute of Technology.

It has been subsequently refactored by Graham Voysey (gvoysey@bu.edu), to incorporate it into a modeling framework being used in his [M.S. thesis](https://github.com/gvoysey/thesis-code) at Boston University.   Changes include: 

1. PEP-8 compliance (somewhat)
2. Addition of `core.py`, a container for tracking operational parameters such as location of starting poles. 
3. Support for a progress bar display during computation of each BM section
4. Minor name changes (e.g., `class cochlea_model` --> `class CochleaModel`).


