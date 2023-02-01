
import sys
import argparse
import numpy as np

from one.api import ONE
import brainbox.io.one

import iblUtils

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--eID", type=str, help="experiment ID",
                        default="ebe2efe3-e8a1-451a-8947-76ef42427cc9") # NEURO019
    parser.add_argument("--probe_id", type=str, help="id of the probe to analyze",
                       default="probe00")
    parser.add_argument("--clusters_ids", type=str, help="cluster IDs to epoch",
                        default="[40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]")
    parser.add_argument("--epoch_event_name", help="epoch event name",
                        type=str, default="response_times")
    parser.add_argument("--epoch_start_event_name", type=str,
                        help="behavioral event name to use to start epochs",
                        default="stimOn_times")
    parser.add_argument("--epoch_end_event_name", type=str,
                        help="behavioral event name to use to end epochs",
                        default="stimOff_times")
    parser.add_argument("--elapsed_start", type=float,
                       help="elapsed time (in secs) between trials start times and the epoch start event",
                       default=2.0)
    parser.add_argument("--elapsed_end", type=float,
                       help="elapsed time (in secs) between the stimulus offset time and the epoch end event",
                       default=2.0)
    args = parser.parse_args()

    eID = args.eID
    probe_id = args.probe_id
    clusters_ids = args.clusters_ids[1:-1].split(",")
    epoch_event_name = args.epoch_event_name
    epoch_start_event_name = args.epoch_start_event_name
    epoch_end_event_name = args.epoch_end_event_name
    elapsed_start = args.elapsed_start
    elapsed_end = args.elapsed_end

    clusters_ids = [int(cluster_id) for cluster_id in clusters_ids]

    one = ONE(base_url='https://openalyx.internationalbrainlab.org',
              password='international', silent=True)
    spikes = one.load_object(eID, 'spikes', 'alf/probe00/pykilosort')
    trials = one.load_object(eID, 'trials')

    epoch_times = trials[epoch_event_name]
    n_trials = len(epoch_times)
    trials_ids = np.arange(n_trials)

    epoch_start_times = trials[epoch_start_event_name]
    epoch_end_times = trials[epoch_end_event_name]
    remove_trial = np.logical_or(np.isnan(epoch_times),
                                 np.logical_or(np.isnan(epoch_start_times),
                                               np.isnan(epoch_end_times)))
    keep_trial = np.logical_not(remove_trial)
    epoch_times = epoch_times[keep_trial]
    epoch_start_times = epoch_start_times[keep_trial]
    epoch_end_times = epoch_end_times[keep_trial]
    trials_ids = trials_ids[keep_trial]

    spikes_times_by_neuron = []
    selected_clusters_ids = []
    for n in range(len(clusters_ids)):
        cluster_id = clusters_ids[n]
        neuron_spikes_times = spikes.times[spikes.clusters==cluster_id]
        if len(neuron_spikes_times) > 0:
            selected_clusters_ids.append(cluster_id)
            n_epoched_spikes_times = iblUtils.epoch_neuron_spikes_times(
                neuron_spikes_times=neuron_spikes_times,
                epoch_times = epoch_times,
                epoch_start_times=epoch_start_times,
                epoch_end_times=epoch_end_times,
                elapsed_start=elapsed_start,
                elapsed_end=elapsed_end)
            spikes_times_by_neuron.append(n_epoched_spikes_times)
    n_neurons = len(selected_clusters_ids)
    n_trials = len(spikes_times_by_neuron[0])
    spikes_times = [[spikes_times_by_neuron[n][r] for n in range(n_neurons)]
                    for r in range(n_trials)]
    breakpoint()

    els = load_channel_locations(eID, one=one )

    selected_trials_indices = np.nonzero(
        np.logical_not(np.isnan(trials["epoch_event_name"])))
    clusters = np.unique(spikes["clusters"])
    n_neurons = len(clusters)

    trials_start_times = trials[trial_start_event_name][selected_trials_indices]
    trials_end_times = trials[trial_end_event_name][selected_trials_indices]
    epoch_times = trials[epoch_event_name][selected_trials_indices]
    n_trials = len(epoch_times)

    spikes_times = [[None for n in range(n_neurons)] for r in range(n_trials)]
    for r in range(n_trials):
        for n in range(n_neurons):
            # trial_start_time = trials.
            # spikes_times[r][n] = spikes.times[
            pass
    breakpoint()

if __name__ == "__main__":
    main(sys.argv)
