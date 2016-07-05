#!/usr/bin/env python
"""
Tone in noise.  Runs many configurations of the tone in noise experiment used by Mehraei et. al. (2016) using a variety of models.

Usage:
    tone_in_noise.py -h | --help
    tone_in_noise.py --version
    tone_in_noise.py [--out <outpath>]

Options:
    -h --help           Show this screen and exit.
    --version           Display the version and exit.
    --out=<outpath>     Specify where pypet's output HDF5 database file should be saved.
                        [default: ~/pypet-output/tone-in-noise.hdf5]
"""
import glob
import sys
from datetime import datetime

from docopt import docopt
from importlib.machinery import SourceFileLoader
from os import path
from pypet import Environment
from pypet.utils.explore import cartesian_product

from scripts.base import scriptPath
from verhulst_runner.base import brain_consts, an_consts, periph_consts, modulePath

verhulst_path = path.join(scriptPath, "verhulst_model")
verhulst_model = SourceFileLoader('verhulst_model', verhulst_path).load_module()

periphery_type = '--peripheryType'
brainstem_type = '--brainstemType'
cf_weighting = '--no-cf-weighting'
wavfile = "--wavFile"
level = "--level"
neuropathy = "--neuropathy"


def tone_in_noise(traj: Environment.trajectory):
    commandstr = " ".join([periphery_type, traj.periphery, brainstem_type, traj.brainstem, neuropathy, traj.neuropathy,
                           traj.weighting, wavfile, traj.wavfile, level, str(traj.level), "--pypet"])
    print("Command String: " + commandstr)
    periphery, anr, brain = verhulst_model.main(commandstr)
    periphery = periphery[0]
    anr = anr[0]
    brain = brain[0]
    # do that natural naming thing here and then lots of add_results

    # Periphery results
    traj.f_add_result('periphery.timestamp', periphery.conf.run_timestamp.strftime("%d %b %y - %H:%M:%S"))
    traj.f_add_result('periphery.conf.modelType', periphery.conf.modelType.name)
    traj.f_add_result('periphery.conf.neuropathy', periphery.conf.degradation)
    traj.f_add_result('periphery.conf.cf_weighting', True if traj.weighting else False)
    # god this is ugly and brittle.
    try:
        snr = float(path.basename(traj.wavfile).split('-')[3][0:2])
    except IndexError:
        snr = float('Inf')
    traj.f_add_result('periphery.snr', snr, "")
    traj.f_add_result('periphery.stimulus', periphery.output[periph_consts.Stimulus], "")
    traj.f_add_result('periphery.high_spont', periphery.output[periph_consts.AuditoryNerveFiberHighSpont], "")
    traj.f_add_result('periphery.medium_spont', periphery.output[periph_consts.AuditoryNerveFiberMediumSpont], "")
    traj.f_add_result('periphery.low_spont', periphery.output[periph_consts.AuditoryNerveFiberLowSpont], "")

    # ANR result.
    traj.f_add_result('auditory_nerve.summed_response', anr[an_consts.SumANR], "Summed and weighted")

    # Brainstem results
    traj.f_add_result('brainstem.modeltype', traj.brainstem, "")

    traj.f_add_result('brainstem.wave1', brain[brain_consts.Wave1_AN], "")
    traj.f_add_result('brainstem.wave3', brain[brain_consts.Wave3_CN], "")
    traj.f_add_result('brainstem.wave5', brain[brain_consts.Wave5_IC], "")

    traj.f_add_result('brainstem.cn', brain[brain_consts.CNPopulation], "")
    traj.f_add_result('brainstem.ic', brain[brain_consts.ICPopulation], "")

    # free up some cache.


def main():
    args = docopt(__doc__)
    tic = datetime.now()
    wavpath = path.join(modulePath, "resources", "tone_in_noise")
    stimuli = [path.join(wavpath, i) for i in glob.glob(path.join(wavpath, "*.wav"))]
    outfile = path.realpath(path.expanduser(args["--out"]))
    env = Environment(trajectory='tone-in-noise',
                      filename=outfile,
                      overwrite_file=True,
                      file_title="Tone in noise at different SNR",
                      comment="some comment",
                      large_overview_tables="True",
                      )

    traj = env.trajectory
    traj.f_add_parameter('periphery', 'verhulst', comment="which periphery was used")
    traj.f_add_parameter('brainstem', 'nelsoncarney04', comment="which brainstem model was used")
    traj.f_add_parameter('weighting', "--no-cf-weighting ", comment="weighted CFs")
    traj.f_add_parameter('wavfile', '', comment="Which wav file to run")
    traj.f_add_parameter('level', 80, comment="stimulus level, spl")
    traj.f_add_parameter('neuropathy', "none", comment="")

    parameter_dict = {
        "periphery" : ['verhulst', 'zilany'],
        "brainstem" : ['nelsoncarney04', 'carney2015'],
        "weighting" : [cf_weighting, ""],
        "wavfile"   : stimuli,
        "level"     : [60, 80, 90],
        "neuropathy": ["none", "mild", "moderate", "severe", "ls-mild", "ls-moderate", "ls-severe"]
    }

    traj.f_explore(cartesian_product(parameter_dict))
    env.run(tone_in_noise)
    toc = datetime.now()
    print("Completed pypet simulation in {}".format(toc - tic))
    return 0


if __name__ == "__main__":
    sys.exit(main())
