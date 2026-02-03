#!/usr/bin/env python3
"""
Unit tests for AtomicTimeSync
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone, timedelta
import ntplib

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from time_sync import AtomicTimeSync, TimeSyncError


class TestAtomicTimeSync(unittest.TestCase):
    """Test cases for AtomicTimeSync."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.time_sync = AtomicTimeSync()
    
    def test_init(self):
        """Test initialization."""
        self.assertIsNone(self.time_sync.preferred_server)
        self.assertEqual(self.time_sync.offset, 0.0)
        self.assertIsNone(self.time_sync.last_sync)
        self.assertFalse(self.time_sync.sync_status)
        self.assertEqual(self.time_sync.sync_attempts, 0)
    
    def test_init_with_preferred_server(self):
        """Test initialization with preferred server."""
        server = "time.nist.gov"
        time_sync = AtomicTimeSync(preferred_server=server)
        self.assertEqual(time_sync.preferred_server, server)
    
    @patch('time_sync.ntplib.NTPClient')
    def test_sync_with_ntp_success(self, mock_client_class):
        """Test successful NTP synchronization."""
        # Mock NTP response
        mock_response = MagicMock()
        mock_response.tx_time = 1672574400.0  # 2023-01-01 00:00:00 UTC
        
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        time_sync = AtomicTimeSync()
        result = time_sync.sync_with_ntp()
        
        self.assertTrue(result)
        self.assertTrue(time_sync.sync_status)
        self.assertIsNotNone(time_sync.last_sync)
        self.assertGreater(time_sync.sync_attempts, 0)
    
    @patch('time_sync.ntplib.NTPClient')
    def test_sync_with_ntp_failure(self, mock_client_class):
        """Test NTP synchronization failure."""
        mock_client = MagicMock()
        mock_client.request.side_effect = ntplib.NTPException("Network error")
        mock_client_class.return_value = mock_client
        
        time_sync = AtomicTimeSync()
        result = time_sync.sync_with_ntp()
        
        self.assertFalse(result)
        self.assertFalse(time_sync.sync_status)
    
    @patch('time_sync.ntplib.NTPClient')
    def test_sync_with_specific_server(self, mock_client_class):
        """Test synchronization with specific server."""
        mock_response = MagicMock()
        mock_response.tx_time = 1672574400.0
        
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        time_sync = AtomicTimeSync()
        server = "time.nist.gov"
        result = time_sync.sync_with_ntp(server)
        
        self.assertTrue(result)
        mock_client.request.assert_called_with(server, version=3, timeout=5)
    
    @patch('time_sync.ntplib.NTPClient')
    def test_sync_with_preferred_server_first(self, mock_client_class):
        """Test that preferred server is tried first."""
        mock_response = MagicMock()
        mock_response.tx_time = 1672574400.0
        
        mock_client = MagicMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        preferred_server = "preferred.time.gov"
        time_sync = AtomicTimeSync(preferred_server=preferred_server)
        time_sync.sync_with_ntp()
        
        # Check that preferred server was tried first
        calls = mock_client.request.call_args_list
        self.assertEqual(calls[0][0][0], preferred_server)
    
    @patch('time_sync.datetime')
    def test_get_atomic_time_synced(self, mock_datetime):
        """Test getting atomic time when synchronized."""
        # Setup synchronized state
        self.time_sync.sync_status = True
        self.time_sync.offset = 0.123  # 123ms offset
        
        # Mock current time
        mock_now = Mock()
        mock_now.return_value = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now = mock_now
        
        result = self.time_sync.get_atomic_time()
        
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.tzinfo, timezone.utc)
        # Should be system time + offset
        expected = datetime(2023, 1, 1, 12, 0, 0, 123000, tzinfo=timezone.utc)
        self.assertEqual(result, expected)
    
    @patch('time_sync.datetime')
    @patch.object(AtomicTimeSync, 'sync_with_ntp')
    def test_get_atomic_time_not_synced(self, mock_sync, mock_datetime):
        """Test getting atomic time when not synchronized."""
        # Setup unsynchronized state
        self.time_sync.sync_status = False
        mock_sync.return_value = False
        
        # Mock current time
        mock_now = Mock()
        mock_now.return_value = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now = mock_now
        
        result = self.time_sync.get_atomic_time()
        
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.tzinfo, timezone.utc)
        # Should be system time (no offset)
        expected = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(result, expected)
        
        # Should have tried to sync
        mock_sync.assert_called_once()
    
    def test_calculate_offset(self):
        """Test offset calculation."""
        # Mock the sync status to avoid actual NTP call
        with patch.object(self.time_sync, 'sync_status', True):
            self.time_sync.offset = 0.123
            result = self.time_sync.calculate_offset()
            self.assertEqual(result, 0.123)
    
    @patch.object(AtomicTimeSync, 'sync_with_ntp')
    def test_calculate_offset_not_synced(self, mock_sync):
        """Test offset calculation when not synchronized."""
        self.time_sync.sync_status = False
        mock_sync.return_value = True
        self.time_sync.offset = 0.456
        
        result = self.time_sync.calculate_offset()
        
        self.assertEqual(result, 0.456)
        mock_sync.assert_called_once()
    
    def test_is_synchronized_true(self):
        """Test synchronization status when synced."""
        self.time_sync.sync_status = True
        self.time_sync.last_sync = datetime.now(timezone.utc)
        
        result = self.time_sync.is_synchronized()
        self.assertTrue(result)
    
    @patch('time_sync.datetime')
    def test_is_synchronized_stale(self, mock_datetime):
        """Test synchronization status when sync is stale."""
        # Setup stale sync (older than 1 hour)
        now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        stale_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)  # 2 hours ago
        
        mock_datetime.now.return_value = now
        
        self.time_sync.sync_status = True
        self.time_sync.last_sync = stale_time
        
        result = self.time_sync.is_synchronized()
        self.assertFalse(result)
        self.assertFalse(self.time_sync.sync_status)  # Should be updated to False
    
    def test_get_sync_info(self):
        """Test getting synchronization information."""
        self.time_sync.sync_status = True
        self.time_sync.offset = 0.123
        self.time_sync.last_sync = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        self.time_sync.sync_attempts = 5
        
        info = self.time_sync.get_sync_info()
        
        expected = {
            'synchronized': True,
            'offset_seconds': 0.123,
            'last_sync': '2023-01-01T12:00:00+00:00',
            'sync_attempts': 5
        }
        
        self.assertEqual(info, expected)
    
    def test_get_sync_info_no_sync(self):
        """Test getting sync info when never synced."""
        info = self.time_sync.get_sync_info()
        
        expected = {
            'synchronized': False,
            'offset_seconds': 0.0,
            'last_sync': None,
            'sync_attempts': 0
        }
        
        self.assertEqual(info, expected)
    
    def test_get_time_for_timezone(self):
        """Test getting time for specific timezone."""
        # Setup synchronized state
        self.time_sync.sync_status = True
        self.time_sync.offset = 0.0
        
        # Test with a real timezone - no mocking needed for basic functionality
        result = self.time_sync.get_time_for_timezone('America/Denver')
        
        self.assertIsInstance(result, datetime)
        self.assertIsNotNone(result.tzinfo)


class TestTimeSyncError(unittest.TestCase):
    """Test cases for TimeSyncError."""
    
    def test_time_sync_error(self):
        """Test TimeSyncError exception."""
        error = TimeSyncError("Test error")
        self.assertEqual(str(error), "Test error")


if __name__ == '__main__':
    unittest.main()
