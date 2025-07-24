import re
import os
import sys
from collections import defaultdict
from packaging import version

def find_highest_summaries(summary_dir):
    """Find the two highest-numbered summary files in the directory"""
    summary_files = []
    
    for filename in os.listdir(summary_dir):
        match = re.match(r'^(\d+)summary\.txt$', filename)
        if match:
            num = int(match.group(1))
            summary_files.append((num, os.path.join(summary_dir, filename)))
    
    if len(summary_files) < 2:
        raise ValueError(f"Need at least 2 summary files in {summary_dir}, found {len(summary_files)}")
    
    # Sort by number in descending order
    summary_files.sort(reverse=True, key=lambda x: x[0])
    return summary_files[0][1], summary_files[1][1]

def parse_summary_file(file_path):
    """Parse a summary file and return a dictionary of version stats"""
    version_stats = defaultdict(dict)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='utf-16') as f:
            content = f.read()
    
    version_entries = re.findall(
        r'(\d+\.\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\(([\d.]+)%\)\s*\|\s*(\d+)\s*\(([\d.]+)%\)\s*\|\s*(\d+)\s*\(([\d.]+)%\)',
        content
    )
    
    for entry in version_entries:
        ver = entry[0]
        version_stats[ver] = {
            'total': int(entry[1]),
            'success_count': int(entry[2]),
            'success_pct': float(entry[3]),
            'recon_count': int(entry[4]),
            'recon_pct': float(entry[5]),
            'compile_count': int(entry[6]),
            'compile_pct': float(entry[7])
        }
    
    return version_stats

def parse_result_file(file_path):
    """Parse individual result file to get detailed failure information"""
    failures = {'recon': [], 'compile': []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='utf-16') as f:
            content = f.read()
    
    recon_matches = re.finditer(
        r'^\d+\.\s+(.+?)\s+\[RECONSTRUCTION FAILURE\]\s*\(path:\s*(.+?)\)',
        content,
        re.MULTILINE
    )
    for match in recon_matches:
        failures['recon'].append({
            'filename': match.group(1),
            'path': match.group(2)
        })
    
    compile_matches = re.finditer(
        r'^\d+\.\s+(.+?)\s+\[COMPILE ERROR\]\s*\(path:\s*(.+?)\)',
        content,
        re.MULTILINE
    )
    for match in compile_matches:
        failures['compile'].append({
            'filename': match.group(1),
            'path': match.group(2)
        })
    
    return failures

def find_result_files(base_dir, prefix):
    """Find all result files for a given prefix across versions"""
    version_files = {}
    
    for dir_name in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.isdir(dir_path):
            continue
        
        ver = dir_name.replace('-', '.')
        if not re.match(r'^\d+\.\d+$', ver):
            continue
        
        for file_name in os.listdir(dir_path):
            if re.match(rf'^{prefix}results{ver.replace(".", "_")}.*\.txt$', file_name, re.IGNORECASE):
                version_files[ver] = os.path.join(dir_path, file_name)
                break
    
    return version_files

