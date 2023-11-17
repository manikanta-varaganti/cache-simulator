"""
Module: cache_graph.py
Author: Manikanta Varaganti
Date: November 10, 2023
Description: This module is useful for calculating the AAT and miss rate for multiple configutaions using GCC benchmark.
"""


from sim_cache import CacheSimulator
from math import *

# benchmark parameters
BlOCK_SIZE = 32
BENCHMARK_FILE = "gcc_trace.txt"
L1_size = [2**i for i in range(10, 21)]
L2_size = [2**i for i in range(11, 17)]
associativity = [1, 2, 4, 8, 0]  # 1 - 'FA'
repl_policy = ["0", "1"]  # '0' - LRU ; '1'- FIFO

# L1 L2 cache access time from the cact-table.xsl
L1_hit_time_data = {
    1: [
        0.114797,
        0.12909,
        0.147005,
        0.16383,
        0.198417,
        0.233353,
        0.294627,
        0.3668,
        0.443812,
        0.563451,
        0.69938,
    ],
    2: [
        0.140329,
        0.161691,
        0.181131,
        0.194195,
        0.223917,
        0.262446,
        0.300727,
        0.374603,
        0.445929,
        0.567744,
        0.706046,
    ],
    4: [
        0.14682,
        0.154496,
        0.185685,
        0.211173,
        0.233936,
        0.27125,
        0.319481,
        0.38028,
        0.457685,
        0.564418,
        0.699607,
    ],
    8: [
        0.151152,
        0.180686,
        0.189065,
        0.212911,
        0.254354,
        0.288511,
        0.341213,
        0.401236,
        0.458925,
        0.578177,
        0.705819,
    ],
    0: [
        0.155484,
        0.176515,
        0.182948,
        0.198581,
        0.205608,
        0.22474,
        0.276281,
        0.322486,
        0.396009,
        0.475728,
        0.588474,
    ],
}
L1_hit_time_data_graph_4 = 0.14682
L2_hit_time_data = {
    8: [
        0.180686,
        0.189065,
        0.212911,
        0.254354,
        0.288511,
        0.341213,
    ]
}


# returns L1 miss rate for graph 1 by varying L1 cache size and associativity
def L1_miss_rate_graph():
    output = {}

    for i in associativity:
        L1_miss_rate_list = []
        for j in L1_size:
            cache_sim = CacheSimulator(
                block_size=32,
                L1_size=j,
                L1_assoc=i,
                L2_size=0,
                L2_assoc=0,
                replace_policy="0",
                inclusion_policy="0",
                trace_file=BENCHMARK_FILE,
                debug=True,
            )
            L1_miss_rate_list.append(cache_sim.L1_miss_rate)

        output[i] = L1_miss_rate_list

    return output


# returns L1 AAT for graph 2 by varying L1 cache size and associativity
def L1_AAT_graph():
    output = {}
    for i in associativity:
        L1_aat_list = []
        for j in range(11):
            cache_sim = CacheSimulator(
                block_size=32,
                L1_size=L1_size[j],
                L1_assoc=i,
                L2_size=0,
                L2_assoc=0,
                replace_policy="0",
                inclusion_policy="0",
                trace_file=BENCHMARK_FILE,
                debug=True,
            )

            aat = L1_hit_time_data[i][j] + cache_sim.L1_miss_rate * 100
            L1_aat_list.append(aat)
        output[i] = L1_aat_list
    return output


# returns AAT for L1 cache by varying cache size and replacement policies
def L1_replacement_policy_graph():
    output = {}
    for i in repl_policy:
        L1_aat_list = []
        for j in range(9):
            cache_sim = CacheSimulator(
                block_size=32,
                L1_size=L1_size[j],
                L1_assoc=4,
                L2_size=0,
                L2_assoc=0,
                replace_policy=i,
                inclusion_policy="0",
                trace_file=BENCHMARK_FILE,
                debug=True,
            )
            aat = L1_hit_time_data[4][j] + cache_sim.L1_miss_rate * 100
            L1_aat_list.append(aat)
        output[i] = L1_aat_list
    return output


# returns AAT for L1-L2 cache by varying inclusion property
def inclusion_property_graph():
    incl_policy = ["0", "1"]
    output = {}
    for i in incl_policy:
        print("Inclusion ", i)
        L1_L2_aat_list = []
        for j in range(6):
            cache_sim = CacheSimulator(
                block_size=32,
                L1_size=1024,
                L1_assoc=4,
                L2_size=L2_size[j],
                L2_assoc=8,
                replace_policy="0",
                inclusion_policy=i,
                trace_file=BENCHMARK_FILE,
                debug=True,
            )
            aat = L1_hit_time_data_graph_4 + cache_sim.L1_miss_rate * (
                L2_hit_time_data[8][j] + cache_sim.L2_miss_rate * 100
            )

            L1_L2_aat_list.append(aat)
        output[i] = L1_L2_aat_list
    return output


if __name__ == "__main__":
    print("Graph 1 Study output", L1_miss_rate_graph())
    print("-" * 10)
    print("Graph 2 Study output", L1_AAT_graph())
    print("-" * 10)
    print("Graph 3 Study output", L1_replacement_policy_graph())
    print("-" * 10)
    print("Graph 4 Study output", inclusion_property_graph())
