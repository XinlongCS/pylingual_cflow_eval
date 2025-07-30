#!/bin/bash
rm -rf /tmp/cflow_test/3.*

tmux new-session -d -s py_versions
for version in 3.6 3.7 3.8 3.9 3.10 3.11 3.12 3.13; do
    tmux split-window -t py_versions "python ~/pylingual/dev_scripts/cflow.py /syssec-nas1/pyc-research/evaluation_sets/rand_py_paths.txt -v $version"
    tmux select-layout -t py_versions tiled
done
tmux attach -t py_versions