# Generic Cache Simulator

This repository contains a cache simulator that simulates the behavior of a memory hierarchy. It consists of a generic cache module that can be instantiated as an L1 cache, an L2 cache, an L3 cache, and so on. The simulator supports various cache configurations and replacement policies.

## Features

- Simulates a memory cache with configurable parameters.
- Supports different cache configurations, including direct-mapped, set-associative, and fully-associative caches.
- Implements common cache replacement policies such as LRU (Least Recently Used) and FIFO (First In, First Out).
- Generates statistics on cache hits, misses, miss rates, write-backs and memory traffic.
- Uses Write-back + Write-allocate (WB-WA) policy.
- Supports the inclusion and non-inclusion property.


## Input
 The simulator reads a trace file in the following format:

```
r|w <hex address>
```
where 'r' (read) indicates a load and 'w' (write) indicates a store from the processor and addresses are 32 bits


## Usage

Clone the repository:

```bash
git clone https://github.com/manikanta-varaganti/cache-simulator.git
```

Navigate to the project directory and configure the simulation parameters by running the following command in the terminal

```bash
python3 sim_cache <BLOCKSIZE> <L1_SIZE> <L1_ASSOC> <L2_SIZE> <L2_ASSOC> <REPLACEMENT_POLICY> <INCLUSION_PROPERTY>  <trace_file> 
```
Where
 * BLOCKSIZE: Block size in bytes. (Same block size for all caches in the memory hierarchy.)
 * L1_SIZE: L1 cache size in bytes.
 * L1_ASSOC: L1 set-associacitivity (1 is direct-mapped, 0 is fully-associative)
 * L2_SIZE: L2 cache size in bytes. L2_SIZE = 0 signifies that there is no L2 cache.
 * L2_ASSOC: L2 set-associativity (1 is direct-mapped, 0 is fully-associative).
 * REPLACEMENT_POLICY: 0 for LRU, 1 for FIFO.
 * INCLUSION_PROPERTY: 0 for non-inclusive, 1 for inclusive.
 * trace_file: Full name of trace file including any extensions. 


  
