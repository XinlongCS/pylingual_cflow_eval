Parse files
```bash
for version in 3.6 3.7 3.8 3.9 3.10 3.11 3.12 3.13; do
    echo "Running with Python $version..."
    python dev_scripts/cflow.py /syssec-nas1/pyc-research/evaluation_sets/rand_py_paths.txt -v "$version"
    echo "----------------------------------"
done
```

Save results
```bash
for version in 3.6 3.7 3.8 3.9 3.10 3.11 3.12 3.13; do
    # Convert version number to underscore format (3.6 -> 3_6)
    version_underscore=${version/./_}
    
    echo "Running with Python $version..."
    echo "Output will be saved to 2results${version_underscore}.txt"
    python parse_results.py "/tmp/cflow_test/${version}/rand_py_paths_0/results.json" > "2results${version_underscore}.txt"
    echo "----------------------------------"
done
```

Summarize results
```bash
python summary_script.py . 1 --output ./summary
```

Compare summaries
```
python compare_summary.py summary/1summary.txt summary/2summary.txt comparison_report.txt
```