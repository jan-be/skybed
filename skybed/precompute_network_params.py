import concurrent.futures
import multiprocessing
import os
from bisect import bisect_right

import pandas as pd
from tqdm import tqdm

from skybed.ns3_interface import get_ns3_sim_result, NetworkParams


def get_closest_ns3_sim_result(distance) -> NetworkParams:
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "../precomputed_network_params.csv"))
    # the bisect algorithm only works on sorted lists, but it is O(log(N))
    # -1 because otherwise it gives out of bounds error if distance > largest known distance
    res = df.iloc[bisect_right(df["distance"].values, distance) - 1]
    return NetworkParams(delay=res["delay"], throughput=res["throughput"], packet_loss=0, jitter=0)


def set_network_params_result(distance, results):
    result = get_ns3_sim_result(distance=distance)
    results.append([distance, result.throughput, result.delay])


def precompute_network_params(samples=1000):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        # Submit all tasks to the executor
        futures = [executor.submit(set_network_params_result, i ** 1.5, results) for i in range(0, samples)]

        # add progress bar
        with tqdm(total=samples) as pbar:
            # Wait for all threads to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                    pbar.update(1)
                except Exception as e:
                    print(f"An error occurred: {e}")

    df = pd.DataFrame(results, columns=['distance', 'throughput', 'delay'])
    df = df.sort_values(by='distance')
    df.to_csv("precomputed_network_params.csv", index=False)


if __name__ == '__main__':
    precompute_network_params()
