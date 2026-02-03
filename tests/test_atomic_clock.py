#!/usr/bin/env python3
"""
Unit tests for atomic clock application.
"""

import unittest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from time_sync import AtomicTimeSync, TimeSyncError
from location_manager import LocationManager
from clock_renderer import ClockRenderer


class TestTimeSync(unittest.TestCase):
    """Test time synchronization module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sync = AtomicTimeSync()
    
    def test_initialization(self):
        """Test AtomicTimeSync initialization."""
        self.assertIsNotNone(self.sync)
        self.assertFalse(self.sync.sync_status)
        self.assertEqual(self.sync.offset, 0.0)
    
    @patch('time_sync.ntplib.NTPClient')
    def test_sync_with_ntp_success(self, mock_ntp_client):
        """Test successful NTP synchronization."""
        # Mock successful NTP response
        mock_response = MagicMock()
        mock_response.tx_time = 1234567890.0
        mock_client_instance = MagicMock()
        mock_client_instance.request.return_value = mock_response
        mock_ntp_client.return_value = mock_client_instance
        
        self.sync.ntp_client = mock_client_instance
        
        with patch('time.time', return_value=1234567890.5):
            result = self.sync.sync_with_ntp('time.nist.gov')
        
        # Should succeed (even if offset is calculated)
        self.assertIsNotNone(self.sync.last_sync)
    
    def test_get_atomic_time(self):
        """Test getting atomic time."""
        # Without sync, should return system time
        time_before = datetime.now(timezone.utc)
        atomic_time = self.sync.get_atomic_time()
        time_after = datetime.now(timezone.utc)
        
        self.assertIsNotNone(atomic_time)
        self.assertGreaterEqual(atomic_time, time_before)
        self.assertLessEqual(atomic_time, time_after)
    
    def test_is_synchronized(self):
        """Test synchronization status check."""
        # Initially not synchronized
        self.assertFalse(self.sync.is_synchronized())
        
        # After setting sync status
        self.sync.sync_status = True
        self.sync.last_sync = datetime.now(timezone.utc)
        self.assertTrue(self.sync.is_synchronized())
    
    def test_get_sync_info(self):
        """Test getting sync information."""
        info = self.sync.get_sync_info()
        
        self.assertIn('synchronized', info)
        self.assertIn('offset_seconds', info)
        self.assertIn('last_sync', info)
        self.assertIn('sync_attempts', info)


class TestLocationManager(unittest.TestCase):
    """Test location manager module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        import tempfile
        import json
        
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'locations.json')
        
        test_config = {
            "locations": [
                {
                    "id": "test",
                    "name": "TEST",
                    "city": "Test City",
                    "timezone": "UTC",
                    "ntp_server": "time.nist.gov",
                    "corner": "top_left"
                }
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.manager = LocationManager(config_path=self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_locations(self):
        """Test loading locations from config."""
        self.assertEqual(len(self.manager.locations), 1)
        self.assertEqual(self.manager.locations[0]['id'], 'test')
    
    def test_get_location(self):
        """Test getting location by ID."""
        location = self.manager.get_location('test')
        self.assertIsNotNone(location)
        self.assertEqual(location['id'], 'test')
        
        # Non-existent location
        location = self.manager.get_location('nonexistent')
        self.assertIsNone(location)
    
    def test_get_location_time(self):
        """Test getting time for location."""
        time_obj = self.manager.get_location_time('test')
        self.assertIsNotNone(time_obj)
        self.assertIsInstance(time_obj, datetime)
    
    def test_format_time_for_display(self):
        """Test time formatting."""
        test_time = datetime(2024, 1, 1, 12, 30, 45, tzinfo=timezone.utc)
        location = {'id': 'test', 'name': 'TEST', 'timezone': 'UTC'}
        
        formatted = self.manager.format_time_for_display(test_time, location)
        self.assertEqual(formatted, "12:30:45")
    
    def test_get_utc_offset(self):
        """Test UTC offset calculation."""
        location = {'id': 'test', 'name': 'TEST', 'timezone': 'UTC'}
        offset = self.manager.get_utc_offset(location)
        self.assertEqual(offset, "+00:00")
    
    def test_get_location_by_corner(self):
        """Test getting location by corner."""
        location = self.manager.get_location_by_corner('top_left')
        self.assertIsNotNone(location)
        self.assertEqual(location['corner'], 'top_left')


class TestClockRenderer(unittest.TestCase):
    """Test clock renderer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.renderer = ClockRenderer(width=80, height=24)
    
    def test_initialization(self):
        """Test renderer initialization."""
        self.assertEqual(self.renderer.width, 80)
        self.assertEqual(self.renderer.height, 24)
        self.assertEqual(self.renderer.center_x, 40)
        self.assertEqual(self.renderer.center_y, 12)
    
    def test_update_size(self):
        """Test size update."""
        self.renderer.update_size(100, 50)
        self.assertEqual(self.renderer.width, 100)
        self.assertEqual(self.renderer.height, 50)
        self.assertEqual(self.renderer.center_x, 50)
        self.assertEqual(self.renderer.center_y, 25)
    
    def test_render_clock_face(self):
        """Test clock face rendering."""
        # This test verifies the function doesn't crash
        # Actual rendering would require terminal output
        try:
            self.renderer.render_clock_face(12, 30, 45)
            # If we get here, rendering didn't crash
            success = True
        except Exception as e:
            success = False
        
        self.assertTrue(success)
    
    def test_render_corner_time(self):
        """Test corner time rendering."""
        time_info = {
            'name': 'TEST',
            'city': 'Test City',
            'time': '12:30:45',
            'utc_offset': '+00:00'
        }
        
        # Test rendering doesn't crash
        try:
            self.renderer.render_corner_time(time_info, 'top_left')
            success = True
        except Exception as e:
            success = False
        
        self.assertTrue(success)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_time_sync_and_location_manager(self):
        """Test integration between time sync and location manager."""
        sync = AtomicTimeSync()
        manager = LocationManager()
        
        # Should be able to get times for locations
        times = manager.get_all_location_times()
        self.assertIsInstance(times, dict)
    
    def test_location_manager_and_renderer(self):
        """Test integration between location manager and renderer."""
        manager = LocationManager()
        renderer = ClockRenderer(80, 24)
        
        # Get corner times
        corner_times = {}
        for location in manager.locations:
            corner = location.get('corner')
            if corner:
                time_info = manager.get_corner_time_info(corner)
                if time_info:
                    corner_times[corner] = time_info
        
        # Should have some corner times
        self.assertGreater(len(corner_times), 0)


if __name__ == '__main__':
    unittest.main()
