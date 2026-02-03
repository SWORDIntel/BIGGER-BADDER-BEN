#!/usr/bin/env python3
"""
Unit tests for LocationManager
"""

import unittest
import tempfile
import json
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from location_manager import LocationManager


class TestLocationManager(unittest.TestCase):
    """Test cases for LocationManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "locations": [
                {
                    "id": "utc",
                    "name": "UTC",
                    "timezone": "UTC",
                    "corner": "top_left",
                    "city": "Universal"
                },
                {
                    "id": "denver",
                    "name": "Denver",
                    "timezone": "America/Denver",
                    "corner": "top_right",
                    "city": "Colorado"
                },
                {
                    "id": "tokyo",
                    "name": "Tokyo",
                    "timezone": "Asia/Tokyo",
                    "corner": "bottom_left",
                    "city": "Japan"
                },
                {
                    "id": "london",
                    "name": "London",
                    "timezone": "Europe/London",
                    "corner": "bottom_right",
                    "city": "UK"
                }
            ]
        }
        
        # Create temporary config file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_file)
        self.temp_file.close()
        
        self.location_manager = LocationManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    def test_load_locations_success(self):
        """Test successful loading of locations."""
        self.assertTrue(self.location_manager.load_locations())
        self.assertEqual(len(self.location_manager.locations), 4)
        
        # Check first location
        location = self.location_manager.locations[0]
        self.assertEqual(location['id'], 'utc')
        self.assertEqual(location['name'], 'UTC')
        self.assertEqual(location['timezone'], 'UTC')
        self.assertEqual(location['corner'], 'top_left')
    
    def test_load_locations_file_not_found(self):
        """Test loading when config file doesn't exist."""
        manager = LocationManager('/nonexistent/file.json')
        self.assertFalse(manager.load_locations())
        self.assertEqual(len(manager.locations), 0)
    
    def test_load_locations_invalid_json(self):
        """Test loading with invalid JSON."""
        # Create invalid JSON file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write('{"invalid": json}')
        temp_file.close()
        
        manager = LocationManager(temp_file.name)
        self.assertFalse(manager.load_locations())
        
        os.unlink(temp_file.name)
    
    def test_load_locations_missing_required_fields(self):
        """Test loading with missing required fields."""
        invalid_config = {
            "locations": [
                {
                    "id": "test",
                    "name": "Test"
                    # Missing timezone and corner
                }
            ]
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(invalid_config, temp_file)
        temp_file.close()
        
        manager = LocationManager(temp_file.name)
        self.assertFalse(manager.load_locations())
        
        os.unlink(temp_file.name)
    
    def test_get_location(self):
        """Test getting location by ID."""
        location = self.location_manager.get_location('denver')
        self.assertIsNotNone(location)
        self.assertEqual(location['name'], 'Denver')
        self.assertEqual(location['timezone'], 'America/Denver')
        
        # Test non-existent location
        location = self.location_manager.get_location('nonexistent')
        self.assertIsNone(location)
    
    def test_get_location_by_corner(self):
        """Test getting location by corner position."""
        location = self.location_manager.get_location_by_corner('top_right')
        self.assertIsNotNone(location)
        self.assertEqual(location['id'], 'denver')
        
        # Test non-existent corner
        location = self.location_manager.get_location_by_corner('center')
        self.assertIsNone(location)
    
    @patch('location_manager.AtomicTimeSync')
    def test_get_location_time(self, mock_sync):
        """Test getting time for a location."""
        # Mock time sync
        mock_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_sync_instance = MagicMock()
        mock_sync_instance.get_atomic_time.return_value = mock_time
        mock_sync.return_value = mock_sync_instance
        
        manager = LocationManager(self.temp_file.name)
        manager.time_sync = mock_sync_instance
        
        time = manager.get_location_time('denver')
        self.assertIsNotNone(time)
        self.assertIsInstance(time, datetime)
        
        # Test non-existent location
        time = manager.get_location_time('nonexistent')
        self.assertIsNone(time)
    
    def test_format_time_for_display(self):
        """Test time formatting for display."""
        test_time = datetime(2023, 1, 1, 12, 30, 45)
        location = self.location_manager.get_location('denver')
        
        formatted = self.location_manager.format_time_for_display(test_time, location)
        self.assertEqual(formatted, "12:30:45")
        
        # Test with None time
        formatted = self.location_manager.format_time_for_display(None, location)
        self.assertEqual(formatted, "N/A")
    
    def test_get_utc_offset(self):
        """Test UTC offset calculation."""
        location = self.location_manager.get_location('utc')
        offset = self.location_manager.get_utc_offset(location)
        self.assertEqual(offset, "+00:00")
        
        location = self.location_manager.get_location('denver')
        offset = self.location_manager.get_utc_offset(location)
        # Denver should be either -07:00 or -06:00 depending on DST
        self.assertTrue(offset in ["-07:00", "-06:00"])
    
    def test_get_all_location_times(self):
        """Test getting times for all locations."""
        with patch('location_manager.AtomicTimeSync') as mock_sync:
            mock_time = datetime(2023, 1, 1, 12, 0, 0)
            mock_sync_instance = MagicMock()
            mock_sync_instance.get_atomic_time.return_value = mock_time
            mock_sync.return_value = mock_sync_instance
            
            manager = LocationManager(self.temp_file.name)
            manager.time_sync = mock_sync_instance
            
            all_times = manager.get_all_location_times()
            
            self.assertEqual(len(all_times), 4)
            
            for location_id, info in all_times.items():
                self.assertIn('location', info)
                self.assertIn('time', info)
                self.assertIn('time_str', info)
                self.assertIn('utc_offset', info)
                self.assertIn('corner', info)
    
    def test_get_corner_time_info(self):
        """Test getting formatted time info for a corner."""
        with patch('location_manager.AtomicTimeSync') as mock_sync:
            mock_time = datetime(2023, 1, 1, 12, 0, 0)
            mock_sync_instance = MagicMock()
            mock_sync_instance.get_atomic_time.return_value = mock_time
            mock_sync.return_value = mock_sync_instance
            
            manager = LocationManager(self.temp_file.name)
            manager.time_sync = mock_sync_instance
            
            info = manager.get_corner_time_info('top_right')
            
            self.assertIsNotNone(info)
            self.assertEqual(info['name'], 'Denver')
            self.assertEqual(info['city'], 'Colorado')
            self.assertIn('time', info)
            self.assertIn('utc_offset', info)
            self.assertIn('date', info)
            
            # Test non-existent corner
            info = manager.get_corner_time_info('center')
            self.assertIsNone(info)


if __name__ == '__main__':
    unittest.main()
