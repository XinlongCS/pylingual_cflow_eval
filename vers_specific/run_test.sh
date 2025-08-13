#!/bin/bash
rm -rf /tmp/cflow_test/3*

tmux new-session -d -s py_versions
for version in 6 7 8 9 10 11 12 13; do
    tmux split-window -t py_versions "python ~/pylingual/dev_scripts/cflow.py ~/pylingual_eval/py_files/random1_py_paths3_${version}_files.txt -v 3.${version}"
    tmux select-layout -t py_versions tiled
done
tmux attach -t py_versions