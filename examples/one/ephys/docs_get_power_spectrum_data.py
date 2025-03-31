"""
Download and plot power spectrum of raw data
============================================

Downloads LFP power spectrum for a given session and probe and plots a heatmap of power spectrum
on the channels along probe against frequency
"""


# import modules
from oneibl.one import ONE
import matplotlib.pyplot as plt
import alf.io
import numpy as np

# instantiate ONE
one = ONE()

# Specify subject, date and probe we are interested in
subject = 'CSHL049'
date = '2020-01-08'
sess_no = 1
probe_label = 'probe00'
eid = one.search(subject=subject, date=date, number=sess_no)[0]

# Specify the dataset types of interest
dtypes = ['_iblqc_ephysSpectralDensity.freqs',
          '_iblqc_ephysSpectralDensity.power',
          'channels.rawInd',
          'channels.localCoordinates']

# Download the data and get paths to downloaded data
_ = one.load(eid, dataset_types=dtypes, download_only=True)
ephys_path = one.path_from_eid(eid).joinpath('raw_ephys_data', probe_label)
alf_path = one.path_from_eid(eid).joinpath('alf', probe_label)

# Index of good recording channels along probe
chn_inds = np.load(alf_path.joinpath('channels.rawInd.npy'))
# Position of each recording channel along probe
chn_pos = np.load(alf_path.joinpath('channels.localCoordinates.npy'))
# Get range for y-axis
depth_range = [np.min(chn_pos[:, 1]), np.max(chn_pos[:, 1])]

# Load in power spectrum data
lfp_spectrum = alf.io.load_object(ephys_path, 'ephysSpectralDensityLF', namespace='iblqc')
lfp_freq = lfp_spectrum['freqs']
lfp_power = lfp_spectrum['power'][:, chn_inds]

# Define a frequency range of interest
freq_range = [0, 300]
freq_idx = np.where((lfp_freq >= freq_range[0]) &
                    (lfp_freq < freq_range[1]))[0]

# Limit data to freq range of interest and also convert to dB
lfp_spectrum_data = 10 * np.log(lfp_power[freq_idx, :])
dB_levels = np.quantile(lfp_spectrum_data, [0.1, 0.9])

# Create figure
fig, ax = plt.subplots()
# Plot the LFP spectral data
spectrum_plot = ax.imshow(lfp_spectrum_data.T, extent=np.r_[freq_range, depth_range],
                          cmap='viridis', vmin=dB_levels[0], vmax=dB_levels[1], origin='lower',
                          aspect='auto')
cbar = fig.colorbar(spectrum_plot, ax=ax)
cbar.set_label('LFP power (dB)')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Depth along probe (um)')
ax.set_title('Power Spectrum of LFP')

plt.show()
