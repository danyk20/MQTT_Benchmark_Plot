# Visualise results from [MQTT Benchmark](https://github.com/danyk20/MQTT_Benchmark.git)

Current visualization expects data from three different test runs. Each test run has own subfolder inside of `data`
directory which contains all measured values. Name of the subfolder represents the number of subscribers measured in
that test. Inside those subfolders are textfiles (`.txt`) with arbitrary unique names. Each file represents a single
subscriber also called consumer. All those data within one subfolder will be averaged and plotted on the graph as single
line.

## Prerequisites

Run [MQTT Benchmark](https://github.com/danyk20/MQTT_Benchmark.git) to generate data for visualisation/

## Instruction

1. Replace example data with your data inside of `data` folder
2. Run the script

```shell
python3 show_graph.py
```