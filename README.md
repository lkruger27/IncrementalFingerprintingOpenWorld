# Incremental Fingerprinting Experiments
This artifact details how the experiments of the paper ``Incremental Fingerprinting in an Open World'' for all presented results can be reproduced.
Additionally, the artifact contains learned models, results and details on how incremental fingerprinting can be used to learn a list of implementations.

The artifact is structured as follows:
1. Explanation of the benchmarks.
2. Explanation of the incremental fingerprinting code including: an explanation of the structure, details on how to install dependencies, an example run, how to generate the plots and runtime information.
3. Explanation of the incremental fingerprinting code for new experiments.

# Benchmarks

We use benchmark sets: TLS, SSH, MQTT, BLE and BLEDiff. We include .dot files for most of these models and how these models can be generated if they are not existing benchmarks.

## TLS
These are models from the Master's Thesis `Fingerprinting TLS implementations using model learning` by Erwin Janssen. The models are contained in directories `mbedtls` and `openssl`. The file `LearnTLSExperiment.py` runs L# for each model, stores the results in `L#_results.csv` and generates Table 1 in the Appendix.
The models can be found [here](https://github.com/tlsprint/models).

## SSH
These are three models from `Model Learning and Model Checking of SSH Implementations` by Fiterau-Brostean et al. and an additional 17 models mutated from these 3 base models. The original models end in suffix `Orig`. The file `Mutator.py` contains code for mutating a model. The file `LearnSSHExperiment.py` runs L# for each models, stores the results in `L#_results.csv` and generates Table 2 in the Appendix. 

## MQTT
These are models learned by interacting with various MQTT brokers using code from `Learning-Based Fuzzing of IoT Message Brokers` by Aichernig et al. The file `run.sh` can be used to generate models. 
Note that the MQTT broker still need to be installed. We refer to the installation guide of the respective broker, most can directly be installed with docker.
In the installation, please ensure that ports are forwarded as stated in `run.sh`. 
For better reliability, we recommend learning broker one-by-one.
To preserve anonymity, we only provide `mqtt.jar` for executing the custom-written MQTT broker, but will also publish the full code upon acceptance. 

The file `results.csv` contains the learning information using L# and is used to make Table 3 in the Appendix.


## BLE 
The BLE models can be found in directory `BLELearning/out/`. Some of these models are copied from the paper `Fingerprinting Bluetooth Low Energy Devices via Active Automata Learning` and the thesis `Automata Learning for Security Testing and Analysis in Networked Environments` of Andrea Pferscher. The new models can be found in `BLELearning/results/` and generated using `BLESULConnectingStart.py`. The file `LearnBLEExperiment.py` runs L# for each models, stores the results in `L#_results.csv` and generates Table 5 in the Appendix. 

## BLEDiff
These 6 models were provided by the authors of `Blediff: Scalable and property-agnostic noncompliance checking for ble implementations` but we do not have permission to share them. Therefore, the `BLEDiff_Models` directory only provides the learning results and how we generated the results.

# Incremental Fingerprinting 
The directory `fingerprinting` contains all the files for running the experiments as well as the generation of plots and tables.

The files `FingerprintingIngredients` contains the IncrementalFingerprinting and IdentifyOrLearn algorithm while `FingerprintingExperiments` can be used to run experiments using these algorithms. The result csv is stored in the `results` directory. Plots can be generated per experiment, see directory `plots`. Finally, tables in the Appendix can be generated using `table_maker.py`.

## Available Experiments
- "RQ0_closed_world_fingerprint": This experiment fingerprints models under a closed-world assumption, starting with different numbers of specifications. It is used in the overview and results are summarized in Table I.
- "RQ0_IF": This experiment applies our incremental fingerprinting algorithm IF when starting with different numbers of specifications. It is used in the overview and results are summarized in Table I.
- "RQ0_LSharp": This experiment applies RL# with RandomWp500 and is used in the overview.
- "RQ1_Perfect_Teacher": This experiment compares IF, RAL# and RL# when using a perfect teacher.
- "RQ1_Budget": This experiment compares IF, RAL# and RL# when using a set budget per benchmark.
- "RQ1_RQ2": This experiment runs RAL# and RL# with ADG and RandomWp100 and IF with all possible configurations as described in the state-of-the-art section. Figures 1 and 2 are derived from this experiment.
- "RQ1_additional": This experiment runs RAL# and IF with different conformance testing implementations. Figures 6 and 7 are derived from this experiment.
- "RQ2_additional": This experiment runs different conformance testing implementations for learning and fingerprinting. Figure 8 is derived from this experiment.
- "RQ3": This experiment keeps the conformance testing for fingerprinting consistent while changing the learning conformance test during IF. Figure 3 is derived from this.
- "duplicates": This experiment runs IF on a benchmark with different number of copies per unique model. This is discussed in Section 6F.

Note that the `RQ0*_` experiments are only available for TLS, and `duplicates` only for MQTT.

## Example
Before running the experiments, please install all libraries by running 
```
    pip install -r requirements.txt
```

To run experiment the following command can be used:
```
    python3 ./fingerprinting/FingerprintingExperiments.py `experimentname` `benchmarkname` -r 20 -p 3
```
Here `-r` indicates the number of runs, which is set to 20 for our experiments. Parameter `-p` indicates the number of processes and is set to 3 as default value. For example,
```
    python3 ./fingerprinting/FingerprintingExperiments.py "RQ3" "BLE" -r 20 -p 3
```

Running this command will append results to file `./results/RQ3_BLE.csv`. 

Experiments starting with RQ0 are only available for TLS and duplicates is only available for MQTT. Note that the experiments cannot be replicated for BLEDiff as the models are not publicly available. Note that RQ1 and RQ2 should be execute together as `RQ1_RQ2`.

## Plots
To re-generate the plots, run:
```
    python3 ./fingerprinting/plot/plot_RQ*.py
```

For example, to plot Figure 3, stored in `RQ1.png` run:
```
    python3 ./fingerprinting/plots/plot_RQ1.py
```

All results are contained in the artifact, thus, each figure can be reproduced without running any experiments.

## Runtime Info
Small benchmarks like `BLE` that have up to 40 implementations of up to 16 states generally take less than 15 minutes to run for any experiment. The most time costly benchmark is `SSH` as it has the biggest models. To give an estimation: performing `RQ3` with `SSH` takes roughly 3 hours when using 40 processes.

# Learning a list of Implementations
Besides running the experiments detailed in the paper, this artifact can be used to make new experiments using the following command:
```
python3 ./fingerprinting/FingerprintingInterface.py 'benchmark' 'algorithm'
```
This will run the specified algorithm on a directory containing `.dot` models and provides a summary after executions. For example:

```
> python3 ./fingerprinting/FingerprintingInterface.py "./TLS/mbedtls/" "IF"
-----------------------------------
Learning Finished of ./TLS/mbedtls/ using IF with:
  - Fingerprint Algorithm: ADG,
  - Fingerprint Conformance Check: RandomWp100,
  - Learning Algorithm: AL#,
  - Learning Conformance Check: RandomWp100.
-----------------------------------
Accuracy
 # Number of Implementations          : 332
 # Found Specifications               : 6
 # Correctly Learned Implementations  : 100.0%
-----------------------------------
Fingerprinting
 # Queries  : 724
 # Steps    : 2467
Fingerprint Conformance Check
 # Queries  : 191507
 # Steps    : 1192218
Learning
 # Queries  : 4585
 # Steps    : 25235
-----------------------------------
```

The following mandatory arguments should be provided:
- Path to the directory with the implementations.
- Algorithm to use ('IF', 'RL#', 'RAL#').

The following *optional* arguments are available:
- `specifications_directory`: Path to the directory with the specifications.
- `fcq`: Conformance checking algorithm to use after fingerprinting ('PerfectKnowledge', 'RandomWord1000', 'RandomWp100'), only necessary with `IF`. Default='RandomWp100'.
- `lcq`: Conformance checking algorithm to use after learning ('PerfectKnowledge', 'RandomWord1000', 'RandomWp100'), default='RandomWp100'.
- `fingerprint`: Fingerprinting algorithm ('SepSeq', 'ADG'), only necessary with `IF`. Default='ADG'.
- `learning`: Learning algorithm ('AL#', 'L#'), only necessary with `IF`. Default="AL#".
- `print_mapping`: Boolean to indicate whether the mapping should be printed, default="False".
- `seed`: Seed used for randomization, default=0.