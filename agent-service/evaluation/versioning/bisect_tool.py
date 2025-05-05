import subprocess
from typing import Optional

def bisect_performance(start: str, end: str) -> Optional[str]:
    """Find performance regression commit"""
    result = subprocess.run(
        ["git", "bisect", "start", start, end],
        capture_output=True)
    
    # Automated test script
    subprocess.run(
        ["git", "bisect", "run", 
         "python evaluation/offline/benchmark.py --threshold=0.85"])
    
    bad_commit = subprocess.check_output(
        ["git", "bisect", "log"]).decode()
    
    return extract_commit_hash(bad_commit)