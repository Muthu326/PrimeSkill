import json
import os
import numpy as np

cache_file = "data/scan_cache.json"
inst_file = "data/inst_scanner_results.json"
pro_file = "data/pro_v2_dashboard.json"

def sanitize(obj):
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(i) for i in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
    return obj

for file_path in [cache_file, inst_file, pro_file]:
    if os.path.exists(file_path):
        print(f"Cleaning {file_path}...")
        try:
            # Use a more flexible loader for the broken JSON if possible
            # But standard json.load will fail on NaN. 
            # We can use a regex replacement or just delete and regenerate.
            # actually, let's try reading it as text and replacing NaN
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace NaN with null
            fixed_content = content.replace(': NaN', ': null').replace(': Infinity', ': null').replace(': -Infinity', ': null')
            
            # Validate and format
            data = json.loads(fixed_content)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Successfully cleaned {file_path}")
        except Exception as e:
            print(f"Error cleaning {file_path}: {e}")
            # If it's too broken, just delete it
            # os.remove(file_path)