def generate_comparison_report(file1, file2, base_dir, output_dir):
    """Generate the full comparison report"""
    stats1 = parse_summary_file(file1)
    stats2 = parse_summary_file(file2)
    
    # Extract the full number prefix from filenames (e.g., "9" from "9summary.txt")
    prefix1 = os.path.basename(file1).split('summary')[0]
    prefix2 = os.path.basename(file2).split('summary')[0]
    
    result_files1 = find_result_files(base_dir, prefix1)
    result_files2 = find_result_files(base_dir, prefix2)
    
    versions = sorted(set(stats1.keys()).union(set(stats2.keys())), key=lambda x: version.parse(x))
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename based on input prefixes
    output_file = os.path.join(output_dir, f"{prefix1}comparison_report.txt")
    
    report = []
    report.append("COMPARATIVE ANALYSIS OF TEST RESULTS".center(100))
    report.append("=" * 100)
    report.append(f"Comparing {os.path.basename(file1)} (old) vs {os.path.basename(file2)} (new)")
    report.append("=" * 100)
    
    # Summary comparison
    report.append("\nSUMMARY COMPARISON")
    report.append("=" * 100)
    report.append("Version | Total  | Success (Δcnt/Δ%)   | Recon Fail (Δcnt/Δ%) | Compile Err (Δcnt/Δ%)  | Trend")
    report.append("--------|--------|---------------------|----------------------|------------------------|------------")
    
    for ver in versions:
        if ver not in stats1 or ver not in stats2:
            continue
            
        s1 = stats1[ver]
        s2 = stats2[ver]
        
        scnt = s2['success_count'] - s1['success_count']
        spct = s2['success_pct'] - s1['success_pct']
        rcnt = s2['recon_count'] - s1['recon_count']
        rpct = s2['recon_pct'] - s1['recon_pct']
        ccnt = s2['compile_count'] - s1['compile_count']
        cpct = s2['compile_pct'] - s1['compile_pct']
        
        success_val = f"{s2['success_count']} ({scnt:>+1}/{spct:>+1.1f}%)"
        recon_val = f"{s2['recon_count']} ({rcnt:>+1}/{rpct:>+1.1f}%)"
        compile_val = f"{s2['compile_count']} ({ccnt:>+1}/{cpct:>+1.1f}%)"
        trend = "IMPROVED" if scnt > 0 else "WORSENED" if scnt < 0 else "MIXED"
        
        report.append(f"{ver:7} | {s1['total']:6} | {success_val:19} | {recon_val:20} | {compile_val:22} | {trend}")
    
    # Detailed comparisons
    report.append("\n" + "=" * 100)
    report.append("DETAILED VERSION COMPARISONS")
    report.append("=" * 100)
    
    for ver in versions:
        if ver not in result_files1 or ver not in result_files2:
            continue
        
        failures1 = parse_result_file(result_files1[ver])
        failures2 = parse_result_file(result_files2[ver])
        
        old_failures = {f['path'] for f in failures1['recon'] + failures1['compile']}
        new_failures = {f['path'] for f in failures2['recon'] + failures2['compile']}
        
        fixed_files = old_failures - new_failures
        broken_files = new_failures - old_failures
        same_failures = old_failures & new_failures
        
        old_success = stats1[ver]['success_pct'] if ver in stats1 else 0
        new_success = stats2[ver]['success_pct'] if ver in stats2 else 0
        success_delta = new_success - old_success
        
        report.append(f"\nComparison for Python {ver}")
        report.append("-" * 100)
        report.append(f"Old: {result_files1[ver]} (Success: {old_success:.1f}%)")
        report.append(f"New: {result_files2[ver]} (Success: {new_success:.1f}%)")
        report.append(f"Success Rate Change: {success_delta:+.1f}%")
        
        report.append(f"\nFixed files ({len(fixed_files)}):")
        report.extend([f" - {path}" for path in sorted(fixed_files)[:10]])
        if len(fixed_files) > 10:
            report.append(f"... and {len(fixed_files)-10} more")
        
        report.append(f"\nBroken files ({len(broken_files)}):")
        report.extend([f" - {path}" for path in sorted(broken_files)[:10]])
        if len(broken_files) > 10:
            report.append(f"... and {len(broken_files)-10} more")
        
        report.append(f"\nStill failing ({len(same_failures)}):")
        report.extend([f" - {path}" for path in sorted(same_failures)[:10]])
        if len(same_failures) > 10:
            report.append(f"... and {len(same_failures)-10} more")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"Comparison report generated: {output_file}")

def main():
    # Default directories
    summary_dir = "summary"
    result_dir = "."
    output_dir = "summary_comparisons"
    
    try:
        # Find the two highest summary files
        file2, file1 = find_highest_summaries(summary_dir)
        print(f"Found summary files to compare:")
        print(f" - {file1}")
        print(f" - {file2}")
        
        # Generate comparison
        generate_comparison_report(file1, file2, result_dir, output_dir)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()