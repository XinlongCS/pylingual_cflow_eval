import os
import re
from packaging import version

def parse_result_file(file_path):
    """Extract success/failure stats from a single result file."""
    stats = {
        'total': 0,
        'success': {'count': 0, 'pct': 0.0},
        'recon_fail': {'count': 0, 'pct': 0.0},
        'compile_error': {'count': 0, 'pct': 0.0}
    }
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Extract total files processed
            total_match = re.search(r'Total files processed:\s*(\d+)', content)
            if total_match:
                stats['total'] = int(total_match.group(1))
            
            # Extract success count and percentage
            success_match = re.search(r'Success:\s*(\d+)\s*\(([\d.]+)%\)', content)
            if success_match:
                stats['success']['count'] = int(success_match.group(1))
                stats['success']['pct'] = float(success_match.group(2))
            
            # Extract total failures (to verify our counts)
            total_failures = 0
            failures_match = re.search(r'Total failures:\s*(\d+)\s*\(([\d.]+)%\)', content)
            if failures_match:
                total_failures = int(failures_match.group(1))
            
            # Improved reconstruction failures extraction
            recon_match = re.search(r'Reconstruction failures:\s*(\d+)\s*(?:\(([\d.]+)%\))?', content)
            if recon_match:
                stats['recon_fail']['count'] = int(recon_match.group(1))
                if recon_match.group(2):  # Percentage might be missing
                    stats['recon_fail']['pct'] = float(recon_match.group(2))
                else:
                    stats['recon_fail']['pct'] = (stats['recon_fail']['count'] / stats['total']) * 100
            
            # Improved compile errors extraction
            compile_match = re.search(r'Compile errors:\s*(\d+)\s*(?:\(([\d.]+)%\))?', content)
            if compile_match:
                stats['compile_error']['count'] = int(compile_match.group(1))
                if compile_match.group(2):  # Percentage might be missing
                    stats['compile_error']['pct'] = float(compile_match.group(2))
                else:
                    stats['compile_error']['pct'] = (stats['compile_error']['count'] / stats['total']) * 100
            
            # Verify counts add up correctly
            if stats['total'] > 0:
                calculated_total = (stats['success']['count'] + 
                                  stats['recon_fail']['count'] + 
                                  stats['compile_error']['count'])
                
                if total_failures > 0 and (stats['recon_fail']['count'] + stats['compile_error']['count']) != total_failures:
                    print(f"Warning: Failure count mismatch in {file_path}")
                    print(f"  Total failures: {total_failures}")
                    print(f"  Recon + Compile: {stats['recon_fail']['count'] + stats['compile_error']['count']}")
                
                if calculated_total != stats['total']:
                    print(f"Warning: Total count mismatch in {file_path}")
                    print(f"  Expected: {stats['total']}")
                    print(f"  Calculated: {calculated_total}")
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return stats

def generate_summary(base_dir, number, output_dir="summary"):
    """Generate summary for all versions of a specific test number."""
    versions = ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12', '3.13']
    all_stats = {}
    
    os.makedirs(output_dir, exist_ok=True)
    
    for ver in versions:
        # Try both directory naming conventions
        dir_variants = [
            os.path.join(base_dir, ver.replace('.', '-')),  # 3-6
            os.path.join(base_dir, ver)                     # 3.6
        ]
        
        found_dir = None
        for dir_path in dir_variants:
            if os.path.exists(dir_path):
                found_dir = dir_path
                break
        
        if not found_dir:
            print(f"Warning: Directory not found for version {ver}")
            all_stats[ver] = {
                'total': 0,
                'success': {'count': 0, 'pct': 0.0},
                'recon_fail': {'count': 0, 'pct': 0.0},
                'compile_error': {'count': 0, 'pct': 0.0}
            }
            continue
        
        # Try different file name patterns
        file_patterns = [
            rf"^{number}results{ver.replace('.', '_')}.*\.txt$",    # 1results3_6.txt
        ]
        
        found_file = None
        for file in os.listdir(found_dir):
            for pattern in file_patterns:
                if re.match(pattern, file, re.IGNORECASE):
                    found_file = os.path.join(found_dir, file)
                    break
            if found_file:
                break
        
        if found_file:
            stats = parse_result_file(found_file)
            all_stats[ver] = stats
        else:
            print(f"Warning: No result file found for version {ver} in {found_dir}")
            all_stats[ver] = {
                'total': 0,
                'success': {'count': 0, 'pct': 0.0},
                'recon_fail': {'count': 0, 'pct': 0.0},
                'compile_error': {'count': 0, 'pct': 0.0}
            }
    
    # Generate summary output
    output_lines = [
        f"Summary for test number: {number}",
        "=" * 90,
        "Version  | Total Files | Success (count/%) | Recon Fail (count/%) | Compile Error (count/%)",
        "-" * 90
    ]
    
    # Sort versions numerically
    for ver in sorted(all_stats.keys(), key=lambda x: version.parse(x)):
        stats = all_stats[ver]
        
        if stats['total'] == 0:
            output_lines.append(
                f"{ver:7} | {'No data':11} | {'N/A':18} | {'N/A':20} | {'N/A':20}"
            )
            continue
            
        success_str = f"{stats['success']['count']} ({stats['success']['pct']:.1f}%)"
        recon_str = f"{stats['recon_fail']['count']} ({stats['recon_fail']['pct']:.1f}%)"
        compile_str = f"{stats['compile_error']['count']} ({stats['compile_error']['pct']:.1f}%)"
        
        output_lines.append(
            f"{ver:7} | {stats['total']:11} | {success_str:18} | {recon_str:20} | {compile_str:20}"
        )
    
    # Write to output file
    output_file = os.path.join(output_dir, f"{number}summary.txt")
    with open(output_file, 'w') as f:
        f.write("\n".join(output_lines))
    
    print(f"Summary saved to: {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate summary of test results across Python versions.')
    parser.add_argument('base_dir', help='Base directory containing version folders')
    parser.add_argument('number', help='Test number prefix (e.g., "001")')
    parser.add_argument('--output', default="summary", help='Output directory for summary files')
    
    args = parser.parse_args()
    generate_summary(args.base_dir, args.number, args.output)