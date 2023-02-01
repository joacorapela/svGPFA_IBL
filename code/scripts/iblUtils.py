
import numpy as np

def epoch_neuron_spikes_times(neuron_spikes_times, epoch_times,
                              epoch_start_times, epoch_end_times,
                              elapsed_start, elapsed_end):
    epoch_start_indices = np.searchsorted(neuron_spikes_times, epoch_start_times-elapsed_start)
    epoch_end_indices = np.searchsorted(neuron_spikes_times, epoch_end_times+elapsed_end)
    epoch_end_indices[epoch_end_indices==len(neuron_spikes_times)] = len(neuron_spikes_times)-1
    n_trials = len(epoch_start_indices)
    epoched_spikes_times = \
        [[neuron_spikes_times[epoch_start_indices[r]:epoch_end_indices[r]]-epoch_times[r]]
         for r in range(n_trials)]
    return epoched_spikes_times


