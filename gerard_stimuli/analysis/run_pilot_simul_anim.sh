#!/bin/bash

#$ -pe omp 10 						# Request 6 slots
#$ -V 							# Export all current variables
#$ -l h_rt=12:00:00 					# Hard run time limit (6 hours)
#$ -j y							# Merge the error and output stream files into a single file
#$ -S /bin/bash
#$ -P anl1 						# Project name (must be anl1)
#$ -o stdout_anim					# output file path
#$ -e stderr_anim					# error file path
#$ -N pilot_an_anim					# Job name
#$ -M gerard.encina@gmail.com				# User email
#$ -m bea						# Send email when begins (b), ends (e) and aborted(a) 
#$ -l cpu_arch=nehalem 					# Processor architecture

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/1_m_85/periphery-output-20.0dB.npz', 'mod85')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/1_m_85/periphery-output-40.0dB.npz', 'mod85')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/1_m_85/periphery-output-55.0dB.npz', 'mod85')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/1_m_85/periphery-output-75.0dB.npz', 'mod85')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/1_m_85/periphery-output-90.0dB.npz', 'mod85')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/2_m_25/periphery-output-20.0dB.npz', 'mod25')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/2_m_25/periphery-output-40.0dB.npz', 'mod25')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/2_m_25/periphery-output-55.0dB.npz', 'mod25')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/2_m_25/periphery-output-75.0dB.npz', 'mod25')"

python -c "import run_assr_level_anim_for_batch; run_assr_level_anim_for_batch.an_animation('1_mdl_simulations/1_pilot_simulations_an/2_m_25/periphery-output-90.0dB.npz', 'mod25')"
wait
