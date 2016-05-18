#!/usr/bin/env python
"""
Function: generate_an_fig_on_vs_off

Usage:
    generate_an_fig_on_vs_off -h | --help
    generate_an_fig_on_vs_off --version
    generate_an_fig_on_vs_off [--out <outpath>]  [-c | --clean]  [-v | --verbose] [--pSave <peripheryFlag>] [--bSave] [--noBrainstem] [(--stimulusFile <stimulusPath> | (--wavFile <wavPath> --level <spl>))] [--no-cf-weighting]

Options:
    -h --help                       Show this screen and exit.
    --version                       Display the version and exit.
    --path_filename=<fn_path>       Specify the full location of the .npz file to process [default: /Volumes/EXT_DISK/encina/2_data_for_scripts/1_modeling/2_model-verhulst-abr/]
    --mod=<mod_flag>                Specify the modulation depth with the string "m85" for m = 85% or "m25" for m = 25% [default: "m85"]
"""


# Import modules
import sys
import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from os import sep
from math import ceil

# something


def main():
    # get the command line args
    args = docopt(__doc__, version=__version__)

    # get the path to the file
    path_filename = args["path_filename"]
    mod = args["mod"]

    # Set the current working directory to the 2_model-verhulst-abr folder in
    # the external disk
    os.chdir(
        '/Volumes/EXT_DISK/encina/2_data_for_scripts/1_modeling/2_model-verhulst-abr')

    # Load data from npz files
    periph = np.load(path_filename)
    periph_bm = periph['bm_velocity']
    periph_ihc = periph['ihc']
    periph_an_high_non_scaled = periph['an_high_spont']
    periph_an_med_non_scaled = periph['an_medium_spont']
    periph_an_low_non_scaled = periph['an_low_spont']
    periph_lvl = int(periph['stimulus_level'])

    # Distribution of different kind of SR fibers (Number of fibers per IHC)
    num_low_sr_x_ihc = 3
    num_med_sr_x_ihc = 3
    num_high_sr_x_ihc = 13
    num_total_sr_x_ihc = 19

    # Weighting factor to produce a W-I amplitude of 0.15 muV
    M1_weight_fact = 0.15e-6 / 2.7676e+07

    # Scale each SR fiber type by its proportion
    periph_an_high = periph_an_high_non_scaled * \
        (num_high_sr_x_ihc / num_total_sr_x_ihc)
    periph_an_med = periph_an_med_non_scaled * \
        (num_med_sr_x_ihc / num_total_sr_x_ihc)
    periph_an_low = periph_an_low_non_scaled * \
        (num_low_sr_x_ihc / num_total_sr_x_ihc)

    periph_an_sum = periph_an_high + periph_an_med + periph_an_low

    fs = 100000
    freq_ax = periph['cf']
    time_ax = np.arange(0, .3, 1 / fs)

    low_smpl_lim = 5150
    upper_smpl_lim = 9450

    freq_sampl_total = len(freq_ax)
    time_sampl_total = len(time_ax)

    idx_freq_off = [(index, item) for index, item in enumerate(freq_ax) if item > 5990 and
                    item < 6010]
    idx_freq_off = idx_freq_off[0][0]
    idx_freq_on = [(index, item) for index, item in enumerate(freq_ax) if item > 1995 and
                   item < 2005]
    idx_freq_on = idx_freq_on[0][0]

    fig_an_on_vs_off = plt.figure(figsize=(14, 8))
    sns.set_style('ticks')

    gs_an_on_vs_off_1 = gridspec.GridSpec(nrows=2, ncols=1)
    gs_an_on_vs_off_1.update(left=0.08, right=0.48,
                             top=0.90, bottom=0.55, hspace=-.00)
    ax_an_high_on = fig_an_on_vs_off.add_subplot(gs_an_on_vs_off_1[0, 0])
    ax_an_high_off = fig_an_on_vs_off.add_subplot(
        gs_an_on_vs_off_1[1, 0], sharex=ax_an_high_on)
    ax_an_high_on.get_xaxis().set_visible(False)

    gs_an_on_vs_off_2 = gridspec.GridSpec(nrows=2, ncols=1)
    gs_an_on_vs_off_2.update(left=0.55, right=0.95,
                             top=0.90, bottom=0.55, hspace=0.00)
    ax_an_med_on = fig_an_on_vs_off.add_subplot(gs_an_on_vs_off_2[0, 0])
    ax_an_med_off = fig_an_on_vs_off.add_subplot(
        gs_an_on_vs_off_2[1, 0], sharex=ax_an_med_on)
    ax_an_med_on.get_xaxis().set_visible(False)

    gs_an_on_vs_off_3 = gridspec.GridSpec(nrows=2, ncols=1)
    gs_an_on_vs_off_3.update(left=0.08, right=0.48,
                             top=0.45, bottom=0.05, hspace=0.00)
    ax_an_low_on = fig_an_on_vs_off.add_subplot(gs_an_on_vs_off_3[0, 0])
    ax_an_low_off = fig_an_on_vs_off.add_subplot(
        gs_an_on_vs_off_3[1, 0], sharex=ax_an_low_on)
    ax_an_low_on.get_xaxis().set_visible(False)

    gs_an_on_vs_off_4 = gridspec.GridSpec(nrows=2, ncols=1)
    gs_an_on_vs_off_4.update(left=0.55, right=0.95,
                             top=0.45, bottom=0.05, hspace=0.00)
    ax_an_sum_on = fig_an_on_vs_off.add_subplot(gs_an_on_vs_off_4[0, 0])
    ax_an_sum_off = fig_an_on_vs_off.add_subplot(
        gs_an_on_vs_off_4[1, 0], sharex=ax_an_sum_on)
    ax_an_sum_on.get_xaxis().set_visible(False)

    fig_an_on_vs_off.suptitle('AN response - ON (2 kHz) vs OFF (6 kHz) frequency - ' +
                              str(periph_lvl) + ' dB SPL', fontsize=18)

    # int( ceil( np.max(periph_an_sum[low_smpl_lim:upper_smpl_lim,:]) ))
    sum_max_val = 500

    ax_an_high_on.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                       periph_an_high[low_smpl_lim:upper_smpl_lim, idx_freq_on])
    ax_an_high_off.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                        periph_an_high[low_smpl_lim:upper_smpl_lim, idx_freq_off])
    ax_an_high_off.set_xlim(low_smpl_lim / fs, upper_smpl_lim / fs)
    ax_an_high_on.set_ylim(0, sum_max_val)
    ax_an_high_off.set_ylim(0, sum_max_val)
    ax_an_high_on.set_title('High-SR', fontsize=14)
    ax_an_high_off.set_xlabel('Time [s]')
    ax_an_high_on.set_ylabel('On-freq')
    ax_an_high_off.set_ylabel('Off-freq')
    ax_an_high_on.tick_params(right="off")
    ax_an_high_off.tick_params(top="off", right="off")

    ax_an_med_on.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                      periph_an_med[low_smpl_lim:upper_smpl_lim, idx_freq_on])
    ax_an_med_off.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                       periph_an_med[low_smpl_lim:upper_smpl_lim, idx_freq_off])
    ax_an_med_off.set_xlim(low_smpl_lim / fs, upper_smpl_lim / fs)
    ax_an_med_on.set_ylim(0, sum_max_val)
    ax_an_med_off.set_ylim(0, sum_max_val)
    ax_an_med_on.set_title('Med-SR', fontsize=14)
    ax_an_med_off.set_xlabel('Time [s]')
    ax_an_med_on.set_ylabel('On-freq')
    ax_an_med_off.set_ylabel('Off-freq')
    ax_an_med_on.tick_params(right="off")
    ax_an_med_off.tick_params(top="off", right="off")

    ax_an_low_on.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                      periph_an_low[low_smpl_lim:upper_smpl_lim, idx_freq_on])
    ax_an_low_off.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                       periph_an_low[low_smpl_lim:upper_smpl_lim, idx_freq_off])
    ax_an_low_off.set_xlim(low_smpl_lim / fs, upper_smpl_lim / fs)
    ax_an_low_on.set_ylim(0, sum_max_val)
    ax_an_low_off.set_ylim(0, sum_max_val)
    ax_an_low_on.set_title('Low-SR', fontsize=14)
    ax_an_low_off.set_xlabel('Time [s]')
    ax_an_low_on.set_ylabel('On-freq')
    ax_an_low_off.set_ylabel('Off-freq')
    ax_an_low_on.tick_params(right="off")
    ax_an_low_off.tick_params(top="off", right="off")

    ax_an_sum_on.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                      periph_an_sum[low_smpl_lim:upper_smpl_lim, idx_freq_on])
    ax_an_sum_off.plot(time_ax[low_smpl_lim:upper_smpl_lim],
                       periph_an_sum[low_smpl_lim:upper_smpl_lim, idx_freq_off])
    ax_an_sum_off.set_xlim(low_smpl_lim / fs, upper_smpl_lim / fs)
    ax_an_sum_on.set_ylim(0, sum_max_val)
    ax_an_sum_off.set_ylim(0, sum_max_val)
    ax_an_sum_on.set_title('Sum across SR', fontsize=14)
    ax_an_sum_off.set_xlabel('Time [s]')
    ax_an_sum_on.set_ylabel('On-freq')
    ax_an_sum_off.set_ylabel('Off-freq')
    ax_an_sum_on.tick_params(right="off")
    ax_an_sum_off.tick_params(top="off", right="off")

    fig_an_on_vs_off.savefig(os.getcwd() + sep + '2_mdl_plots' + sep +
                             '1_pilot_simulations_an' + sep + '1_plots' + sep + 'fig_periph_an_on_vs_off_' +
                             mod + '_' + str(periph_lvl) + 'dB.pdf', bbox_inches='tight', dpi=300)

if __name__ == "__main__":
    sys.exit(main())
