#!/bin/bash
rm -rf /tmp/cflow_test/3*

tmux new-session -d -s py_versions
for version in 13 12 11 10 9 8 7 6; do
    tmux split-window -t py_versions "python ~/pylingual/dev_scripts/cflow.py ~/pylingual_eval/py_files/med_eval/med_eval_3_${version}.txt -v 3.${version}"
    tmux select-layout -t py_versions tiled
done
tmux attach -t py_versions