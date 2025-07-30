import json
from pathlib import Path

def parse_and_format_results(json_path):
    # Load the JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Get all failed files
    compile_errors = data.get('compile_error', [])
    failures = data.get('failure', [])
    errors = data.get('error', [])  # New: Capture runtime errors
    all_failures = compile_errors + failures + errors  # Include errors in total failures
    
    # Count totals
    total_files = sum(len(v) for v in data.values() if isinstance(v, list))
    total_success = len(data.get('success', []))
    total_failures = len(failures)
    total_compile_errors = len(compile_errors)
    total_errors = len(errors)  # New: Count runtime errors
    
    # Format the output
    output = []
    output.append(f"Total files processed: {total_files}")
    output.append(f"Success: {total_success} ({total_success/total_files:.1%})")
    output.append(f"Total failures: {len(all_failures)} ({len(all_failures)/total_files:.1%})")
    output.append(f"  - Reconstruction failures: {total_failures}")
    output.append(f"  - Compile errors: {total_compile_errors}")
    output.append(f"  - Runtime errors: {total_errors}")  # New: Show runtime errors count
    
    # Combined sorted failures section
    if all_failures:
        output.append("\n=== All Failed Files (Sorted) ===")
        # Sort by filename (case sensitive)
        sorted_failures = sorted(
            all_failures,
            key=lambda x: Path(x).name
        )
        for i, filepath in enumerate(sorted_failures, 1):
            filename = Path(filepath).name
            # Determine failure type
            if filepath in compile_errors:
                failure_type = "COMPILE ERROR"
            elif filepath in errors:
                failure_type = "RUNTIME ERROR"
            else:
                failure_type = "RECONSTRUCTION FAILURE"
            output.append(f"{i}. {filename} [{failure_type}] (path: {filepath})")
    
    # Detailed sections for each failure type
    output.append("\n=== Detailed Breakdown ===")
    
    # Runtime errors section (new)
    if errors:
        output.append("\nRuntime Errors:")
        sorted_errors = sorted(
            errors,
            key=lambda x: Path(x).name
        )
        for i, filepath in enumerate(sorted_errors, 1):
            filename = Path(filepath).name
            output.append(f"{i}. {filename} (path: {filepath})")
    
    # Compile errors section
    if compile_errors:
        output.append("\nCompile Errors:")
        sorted_compile_errors = sorted(
            compile_errors,
            key=lambda x: Path(x).name
        )
        for i, filepath in enumerate(sorted_compile_errors, 1):
            filename = Path(filepath).name
            output.append(f"{i}. {filename} (path: {filepath})")
    
    # Reconstruction failures section
    if failures:
        output.append("\nReconstruction Failures:")
        sorted_failures = sorted(
            failures,
            key=lambda x: Path(x).name
        )
        for i, filepath in enumerate(sorted_failures, 1):
            filename = Path(filepath).name
            output.append(f"{i}. {filename} (path: {filepath})")
    
    return '\n'.join(output)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python parse_results.py <results.json>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    formatted_output = parse_and_format_results(json_path)
    print(formatted_output)