#!/bin/bash
for version in 3.6 3.7 3.8 3.9 3.10 3.11 3.12 3.13; do
    # Convert version number to underscore format (3.6 -> 3_6)
    version_underscore=${version/./_}
    
    # Find the highest existing results file number
    max_num=0
    for file in "${version}/"*results"${version_underscore}.txt"; do
        if [[ $file =~ ([0-9]+)results${version_underscore}\.txt ]]; then
            num=${BASH_REMATCH[1]}
            if (( num > max_num )); then
                max_num=$num
            fi
        fi
    done
    
    # Increment the number for the new file
    new_num=$((max_num + 1))
    
    echo "Running with Python $version..."
    echo "Output will be saved to ${version}/${new_num}results${version_underscore}.txt"
    python ~/pylingual_eval/parse_results.py "/tmp/cflow_test/${version}/fast_eval_${version_underscore}_files_0/results.json" > "${version}/${new_num}results${version_underscore}.txt"
    echo "----------------------------------"
done

# Summarize results
python ~/pylingual_eval/summarize_results.py . ${new_num} --output ./summary

# Compare summaries
python ~/pylingual_eval/compare_summary.py