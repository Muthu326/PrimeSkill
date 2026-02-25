"""
Cache Manager - Fast JSON-based caching for market scan results
Enables instant page load by reading cached data while new scan runs in background
"""
import json
import os
import numpy as np
from datetime import datetime
from pathlib import Path

class ScanCacheManager:
    def __init__(self, cache_file="data/scan_cache.json"):
        self.cache_file = Path(__file__).parent.parent / cache_file
        self._ensure_cache_exists()
    
    def _sanitize_data(self, obj):
        """🛡️ Recursive sanitizer to replace NaN/Inf with None (null)"""
        if isinstance(obj, dict):
            return {k: self._sanitize_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_data(i) for i in obj]
        elif isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
        return obj

    def _ensure_cache_exists(self):
        """Create cache file if it doesn't exist"""
        if not self.cache_file.exists():
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_cache({
                "last_update": "",
                "scan_data": [],
                "index_picks": [],
                "diamond_picks": []
            })
    
    def _write_cache(self, data):
        """Write data to cache file"""
        try:
            # Sanitize before writing to prevent "Unexpected token 'N' (NaN)" in JS
            sanitized_data = self._sanitize_data(data)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(sanitized_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def _read_cache(self):
        """Read data from cache file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Cache read error: {e}")
        return {
            "last_update": "",
            "scan_data": [],
            "index_picks": [],
            "diamond_picks": []
        }
    
    def save_scan_results(self, scan_data, index_picks=None, diamond_picks=None):
        """Save scan results to cache with timestamp"""
        cache_data = {
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "scan_data": scan_data if scan_data else [],
            "index_picks": index_picks if index_picks else [],
            "diamond_picks": diamond_picks if diamond_picks else []
        }
        self._write_cache(cache_data)
    
    def load_scan_results(self):
        """Load cached scan results"""
        cache = self._read_cache()
        return cache.get('scan_data', []), cache.get('index_picks', []), cache.get('diamond_picks', [])
    
    def get_cache_age(self):
        """Get age of cache in minutes"""
        cache = self._read_cache()
        last_update = cache.get('last_update', '')
        if not last_update:
            return 999999  # Very old
        
        try:
            cache_time = datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
            age_seconds = (datetime.now() - cache_time).total_seconds()
            return age_seconds / 60  # Return minutes
        except:
            return 999999
    
    def is_cache_fresh(self, max_age_minutes=5):
        """Check if cache is fresh (less than max_age_minutes old)"""
        return self.get_cache_age() < max_age_minutes
    
    def get_last_update(self):
        """Get last update timestamp string"""
        cache = self._read_cache()
        return cache.get('last_update', 'Never')
