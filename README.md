# hash_framework
## Overview

`hash_framework` is a framework for studying cryptographic hash functions via
[SAT](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem). Its
focus is in developing metrics for analyzing collisions and studying and
improving new attacks.

_This framework is under heavy development and is not yet stable and thus
has no guarantees about working in the future._

## Requirements

  - Python3
  - Flask
  - sqlite3
  - [CryptoMiniSat5](https://github.com/msoos/cryptominisat)
  - [bc2cnf](https://users.ics.aalto.fi/tjunttil/circuits/)


## Installation

This repository is meant to be run from master. Simply clone the repository
and update the configuration in `hash_framework/config.py` to point to the
required tools.

To run a worker, validate the configuration and run `start_workers.sh` from
the base of the repository. See examples in `runs` for distributing jobs.


## Existing kernels

  - ASCII Search
  - Family Search
  - Minimal Differential Path Search
  - Multicollision Search
  - Neighborhood Search
  - Ones
  - Zeros


## Contributing

`hash_framework` is licensed under the GLPv3. Contributions are welcome; please
fork and open a pull request. No guarantees made about timeliness in response;
please be patient.

Most welcome are new attacks (in the form of kernels) and implementations
of other hash functions. Also welcome is compute resources for ongoing
research.

## Research

This project is part of ongoing research at Iowa State University. As papers
are published using this framework, please refer to this repository.
