import re
from collections import defaultdict
import sys

def parse_summary_file(file_path):
    """Parse a summary file and return a dictionary of version stats"""
    version_stats = defaultdict(dict)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='utf-16') as f:
            content = f.read()
    
    # Find all version entries using more flexible regex
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

def compare_summaries(file1, file2, output_file='comparison.txt'):
    """Compare two summary files with perfect alignment"""
    stats1 = parse_summary_file(file1)
    stats2 = parse_summary_file(file2)
    
    # Sort versions numerically
    def version_key(v):
        major, minor = v.split('.')
        return (int(major), int(minor))
    
    versions = sorted(set(stats1.keys()).union(set(stats2.keys())), key=version_key)
    
    # Column specifications
    columns = [
        {'name': 'Version', 'width': 7, 'align': '<'},
        {'name': 'Total', 'width': 7, 'align': '>'},
        {'name': 'Success (Δcnt/Δ%)', 'width': 20, 'align': '>'},
        {'name': 'Recon Fail (Δcnt/Δ%)', 'width': 20, 'align': '>'},
        {'name': 'Compile Error (Δcnt/Δ%)', 'width': 20, 'align': '>'},
        {'name': 'Trend', 'width': 9, 'align': '<'}
    ]
    
    # Build header
    header_parts = []
    separator_parts = []
    for col in columns:
        header_parts.append(f"{col['name']:{col['align']}{col['width']}}")
        separator_parts.append('-' * col['width'])
    
    header = " | ".join(header_parts)
    separator = "-+-".join(separator_parts)
    
    report = []
    report.append("COMPARATIVE ANALYSIS OF TEST RESULTS".center(len(header)))
    report.append("=" * len(header))
    report.append(header)
    report.append(separator)
    
    for ver in versions:
        if ver not in stats1 or ver not in stats2:
            continue
            
        s1 = stats1[ver]
        s2 = stats2[ver]
        
        # Calculate differences
        scnt = s2['success_count'] - s1['success_count']
        spct = s2['success_pct'] - s1['success_pct']
        rcnt = s2['recon_count'] - s1['recon_count']
        rpct = s2['recon_pct'] - s1['recon_pct']
        ccnt = s2['compile_count'] - s1['compile_count']
        cpct = s2['compile_pct'] - s1['compile_pct']
        
        # Format values
        success_val = f"{scnt:>+4}/{spct:>+6.1f}%"
        recon_val = f"{rcnt:>+4}/{rpct:>+6.1f}%"
        compile_val = f"{ccnt:>+4}/{cpct:>+6.1f}%"
        trend = "IMPROVED" if scnt > 0 else "WORSENED" if scnt < 0 else "MIXED"
        
        # Build row
        row_parts = [
            f"{ver:<7}",
            f"{s1['total']:>7}",
            f"{success_val:>20}",
            f"{recon_val:>20}",
            f"{compile_val:>20}",
            f"{trend:<9}"
        ]
        report.append(" | ".join(row_parts))
    
    # Generate output
    output = "\n".join(report)
    print(output)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_summary.py <file1> <file2> [output_file]")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else 'comparison.txt'
    
    compare_summaries(file1, file2, output_file)