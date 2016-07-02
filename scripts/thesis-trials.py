# i can store the output path for each configuration, and know what it is, and store relevant plotting parameters in a named tuple here.
# Then directory path doesn't matter.
import glob

from importlib.machinery import SourceFileLoader
from os import path
from pypet import Environment
from pypet.utils.explore import cartesian_product

from verhulst_runner import base

verhulst_model = SourceFileLoader('verhulst_model', './verhulst_model').load_module()


def tone_in_noise(traj: Environment.trajectory):
    commandstr = " ".join([periphery_type, traj.periphery, brainstem_type, traj.brainstem,
                           traj.weighting, wavfile, traj.wavfile, level, str(traj.level)])
    result = verhulst_model.main(commandstr)
    print("got result!")


wavpath = path.join(base.rootPath, "resources", "click-with-noise-stimuli")

stimuli = [path.join(wavpath, i) for i in glob.glob(path.join(wavpath, "*.wav"))]

outfile = path.join(path.expanduser("~"), "pypet-thesis-output", "thesis-output.hdf5")

env = Environment(trajectory='tone-in-noise',
                  filename=outfile,
                  overwrite_file=True,
                  file_title="Tone in noise at different SNR",
                  comment="some comment",
                  large_overview_tables="True",
                  )

traj = env.trajectory
periphery_type = '--peripheryType'
brainstem_type = '--brainstemType'
cf_weighting = '--no-cf-weighting'
wavfile = "--wavFile"
level = "--level"
traj.f_add_parameter('periphery', 'verhulst', comment="which periphery was used")
traj.f_add_parameter('brainstem', 'nelsoncarney04', comment="which brainstem model was used")
traj.f_add_parameter('weighting', "--no-cf-weighting ", comment="weighted CFs")
traj.f_add_parameter('wavfile', '', comment="Which wav file to run")
traj.f_add_parameter('level', 80, comment="stimulus level, spl")

parameter_dict = {
    "periphery": ['verhulst', 'zilany'],
    "brainstem": ['nelsoncarney04', 'carney2015'],
    "weighting": [cf_weighting, ""],
    "wavfile"  : stimuli,
    "level"    : [60, 80, 90]
}

traj.f_explore(cartesian_product(parameter_dict))

env.run(tone_in_noise)
