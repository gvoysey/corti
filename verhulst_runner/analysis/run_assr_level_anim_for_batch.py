# Function to produce BM and AN animations
def an_animation(path_filename: str, mod: str):

    # Import modules
    import os
    import numpy as np
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    import matplotlib.animation as animation
    from os import sep
    from math import ceil
    import matplotlib.gridspec as gridspec
    from matplotlib.ticker import FormatStrFormatter

    # Set the current working directory to the 2_model-verhulst-abr folder in
    # the external disk
    os.chdir('/projectnb/anl1/encina/')
#    os.chdir(
#       '/Volumes/EXT_DISK/encina/2_data_for_scripts/1_modeling/2_model-verhulst-abr')

    # Load data from npz files
    periph = np.load(path_filename)
    periph_bm = periph['bm_velocity']
    periph_an_high_non_scaled = periph['an_high_spont']
    periph_an_med_non_scaled = periph['an_medium_spont']
    periph_an_low_non_scaled = periph['an_low_spont']
    periph_stim = periph['stimulus']
    periph_lvl = int(periph['stimulus_level'])

    # Distribution of different kind of SR fibers (Number of fibers per IHC)
    num_low_sr_x_ihc = 3
    num_med_sr_x_ihc = 3
    num_high_sr_x_ihc = 13
    num_total_sr_x_ihc = 19

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

    time_ax_anim = time_ax[low_smpl_lim:upper_smpl_lim]

    idx_freq_off = [(index, item) for index, item in
                    enumerate(freq_ax) if item > 5990 and item < 6010]
    idx_freq_off = idx_freq_off[0][0]
    idx_freq_on = [(index, item) for index, item in
                   enumerate(freq_ax) if item > 1995 and item < 2005]
    idx_freq_on = idx_freq_on[0][0]

    # ANIMATIONS

    sns.set_style('darkgrid', {"axes.facecolor": ".9"})

    periph_an_stim_anim = periph_stim[low_smpl_lim:upper_smpl_lim]
    periph_an_bm_anim = periph_bm[low_smpl_lim:upper_smpl_lim, :]
    periph_an_sum_anim = periph_an_sum[low_smpl_lim:upper_smpl_lim, :]
    periph_an_hs_anim = periph_an_high[low_smpl_lim:upper_smpl_lim, :]
    periph_an_ms_anim = periph_an_med[low_smpl_lim:upper_smpl_lim, :]
    periph_an_ls_anim = periph_an_low[low_smpl_lim:upper_smpl_lim, :]

    stim_abs_max_val = ceil(np.max([np.max(periph_an_stim_anim),
                                    np.abs(np.min(periph_an_stim_anim))]) *
                            100) / 100

    bm_abs_max_val = ceil(np.max([np.max(periph_an_bm_anim),
                                  np.abs(np.min(periph_an_bm_anim))]) *
                          100000) / 100000

    an_sr_abs_max_val = int(ceil(np.max([np.max(periph_an_high[
        low_smpl_lim:upper_smpl_lim, :]), np.max(periph_an_med[
            low_smpl_lim:upper_smpl_lim, :]), np.max(periph_an_low[
                low_smpl_lim:upper_smpl_lim, :])])))

    an_sum_max_val = int(
        ceil(np.max(periph_an_sum[low_smpl_lim:upper_smpl_lim, :])))

    fig_an_anim = plt.figure(figsize=(12, 8))

    with sns.axes_style("ticks"):
        gs_an_anim_stim = gridspec.GridSpec(nrows=1, ncols=3)
        gs_an_anim_stim.update(left=0.05, right=0.95, top=0.92, bottom=0.80)
        ax_an_anim_stim = fig_an_anim.add_subplot(gs_an_anim_stim[0, :])
        ax_an_anim_stim.get_yaxis().set_visible(False)
        sns.despine(left=True)

    gs_an_anim_bm_sum = gridspec.GridSpec(nrows=1, ncols=2)
    gs_an_anim_bm_sum.update(left=0.08, right=0.95, top=0.72, bottom=0.44)
    ax_an_anim_bm = fig_an_anim.add_subplot(gs_an_anim_bm_sum[0, 0])
    ax_an_anim_sum = fig_an_anim.add_subplot(gs_an_anim_bm_sum[0, 1])

    gs_an_anim_sr = gridspec.GridSpec(nrows=1, ncols=3)
    gs_an_anim_sr.update(left=0.08, right=0.95, top=0.34,
                         bottom=0.07, wspace=0.04)
    ax_an_anim_sr_hs = fig_an_anim.add_subplot(gs_an_anim_sr[0, 0])
    ax_an_anim_sr_ms = fig_an_anim.add_subplot(gs_an_anim_sr[0, 1])
    ax_an_anim_sr_ls = fig_an_anim.add_subplot(gs_an_anim_sr[0, -1])
    plt.setp(ax_an_anim_sr_ms.get_yticklabels(), visible=False)
    plt.setp(ax_an_anim_sr_ls.get_yticklabels(), visible=False)

    fig_an_anim.suptitle('BM & AN response @ ' +
                         str(periph_lvl) + ' dB SPL', fontsize=18)

    # Plot the lines
    an_stim_line = ax_an_anim_stim.plot(time_ax_anim, periph_an_stim_anim)
    an_bm_line, = ax_an_anim_bm.plot(freq_ax, periph_an_bm_anim[0, :])
    an_sum_line, = ax_an_anim_sum.plot(freq_ax, periph_an_sum_anim[0, :])
    an_hs_line, = ax_an_anim_sr_hs.plot(freq_ax, periph_an_hs_anim[0, :])
    an_ms_line, = ax_an_anim_sr_ms.plot(freq_ax, periph_an_ms_anim[0, :])
    an_ls_line, = ax_an_anim_sr_ls.plot(freq_ax, periph_an_ls_anim[0, :])

    # Plot the dots at fc
    an_stim_dot = ax_an_anim_stim.plot(
        time_ax_anim[0], periph_an_stim_anim[0], 'or')
    an_bm_dot = ax_an_anim_bm.plot(
        freq_ax[idx_freq_on], periph_an_bm_anim[0, idx_freq_on], 'or')
    an_sum_dot = ax_an_anim_sum.plot(
        freq_ax[idx_freq_on], periph_an_sum_anim[0, idx_freq_on], 'or')
    an_hs_dot = ax_an_anim_sr_hs.plot(
        freq_ax[idx_freq_on], periph_an_hs_anim[0, idx_freq_on], 'or')
    an_ms_dot = ax_an_anim_sr_ms.plot(
        freq_ax[idx_freq_on], periph_an_ms_anim[0, idx_freq_on], 'or')
    an_ls_dot = ax_an_anim_sr_ls.plot(
        freq_ax[idx_freq_on], periph_an_ls_anim[0, idx_freq_on], 'or')

    # Set axis, limits and labels
    ax_an_anim_stim.set_ylim(-stim_abs_max_val, stim_abs_max_val)
    ax_an_anim_stim.set_xlim(time_ax_anim[0], time_ax_anim[-1])
    ax_an_anim_stim.set_xlabel('Time [sec]')
    ax_an_anim_stim.set_ylabel('Amplitude [a.u.]')
    ax_an_anim_stim.set_title('Stimulus waveform')

    ax_an_anim_bm.set_ylim(-bm_abs_max_val, bm_abs_max_val)
    ax_an_anim_bm.yaxis.set_major_formatter(FormatStrFormatter('%.0e'))
    ax_an_anim_bm.set_xlim(freq_ax[0], freq_ax[-1])
    ax_an_anim_bm.set_xscale('log')
    ax_an_anim_bm.set_xlabel('Frequency [Hz]')
    ax_an_anim_bm.set_ylabel('Velocity [mm/sec]')
    ax_an_anim_bm.set_title('Basilar membrane')

    ax_an_anim_sum.set_ylim(0, an_sum_max_val)
    ax_an_anim_sum.set_xlim(freq_ax[0], freq_ax[-1])
    ax_an_anim_sum.set_xscale('log')
    ax_an_anim_sum.set_xlabel('Frequency [Hz]')
    ax_an_anim_sum.set_ylabel('Firing rate [spikes/sec]')
    ax_an_anim_sum.set_title('Sum across SR')

    ax_an_anim_sr_hs.set_ylim(0, an_sr_abs_max_val)
    ax_an_anim_sr_hs.set_xlim(freq_ax[0], freq_ax[-1])
    ax_an_anim_sr_hs.set_xscale('log')
    ax_an_anim_sr_hs.set_xlabel('Frequency [Hz]')
    ax_an_anim_sr_hs.set_ylabel('Firing rate [spikes/sec]')
    ax_an_anim_sr_hs.set_title('High-SR')

    ax_an_anim_sr_ms.set_ylim(0, an_sr_abs_max_val)
    ax_an_anim_sr_ms.set_xlim(freq_ax[0], freq_ax[-1])
    ax_an_anim_sr_ms.set_xscale('log')
    ax_an_anim_sr_ms.set_xlabel('Frequency [Hz]')
    ax_an_anim_sr_ms.set_title('Medium-SR')

    ax_an_anim_sr_ls.set_ylim(0, an_sr_abs_max_val)
    ax_an_anim_sr_ls.set_xlim(freq_ax[0], freq_ax[-1])
    ax_an_anim_sr_ls.set_xscale('log')
    ax_an_anim_sr_ls.set_xlabel('Frequency [Hz]')
    ax_an_anim_sr_ls.set_title('Low-SR')

    time_text = fig_an_anim.text(0.02, 0.95, 'Time: ' +
                                 format(time_ax[low_smpl_lim] * 1000,
                                        '.2f') + ' ms', fontsize=14)

    # num_frames is the number of iterations of the update function
    num_frames = int(periph_an_hs_anim.shape[0])

    def update(num_frames):
        # Update lines
        an_bm_line.set_ydata(periph_an_bm_anim[num_frames, :])
        an_sum_line.set_ydata(periph_an_sum_anim[num_frames, :])
        an_hs_line.set_ydata(periph_an_hs_anim[num_frames, :])
        an_ms_line.set_ydata(periph_an_ms_anim[num_frames, :])
        an_ls_line.set_ydata(periph_an_ls_anim[num_frames, :])

        # Update dots
        an_stim_dot[0].set_data(time_ax_anim[num_frames],
                                periph_an_stim_anim[num_frames])
        an_bm_dot[0].set_ydata(periph_an_bm_anim[num_frames, idx_freq_on])

        an_sum_dot[0].set_ydata(periph_an_sum_anim[num_frames, idx_freq_on])
        an_hs_dot[0].set_ydata(periph_an_hs_anim[num_frames, idx_freq_on])
        an_ms_dot[0].set_ydata(periph_an_ms_anim[num_frames, idx_freq_on])
        an_ls_dot[0].set_ydata(periph_an_ls_anim[num_frames, idx_freq_on])

        # Update time text
        time_text.set_text('Time: ' + format(time_ax[
            low_smpl_lim + num_frames] * 1000, '.2f') + ' ms')
        return an_hs_line, an_ms_line, an_ls_line, an_sum_line,

    ani = animation.FuncAnimation(fig_an_anim, update, num_frames, interval=1,
                                  repeat=False, blit=True)
    FFMpegWriter = animation.writers['ffmpeg']
    writer = FFMpegWriter(fps=80, bitrate=100000)

    ani.save(os.getcwd() + sep + '2_mdl_plots' + sep + 'anim_' + mod + '_' +
             str(periph_lvl) + 'dB.mp4', writer=writer, dpi=150,
             extra_args=['-vcodec', 'h264', '-pix_fmt', 'yuv420p'])
