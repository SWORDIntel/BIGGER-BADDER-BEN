#!/usr/bin/env python3
"""
Unit tests for DriftMonitor
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from drift_monitor import DriftMonitor, console_alert_callback


class TestDriftMonitor(unittest.TestCase):
    """Test cases for DriftMonitor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        self.drift_monitor = DriftMonitor(self.temp_db.name, alert_threshold=0.1)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.drift_monitor.stop_monitoring()
        os.unlink(self.temp_db.name)
    
    def test_init_database(self):
        """Test database initialization."""
        # Check that database file exists and has tables
        self.assertTrue(os.path.exists(self.temp_db.name))
        
        # Test recording a drift measurement
        self.drift_monitor.record_drift(0.05, sync_success=True)
        
        # Query database to verify record was inserted
        import sqlite3
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM drift_measurements')
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)
    
    def test_record_drift(self):
        """Test recording drift measurements."""
        offset = 0.123
        ntp_server = "time.nist.gov"
        system_time = datetime(2023, 1, 1, 12, 0, 0)
        ntp_time = datetime(2023, 1, 1, 12, 0, 0, 123000)
        
        self.drift_monitor.record_drift(
            offset_seconds=offset,
            ntp_server=ntp_server,
            sync_success=True,
            system_time=system_time,
            ntp_time=ntp_time
        )
        
        # Verify record was inserted
        import sqlite3
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute('''
                SELECT offset_seconds, ntp_server, sync_success, system_time, ntp_time
                FROM drift_measurements
            ''')
            result = cursor.fetchone()
            
            self.assertEqual(result[0], offset)
            self.assertEqual(result[1], ntp_server)
            self.assertEqual(bool(result[2]), True)
            # Convert string to datetime for comparison - handle both formats
            stored_system_time = result[3]
            if 'T' in stored_system_time:
                # ISO format with T
                self.assertEqual(stored_system_time, system_time.isoformat())
            else:
                # Space format
                self.assertEqual(stored_system_time, system_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            stored_ntp_time = result[4]
            if 'T' in stored_ntp_time:
                # ISO format with T
                self.assertEqual(stored_ntp_time, ntp_time.isoformat())
            else:
                # Space format with microseconds
                self.assertEqual(stored_ntp_time, ntp_time.strftime('%Y-%m-%d %H:%M:%S.%f'))
    
    def test_alert_threshold(self):
        """Test drift alerting."""
        # Record drift within threshold (should not alert)
        self.drift_monitor.record_drift(0.05, sync_success=True)
        
        alerts = self.drift_monitor.get_recent_alerts(1)
        self.assertEqual(len(alerts), 0)
        
        # Record drift exceeding threshold (should alert)
        self.drift_monitor.record_drift(0.15, sync_success=True)
        
        alerts = self.drift_monitor.get_recent_alerts(1)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['type'], 'HIGH_DRIFT')
        self.assertEqual(alerts[0]['drift'], 0.15)
        self.assertEqual(alerts[0]['threshold'], 0.1)
        
        # Test negative drift
        self.drift_monitor.record_drift(-0.15, sync_success=True)
        
        alerts = self.drift_monitor.get_recent_alerts(1)
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[0]['type'], 'LOW_DRIFT')
        self.assertEqual(alerts[0]['drift'], -0.15)
    
    def test_alert_callbacks(self):
        """Test alert callback functionality."""
        callback_called = []
        
        def test_callback(alert_data):
            callback_called.append(alert_data)
        
        self.drift_monitor.add_alert_callback(test_callback)
        
        # Record drift exceeding threshold
        self.drift_monitor.record_drift(0.15, sync_success=True)
        
        # Check callback was called
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0]['type'], 'HIGH_DRIFT')
        self.assertEqual(callback_called[0]['drift'], 0.15)
    
    def test_get_drift_statistics(self):
        """Test drift statistics calculation."""
        # Record some test data
        test_drifts = [0.01, 0.02, 0.03, 0.04, 0.05]
        for drift in test_drifts:
            self.drift_monitor.record_drift(drift, sync_success=True)
        
        # Record a failed sync
        self.drift_monitor.record_drift(0.0, sync_success=False)
        
        stats = self.drift_monitor.get_drift_statistics(1)
        
        self.assertEqual(stats['period_hours'], 1)
        self.assertEqual(stats['measurement_count'], 6)  # 5 successful + 1 failed
        self.assertEqual(stats['success_rate'], 5/6)  # 5 out of 6 successful
        self.assertEqual(stats['mean_drift'], sum(test_drifts) / len(test_drifts))
        self.assertEqual(stats['max_drift'], max(test_drifts))
        self.assertEqual(stats['min_drift'], min(test_drifts))
        self.assertGreater(stats['std_deviation'], 0)
    
    def test_get_drift_statistics_no_data(self):
        """Test statistics when no data available."""
        stats = self.drift_monitor.get_drift_statistics(1)
        
        self.assertEqual(stats['period_hours'], 1)
        self.assertEqual(stats['measurement_count'], 0)
        self.assertEqual(stats['success_rate'], 0.0)
        self.assertEqual(stats['mean_drift'], 0.0)
        self.assertEqual(stats['max_drift'], 0.0)
        self.assertEqual(stats['min_drift'], 0.0)
        self.assertEqual(stats['std_deviation'], 0.0)
    
    def test_get_recent_alerts(self):
        """Test getting recent alerts."""
        # Record some alerts
        self.drift_monitor.record_drift(0.15, sync_success=True)  # High drift
        self.drift_monitor.record_drift(-0.15, sync_success=True)  # Low drift
        
        alerts = self.drift_monitor.get_recent_alerts(1)
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[0]['type'], 'LOW_DRIFT')  # Most recent first
        self.assertEqual(alerts[1]['type'], 'HIGH_DRIFT')
        
        # Test filtering by acknowledgment status
        unacknowledged = self.drift_monitor.get_recent_alerts(1, acknowledged=False)
        self.assertEqual(len(unacknowledged), 2)
        
        # Acknowledge one alert
        import sqlite3
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute('SELECT id FROM drift_alerts ORDER BY timestamp DESC LIMIT 1')
            alert_id = cursor.fetchone()[0]
        
        self.drift_monitor.acknowledge_alert(alert_id)
        
        acknowledged = self.drift_monitor.get_recent_alerts(1, acknowledged=True)
        self.assertEqual(len(acknowledged), 1)
        
        unacknowledged = self.drift_monitor.get_recent_alerts(1, acknowledged=False)
        self.assertEqual(len(unacknowledged), 1)
    
    def test_acknowledge_alert(self):
        """Test alert acknowledgment."""
        # Record an alert
        self.drift_monitor.record_drift(0.15, sync_success=True)
        
        # Get alert ID
        import sqlite3
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute('SELECT id FROM drift_alerts ORDER BY timestamp DESC LIMIT 1')
            alert_id = cursor.fetchone()[0]
        
        # Acknowledge alert
        result = self.drift_monitor.acknowledge_alert(alert_id)
        self.assertTrue(result)
        
        # Verify acknowledgment
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.execute('SELECT acknowledged FROM drift_alerts WHERE id = ?', (alert_id,))
            acknowledged = cursor.fetchone()[0]
            self.assertEqual(acknowledged, 1)
        
        # Test acknowledging non-existent alert
        result = self.drift_monitor.acknowledge_alert(99999)
        self.assertFalse(result)
    
    def test_export_data(self):
        """Test data export functionality."""
        # Record some test data
        self.drift_monitor.record_drift(0.05, sync_success=True)
        self.drift_monitor.record_drift(0.15, sync_success=True)  # This should create an alert
        
        # Export data
        export_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        export_file.close()
        
        try:
            self.drift_monitor.export_data(export_file.name, 1)
            
            # Verify export file
            self.assertTrue(os.path.exists(export_file.name))
            
            with open(export_file.name, 'r') as f:
                data = json.load(f)
            
            self.assertIn('export_timestamp', data)
            self.assertIn('period_hours', data)
            self.assertIn('measurements', data)
            self.assertIn('alerts', data)
            self.assertIn('statistics', data)
            
            self.assertEqual(data['period_hours'], 1)
            self.assertEqual(len(data['measurements']), 2)
            self.assertEqual(len(data['alerts']), 1)
            
        finally:
            os.unlink(export_file.name)
    
    @patch('threading.Thread')
    def test_start_monitoring(self, mock_thread):
        """Test starting continuous monitoring."""
        mock_time_sync = MagicMock()
        
        self.drift_monitor.start_monitoring(mock_time_sync, interval=1)
        
        self.assertTrue(self.drift_monitor.running)
        mock_thread.assert_called_once()
    
    def test_stop_monitoring(self):
        """Test stopping continuous monitoring."""
        mock_time_sync = MagicMock()
        
        self.drift_monitor.start_monitoring(mock_time_sync, interval=1)
        self.assertTrue(self.drift_monitor.running)
        
        self.drift_monitor.stop_monitoring()
        self.assertFalse(self.drift_monitor.running)


class TestConsoleAlertCallback(unittest.TestCase):
    """Test cases for console alert callback."""
    
    @patch('builtins.print')
    def test_console_alert_callback(self, mock_print):
        """Test console alert callback."""
        alert_data = {
            'type': 'HIGH_DRIFT',
            'drift': 0.15,
            'threshold': 0.1,
            'timestamp': datetime(2023, 1, 1, 12, 0, 0),
            'message': 'Time drift exceeds threshold'
        }
        
        console_alert_callback(alert_data)
        
        # Verify print was called with alert information
        calls = mock_print.call_args_list
        self.assertTrue(any('DRIFT ALERT' in str(call) for call in calls))
        self.assertTrue(any('HIGH_DRIFT' in str(call) for call in calls))


if __name__ == '__main__':
    unittest.main()
