
import sys
import argparse
import configparser
import numpy as np
import pickle

from one.api import ONE
import brainbox.io.one

import iblUtils

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--eID", type=str, help="experiment ID",
                        default="ebe2efe3-e8a1-451a-8947-76ef42427cc9") # NEURO019
    parser.add_argument("--probe_id", type=str, help="id of the probe to analyze",
                       default="probe00")
    parser.add_argument("--epoch_event_name", help="epoch event name",
                        type=str, default="response_times")
    parser.add_argument("--results_filename_pattern",
                        help="results filename pattern",
                        type=str,
                        default="../../results/epochedSpikes_eID_{:s}_probeID_{:s}_epochedBy_{:s}.{:s}")
    args = parser.parse_args()

    eID = args.eID
    probe_id = args.probe_id
    epoch_event_name = args.epoch_event_name
    results_filename_pattern = args.results_filename_pattern


    one = ONE(base_url='https://openalyx.internationalbrainlab.org',
              password='international', silent=True)
    trials = one.load_object(eID, 'trials')
    spikes = one.load_object(eID, 'spikes', 'alf/probe00/pykilosort')
    clusters = one.load_object(eID, "clusters", f"alf/{probe_id}/pykilosort")

    clusters_ids = np.unique(spikes.clusters)
    n_clusters = len(clusters_ids)
    channels_for_clusters_ids = clusters.channels
    els = brainbox.io.one.load_channel_locations(eID, one=one)
    locs_for_clusters_ids = els[probe_id]["acronym"][channels_for_clusters_ids].tolist()

    epoch_times = trials[epoch_event_name]
    n_trials = len(epoch_times)
    trials_ids = np.arange(n_trials)

    epoch_start_times = [trials["intervals"][r][0] for r in range(n_trials)]
    epoch_end_times = [trials["intervals"][r][1] for r in range(n_trials)]

    spikes_times_by_neuron = []
    selected_clusters_ids = []
    for cluster_id in clusters_ids:
        print(f"Processing cluster {cluster_id}")
        neuron_spikes_times = spikes.times[spikes.clusters==cluster_id]
        if len(neuron_spikes_times) > 0:
            selected_clusters_ids.append(cluster_id)
            n_epoched_spikes_times = iblUtils.epoch_neuron_spikes_times(
                neuron_spikes_times=neuron_spikes_times,
                epoch_times = epoch_times,
                epoch_start_times=epoch_start_times,
                epoch_end_times=epoch_end_times)
            spikes_times_by_neuron.append(n_epoched_spikes_times)
    n_neurons = len(selected_clusters_ids)
    n_trials = len(spikes_times_by_neuron[0])
    spikes_times = [[spikes_times_by_neuron[n][r] for n in range(n_neurons)]
                    for r in range(n_trials)]
    selected_clusters = [[clusters[clusters_key][cluster_id]
                          if clusters[clusters_key].ndim==1
                          else clusters[clusters_key]
                          for cluster_id in selected_clusters_ids]
                         for clusters_key in clusters.keys()]
    selected_locs_for_clusters_ids = [locs_for_clusters_ids[cluster_id]
                                      for cluster_id in selected_clusters_ids]
    epoch_config = configparser.ConfigParser()
    epoch_config["params"] = {
        "eID": eID,
        "probe_id": probe_id,
        "clusters_ids": selected_clusters_ids,
        "epoch_event_name": epoch_event_name,
    }
    metadata_filename = results_filename_pattern.format(eID, probe_id,
                                                        epoch_event_name,
                                                        "metadata")
    with open(metadata_filename, "w") as f:
        epoch_config.write(f)
    print(f"Saved {metadata_filename}")

    results = {"spikes_times": spikes_times,
               "clusters_ids": selected_clusters_ids,
               "trials_info": trials,
               "clusters_info": selected_clusters,
               "locs_for_clusters_ids": selected_locs_for_clusters_ids,
              }
    results_filename = results_filename_pattern.format(eID, probe_id,
                                                       epoch_event_name,
                                                       "pickle")
    with open(results_filename, "wb") as f:
        pickle.dump(results, f)

    breakpoint()


if __name__ == "__main__":
    main(sys.argv)
