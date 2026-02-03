#!/usr/bin/env python3
"""
Location Manager for Atomic Clock Display

Manages atomic clock locations and timezone conversions.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pytz
from time_sync import AtomicTimeSync
from config_watcher import ConfigWatcher


class LocationManager:
    """Manage atomic clock locations and timezone conversions."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize location manager.
        
        Args:
            config_path: Path to locations.json config file
        """
        if config_path is None:
            # Default to config/locations.json relative to this file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, 'config', 'locations.json')
        
        self.config_path = config_path
        self.locations = []
        self.time_sync = AtomicTimeSync()
        self.load_locations()
    
    def load_locations(self) -> bool:
        """
        Load locations from configuration file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.locations = config.get('locations', [])
            
            # Validate locations
            for loc in self.locations:
                if not all(key in loc for key in ['id', 'name', 'timezone', 'corner']):
                    raise ValueError(f"Invalid location configuration: {loc}")
            
            return True
            
        except FileNotFoundError:
            print(f"Warning: Config file not found: {self.config_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return False
        except Exception as e:
            print(f"Error loading locations: {e}")
            return False
    
    def get_location(self, location_id: str) -> Optional[Dict]:
        """
        Get location configuration by ID.
        
        Args:
            location_id: Location identifier
            
        Returns:
            Location dictionary or None if not found
        """
        for loc in self.locations:
            if loc['id'] == location_id:
                return loc
        return None
    
    def get_location_time(self, location_id: str) -> Optional[datetime]:
        """
        Get current time for a specific location.
        
        Args:
            location_id: Location identifier
            
        Returns:
            Current time in location's timezone, or None if location not found
        """
        location = self.get_location(location_id)
        if not location:
            return None
        
        try:
            # Get UTC time from atomic clock sync
            utc_time = self.time_sync.get_atomic_time()
            
            # Convert to location timezone
            tz_obj = pytz.timezone(location['timezone'])
            local_time = utc_time.astimezone(tz_obj)
            
            return local_time
            
        except Exception as e:
            print(f"Error getting time for {location_id}: {e}")
            return None
    
    def format_time_for_display(self, time: datetime, location: Dict) -> str:
        """
        Format time string for display.
        
        Args:
            time: datetime object
            location: Location dictionary
            
        Returns:
            Formatted time string
        """
        if time is None:
            return "N/A"
        
        # Format: HH:MM:SS
        time_str = time.strftime("%H:%M:%S")
        
        return time_str
    
    def get_utc_offset(self, location: Dict) -> str:
        """
        Get UTC offset string for location.
        
        Args:
            location: Location dictionary
            
        Returns:
            UTC offset string (e.g., "+00:00", "-07:00")
        """
        try:
            tz_obj = pytz.timezone(location['timezone'])
            utc_time = datetime.now(pytz.UTC)
            local_time = utc_time.astimezone(tz_obj)
            offset = local_time.utcoffset()
            
            # Format offset as +/-HH:MM
            total_seconds = int(offset.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            sign = '+' if hours >= 0 else '-'
            return f"{sign}{abs(hours):02d}:{abs(minutes):02d}"
            
        except Exception as e:
            return "N/A"
    
    def get_all_location_times(self) -> Dict[str, Dict]:
        """
        Get current times for all configured locations.
        
        Returns:
            Dictionary mapping location_id to time information
        """
        result = {}
        
        for location in self.locations:
            location_id = location['id']
            local_time = self.get_location_time(location_id)
            
            result[location_id] = {
                'location': location,
                'time': local_time,
                'time_str': self.format_time_for_display(local_time, location),
                'utc_offset': self.get_utc_offset(location),
                'corner': location.get('corner', 'unknown')
            }
        
        return result
    
    def get_location_by_corner(self, corner: str) -> Optional[Dict]:
        """
        Get location configuration by corner position.
        
        Args:
            corner: Corner identifier (top_left, top_right, bottom_left, bottom_right)
            
        Returns:
            Location dictionary or None if not found
        """
        for loc in self.locations:
            if loc.get('corner') == corner:
                return loc
        return None
    
    def get_corner_time_info(self, corner: str) -> Optional[Dict]:
        """
        Get formatted time information for a corner.
        
        Args:
            corner: Corner identifier
            
        Returns:
            Dictionary with formatted time info for display, or None
        """
        location = self.get_location_by_corner(corner)
        if not location:
            return None
        
        local_time = self.get_location_time(location['id'])
        if not local_time:
            return None
        
        return {
            'name': location['name'],
            'city': location.get('city', ''),
            'time': self.format_time_for_display(local_time, location),
            'utc_offset': self.get_utc_offset(location),
            'date': local_time.strftime("%Y-%m-%d") if local_time else None
        }


if __name__ == '__main__':
    # Test location manager
    print("Testing location manager...")
    manager = LocationManager()
    
    print(f"Loaded {len(manager.locations)} locations")
    
    for location in manager.locations:
        print(f"\n{location['name']} ({location['id']}):")
        time_info = manager.get_corner_time_info(location['corner'])
        if time_info:
            print(f"  Time: {time_info['time']}")
            print(f"  UTC Offset: {time_info['utc_offset']}")
            print(f"  City: {time_info['city']}")
