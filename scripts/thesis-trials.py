# i can store the output path for each configuration, and know what it is, and store relevant plotting parameters in a named tuple here.
# Then directory path doesn't matter.
import glob
from os import path

from pypet import Environment
from pypet.utils.explore import cartesian_product

from verhulst_runner import base


def tone_in_noise(traj: Environment.trajectory):
    pass


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
periphery_type = '--peripheryType '
brainstem_type = '--brainstemType '
cf_weighting = '--no-cf-weighting '
wavfile = "--wavFile "
level = "--level "
traj.f_add_parameter(periphery_type, 'verhulst', comment="which periphery was used")
traj.f_add_parameter(brainstem_type, 'nelsoncarney04', comment="which brainstem model was used")
traj.f_add_parameter(cf_weighting, 0, comment="weighted CFs")
traj.f_add_parameter(wavfile, '', comment="Which wav file to run")
traj.f_add_parameter(level, 80, comment="stimulus level, spl")

parameter_dict = {periphery_type: ['verhulst', 'zilany'],
                  brainstem_type: ['nelsoncarney04', 'carney2015'],
                  cf_weighting: [cf_weighting, None],
                  wavfile: stimuli,
                  level: [60, 80, 90]
                  }

traj.f_explore(cartesian_product(parameter_dict))

env.run(tone_in_noise)
