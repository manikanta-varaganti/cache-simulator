"""
Module: cache.py
Author: Manikanta Varaganti
Date: November 10, 2023
Description: This module contains the Class Cache that can be instantiated as L1, L2, so on.
"""
from math import *
from cache_block import CacheBlock
from utils import *
from collections import deque


class Cache:
    def __init__(
        self,
        blockSize,
        size,
        associativity,
        replacementPolicy,
        inclusionPolicy,
        cacheLevel=1,
    ):
        # cache attributes
        self.block_size = blockSize
        self.size = size
        self.associativity = associativity
        self.replacement_policy = replacementPolicy
        self.inclusion = inclusionPolicy
        self.writeBack = False
        self.evictedAddress = None
        self.evicted = False
        self.cache_level = cacheLevel
        self.next_cache_level = None

        # cache metrics
        self.reads = 0
        self.read_hits = 0
        self.read_misses = 0
        self.writes = 0
        self.write_hits = 0
        self.write_misses = 0
        self.write_backs = 0
        self.mem_write_back = 0

        if self.associativity == 0:
            # fully associative cache
            self.sets = 1
            self.associativity = int(self.size / self.block_size)
            self.offset_width = int(log2(blockSize))
            self.index_width = 0
            self.tag_width = 32 - self.offset_width

        else:
            # direct mapped and set associative cache
            self.sets = int(self.size / (self.block_size * self.associativity))

            # tag, index, offset width size for address
            self.offset_width = int(log2(blockSize))
            self.index_width = int(log2(self.sets))
            self.tag_width = 32 - self.offset_width - self.index_width

        # create a 2D array of cache blocks
        self.cacheLines = [
            [CacheBlock() for _ in range(self.associativity)] for _ in range(self.sets)
        ]

        # initialize the LRU & FIFO counters
        self.LRU_matrix = [([0] * self.associativity) for row in range(self.sets)]
        self.FIFO_queue = [
            deque([i for i in range(self.associativity)]) for _ in range(self.sets)
        ]

    # returns the tag address
    def _get_tag_address(self, address):
        binAddr = hexToBin(address)[: self.tag_width]
        return binToHex(binAddr)

    # returns the index value to be mapped in cache
    def _get_index_value(self, address):
        binAddr = hexToBin(address)[self.tag_width : self.tag_width + self.index_width]
        if binAddr == "":
            return 0
        else:
            return binToDec(binAddr)

    # returns the cache cell if found
    def _get_cache_cell(self, address):
        tag = self._get_tag_address(address)
        index = self._get_index_value(address)
        for way in range(self.associativity):
            if self.cacheLines[index][way]._getTag() == tag:
                return self.cacheLines[index][way]
            else:
                None

    # updates the LRU FIFO counters
    def _update_block(self, index, way):
        if self.replacement_policy == "0":
            self.LRU_matrix[index][way] = max(self.LRU_matrix[index]) + 1
        elif self.replacement_policy == "1":
            self.FIFO_queue[index].remove(way)  # Remove way from FIFO queue
            self.FIFO_queue[index].append(way)
        else:
            None

    # returns the cache block that neeeds to be replaced
    def _find_block_to_replace(self, index):
        if self.replacement_policy == "0":  # LRU
            lru = min(self.LRU_matrix[index])
            lru_way = self.LRU_matrix[index].index(lru)
            return self.cacheLines[index][lru_way]

        elif self.replacement_policy == "1":  # FIFO
            fifo_way = self.FIFO_queue[index].popleft()  # Remove the oldest way
            self.FIFO_queue[index].append(fifo_way)
            return self.cacheLines[index][fifo_way]
        else:
            None

    # replaces the cache block
    def _replace_block(self, address, operation):
        tag = self._get_tag_address(address)
        index = self._get_index_value(address)

        # find a cache block that needs to be replaced by a replacement policy
        blockToBeEvicted = self._find_block_to_replace(index)

        # issue writeback if evicted block contains dirty bit
        if blockToBeEvicted.isDirty:
            self.write_backs += 1
            self.writeBack = True  # issues writeback to next level of memory
            self.evictedAddress = blockToBeEvicted._getAddress()

        # used for invalidating L1 block incase of inclusion violation
        if self.cache_level == 2:
            self.evicted = True
            self.evictedAddress = blockToBeEvicted._getAddress()

        if operation == "w":
            blockToBeEvicted._setDirty()
        else:
            blockToBeEvicted._resetDirty()

        evictedBlockWay = blockToBeEvicted._getWay()
        blockToBeEvicted._setTag(tag)
        blockToBeEvicted._setAddress(address)
        self._update_block(index, evictedBlockWay)

    # invalidates a L1 cache block incase of inclusion violation
    def invalidate_block(self, address):
        tag = self._get_tag_address(address)
        cacheCell = self._get_cache_cell(address)
        if cacheCell is not None and self.inclusion == "1":
            if cacheCell.isDirty:
                self.writeBack = True
                self.mem_write_back += (
                    1  # L1 to main memory write back incase of dirty block
                )

            cacheCell._resetAll()  # reset all the properties of a block

    # allocates a block in cache
    def allocate_block(self, address, operation):
        tag = self._get_tag_address(address)
        index = self._get_index_value(address)

        available = False
        if self.associativity > 1:
            # set associative cache
            for way in range(self.associativity):
                if self.cacheLines[index][way]._getValidity() == False:
                    self.cacheLines[index][way]._setTag(tag)
                    self.cacheLines[index][way]._setWay(way)
                    self.cacheLines[index][way]._setValidity()
                    self.cacheLines[index][way]._setAddress(address)
                    self._update_block(index, way)
                    # set dirty bit as true if a write is issued
                    if operation == "w":
                        self.cacheLines[index][way]._setDirty()

                    available = True
                    break

            if available == False:
                # replace block if contents are full
                self._replace_block(address, operation)

        elif self.associativity == 1:
            # direct maaped cache
            if self.cacheLines[index][0]._getTag() is None:
                self.cacheLines[index][0]._setTag(tag)
                self.cacheLines[index][0]._setWay(0)
                self.cacheLines[index][0]._setValidity()
                self.cacheLines[index][0]._setAddress(address)
                self._update_block(index, 0)

                if operation == "w":
                    self.cacheLines[index][0]._setDirty()

            else:
                # replace block if contents are full
                self._replace_block(address, operation)

        else:
            # fully associative cache
            ways = int(self.size / self.block_size)
            for way in range(ways):
                if self.cacheLines[0][way]._getValidity() == False:
                    self.cacheLines[0][way]._setTag(tag)
                    self.cacheLines[0][way]._setWay(way)
                    self.cacheLines[0][way]._setValidity()
                    self.cacheLines[0][way]._setAddress(address)
                    self._update_block(0, way)
                    # set dirty bit as true if a write is issued
                    if operation == "w":
                        self.cacheLines[0][way]._setDirty()

                    # print(f"Block Allocated at Row { index} way {way}")
                    available = True
                    break

            if available == False:
                # replace block if contents are full
                self._replace_block(address, operation)

    # print the LRU FIFO counters
    def _print_LRUFIFO_contents(self):
        if self.replacement_policy == "0":
            print("LRU Matrix ", self.LRU_matrix)
        else:
            print("FIFO Matrix ", self.FIFO_queue)

    # processes the input request to cache
    def cache_request(self, address, operation):
        self.writeBack = False
        self.evictedAddress = None
        self.evicted = False

        if operation == "r":
            self.reads += 1
        else:
            self.writes += 1

        tag = self._get_tag_address(address)
        index = self._get_index_value(address)
        cacheCell = self._get_cache_cell(address)

        if cacheCell is None:
            # miss case
            if operation == "r":
                self.read_misses += 1
            else:
                self.write_misses += 1
            return False

        else:
            # hit case
            way = cacheCell._getWay()
            if operation == "w":
                self.cacheLines[index][way]._setDirty()
            if self.replacement_policy == "0":
                self._update_block(index, way)
            if operation == "r":
                self.read_hits += 1
            else:
                self.write_hits += 1
            return True
