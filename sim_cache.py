"""
Module: sim_cache.py
Author: Manikanta Varaganti
Date: November 10, 2023
Description: This module contains the generic cache simulator code.
"""

import sys
from utils import *
from cache import Cache


class CacheSimulator:
    def __init__(
        self,
        block_size,
        L1_size,
        L1_assoc,
        L2_size,
        L2_assoc,
        replace_policy,
        inclusion_policy,
        trace_file,
        debug=False,
    ):
        self.block_size = block_size
        self.L1_size = L1_size
        self.L1_assoc = L1_assoc
        self.L2_size = L2_size
        self.L2_assoc = L2_assoc
        self.replace_policy = replace_policy
        self.inclusion_policy = inclusion_policy
        self.trace_file = trace_file
        self.debug = debug

        self.replacement_policies = {"0": "LRU", "1": "FIFO"}
        self.inclusion_policies = {"0": "non-inclusive", "1": "inclusive"}

        self.L1_cache = Cache(
            blockSize=self.block_size,
            size=self.L1_size,
            associativity=self.L1_assoc,
            replacementPolicy=self.replace_policy,
            inclusionPolicy=self.inclusion_policy,
            cacheLevel=1,
        )

        if self.L2_size != 0:
            self.L2_cache = Cache(
                blockSize=self.block_size,
                size=self.L2_size,
                associativity=self.L2_assoc,
                replacementPolicy=self.replace_policy,
                inclusionPolicy=self.inclusion_policy,
                cacheLevel=2,
            )
            self.L1_cache.next_cache_level = self.L2_cache

        with open("traces/" + self.trace_file, "r") as file:
            traces = file.readlines()
            for instruction in traces[:]:
                mode, address = instruction.split(" ")
                address = fixAddress(address)
                L1_status = self.L1_cache.cache_request(address=address, operation=mode)
                if L1_status == False:  # miss in L1 cache
                    if self.L2_size == 0:
                        self.L1_cache.allocate_block(
                            address, mode
                        )  # allocate block in L1

                    else:
                        if self.inclusion_policy == 0:
                            # non-inclusive cache
                            self.L1_cache.allocate_block(address, mode)

                            if self.L1_cache.writeBack:
                                # write back from L1 to L2
                                L2_status = self.L2_cache.cache_request(
                                    address=self.L1_cache.evictedAddress, operation="w"
                                )
                                if L2_status == False:
                                    self.L2_cache.allocate_block(
                                        self.L1_cache.evictedAddress, "w"
                                    )  # pass write request to L2 with the evicted address

                            # read request to L2 incase of L1 miss
                            L2_status = self.L2_cache.cache_request(
                                address=address, operation="r"
                            )
                            if L2_status == False:
                                # L2 cache miss, allocate block in L2
                                self.L2_cache.allocate_block(address, "r")

                        else:
                            # inclusive cache
                            self.L1_cache.allocate_block(address, mode)

                            if self.L1_cache.writeBack:
                                # write back from L1 to L2
                                L2_status = self.L2_cache.cache_request(
                                    address=self.L1_cache.evictedAddress, operation="w"
                                )
                                if L2_status == False:
                                    self.L2_cache.allocate_block(
                                        self.L1_cache.evictedAddress, "w"
                                    )
                                    if self.L2_cache.evicted == True:
                                        self.L1_cache.invalidate_block(
                                            self.L2_cache.evictedAddress
                                        )

                            # read request to L2 incase of L1 miss
                            L2_status = self.L2_cache.cache_request(
                                address=address, operation="r"
                            )
                            if L2_status == False:
                                self.L2_cache.allocate_block(address, "r")
                                # send invalidation request to L1 cache to preserve inclusion property
                                if self.L2_cache.evicted == True:
                                    self.L1_cache.invalidate_block(
                                        self.L2_cache.evictedAddress
                                    )

        if self.debug != True:
            self.print_cache_configuration()
            self.print_cache_contents()
            self.print_cache_metrics()

        else:
            # used for evaluating benchmark metrics
            self.L1_miss_rate = (
                float(self.L1_cache.read_misses + self.L1_cache.write_misses)
            ) / (self.L1_cache.reads + self.L1_cache.writes)
            if self.L2_size != 0:
                self.L2_miss_rate = (float(self.L2_cache.read_misses)) / (
                    self.L2_cache.reads
                )

    def print_cache_configuration(self):
        print("===== Simulator configuration =====")
        print("BLOCKSIZE:             " + str(self.block_size))
        print("L1_SIZE:               " + str(self.L1_size))
        print("L1_ASSOC:              " + str(self.L1_assoc))
        print("L2_SIZE:               " + str(self.L2_size))
        print("L2_ASSOC:              " + str(self.L2_assoc))
        print(
            "REPLACEMENT POLICY:    " + self.replacement_policies[self.replace_policy]
        )
        print(
            "INCLUSION PROPERTY:    " + self.inclusion_policies[self.inclusion_policy]
        )
        print("trace_file:            " + self.trace_file)

    def print_cache_contents(self):
        print("===== L1 contents =====")
        for i in range(self.L1_cache.sets):
            print(f"Set\t{i}:\t", end="")
            for j in range(self.L1_cache.associativity):
                print(f"{self.L1_cache.cacheLines[i][j]._getTag()} ", end="")
                if self.L1_cache.cacheLines[i][j].isDirty:
                    print("D  ", end="")
                else:
                    print("   ", end="")
            print()
        if self.L2_size != 0:
            print("===== L2 contents =====")
            for i in range(self.L2_cache.sets):
                print(f"Set\t{i}:\t", end="")
                for j in range(self.L2_cache.associativity):
                    print(f"{self.L2_cache.cacheLines[i][j]._getTag()} ", end="")
                    if self.L2_cache.cacheLines[i][j].isDirty:
                        print("D  ", end="")
                    else:
                        print("   ", end="")
                print()

    def print_cache_metrics(self):
        print("===== Simulation results (raw) =====")
        print(f"a. number of L1 reads:        {self.L1_cache.reads}")
        print(f"b. number of L1 read misses:  {self.L1_cache.read_misses}")
        print(f"c. number of L1 writes:       {self.L1_cache.writes}")
        print(f"d. number of L1 write misses: {self.L1_cache.write_misses}")
        self.L1_miss_rate = (
            float(self.L1_cache.read_misses + self.L1_cache.write_misses)
        ) / (self.L1_cache.reads + self.L1_cache.writes)
        print(f"e. L1 miss rate:              {self.L1_miss_rate:6f}")
        print(f"f. number of L1 writebacks:   {self.L1_cache.write_backs}")
        self.L1_mem_traffic = (
            self.L1_cache.read_misses
            + self.L1_cache.write_misses
            + self.L1_cache.write_backs
        )
        if self.L2_size == 0:
            print(f"g. number of L2 reads:        0")
            print(f"h. number of L2 read misses:  0")
            print(f"i. number of L2 writes:       0")
            print(f"j. number of L2 write misses: 0")
            print(f"k. L2 miss rate:              0")
            print(f"l. number of L2 writebacks:   0")
            print(f"m. total memory traffic:      {self.L1_mem_traffic}")
        else:
            self.L2_miss_rate = (float(self.L2_cache.read_misses)) / (
                self.L2_cache.reads
            )
            self.L2_mem_traffic = (
                self.L2_cache.read_misses
                + self.L2_cache.write_misses
                + self.L2_cache.write_backs
                + self.L1_cache.mem_write_back
            )

            print(f"g. number of L2 reads:        {self.L2_cache.reads}")
            print(f"h. number of L2 read misses:  {self.L2_cache.read_misses}")
            print(f"i. number of L2 writes:       {self.L2_cache.writes}")
            print(f"j. number of L2 write misses: {self.L2_cache.write_misses}")
            print(f"k. L2 miss rate:              {self.L2_miss_rate:6f}")
            print(f"l. number of L2 writebacks:   {self.L2_cache.write_backs}")
            print(f"m. total memory traffic:      {self.L2_mem_traffic}")


if __name__ == "__main__":
    block_size = int(sys.argv[1])
    L1_size = int(sys.argv[2])
    L1_assoc = int(sys.argv[3])
    L2_size = int(sys.argv[4])
    L2_assoc = int(sys.argv[5])
    replace_policy = sys.argv[6]
    inclusion_policy = sys.argv[7]
    trace_file = sys.argv[8]

    cacheSimulator = CacheSimulator(
        block_size,
        L1_size,
        L1_assoc,
        L2_size,
        L2_assoc,
        replace_policy,
        inclusion_policy,
        trace_file,
    )
