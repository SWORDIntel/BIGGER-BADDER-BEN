#!/usr/bin/env python3
"""
High-Precision Drift Monitoring for Atomic Clock Display

Monitors and logs time drift with SQLite persistence and alerting.
"""

import sqlite3
import time
import threading
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import os


class DriftMonitor:
    """Monitor and log time drift with persistence and alerting."""
    
    def __init__(self, db_path: str = None, alert_threshold: float = 0.1):
        """
        Initialize drift monitor.
        
        Args:
            db_path: Path to SQLite database file
            alert_threshold: Drift threshold in seconds for alerts
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'drift_data.db')
        
        self.db_path = db_path
        self.alert_threshold = alert_threshold
        self.running = False
        self.thread = None
        self.alert_callbacks = []
        
        # Initialize database
        self._init_database()
        
        # Load recent drift data for analysis
        self.recent_drifts = self._load_recent_drifts(100)  # Last 100 measurements
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS drift_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    offset_seconds REAL NOT NULL,
                    ntp_server TEXT,
                    sync_success BOOLEAN NOT NULL,
                    system_time DATETIME NOT NULL,
                    ntp_time DATETIME
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS drift_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    alert_type TEXT NOT NULL,
                    drift_value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    message TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_drift_timestamp 
                ON drift_measurements(timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_alert_timestamp 
                ON drift_alerts(timestamp)
            ''')
            
            conn.commit()
    
    def _load_recent_drifts(self, limit: int = 100) -> List[float]:
        """Load recent drift measurements from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT offset_seconds FROM drift_measurements 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def add_alert_callback(self, callback):
        """Add callback function for drift alerts."""
        self.alert_callbacks.append(callback)
    
    def record_drift(self, offset_seconds: float, ntp_server: str = None, 
                    sync_success: bool = True, system_time: datetime = None, 
                    ntp_time: datetime = None):
        """
        Record a drift measurement.
        
        Args:
            offset_seconds: Time offset in seconds
            ntp_server: NTP server used
            sync_success: Whether sync was successful
            system_time: System time at measurement
            ntp_time: NTP time at measurement
        """
        if system_time is None:
            system_time = datetime.now()
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO drift_measurements 
                (timestamp, offset_seconds, ntp_server, sync_success, system_time, ntp_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (system_time, offset_seconds, ntp_server, sync_success, system_time, ntp_time))
            conn.commit()
        
        # Update recent drifts
        self.recent_drifts.insert(0, offset_seconds)
        if len(self.recent_drifts) > 100:
            self.recent_drifts.pop()
        
        # Check for alerts
        self._check_drift_alerts(offset_seconds, system_time)
    
    def _check_drift_alerts(self, offset_seconds: float, timestamp: datetime):
        """Check if drift exceeds alert threshold."""
        abs_drift = abs(offset_seconds)
        
        if abs_drift >= self.alert_threshold:
            alert_type = "HIGH_DRIFT" if offset_seconds > 0 else "LOW_DRIFT"
            message = f"Time drift of {offset_seconds:.3f}s exceeds threshold of {self.alert_threshold}s"
            
            # Store alert
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO drift_alerts 
                    (timestamp, alert_type, drift_value, threshold, message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, alert_type, offset_seconds, self.alert_threshold, message))
                conn.commit()
            
            # Trigger alert callbacks
            alert_data = {
                'type': alert_type,
                'drift': offset_seconds,
                'threshold': self.alert_threshold,
                'timestamp': timestamp,
                'message': message
            }
            
            for callback in self.alert_callbacks:
                try:
                    callback(alert_data)
                except Exception as e:
                    print(f"Error in alert callback: {e}")
    
    def get_drift_statistics(self, hours: int = 24) -> Dict:
        """
        Get drift statistics for the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with drift statistics
        """
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT offset_seconds, sync_success 
                FROM drift_measurements 
                WHERE timestamp >= ?
                ORDER BY timestamp
            ''', (since,))
            
            measurements = cursor.fetchall()
        
        if not measurements:
            return {
                'period_hours': hours,
                'measurement_count': 0,
                'success_rate': 0.0,
                'mean_drift': 0.0,
                'max_drift': 0.0,
                'min_drift': 0.0,
                'std_deviation': 0.0
            }
        
        offsets = [m[0] for m in measurements if m[1]]  # Only successful syncs
        successful_syncs = sum(1 for m in measurements if m[1])
        
        if offsets:
            stats = {
                'period_hours': hours,
                'measurement_count': len(measurements),
                'success_rate': successful_syncs / len(measurements),
                'mean_drift': statistics.mean(offsets),
                'max_drift': max(offsets),
                'min_drift': min(offsets),
                'std_deviation': statistics.stdev(offsets) if len(offsets) > 1 else 0.0
            }
        else:
            stats = {
                'period_hours': hours,
                'measurement_count': len(measurements),
                'success_rate': 0.0,
                'mean_drift': 0.0,
                'max_drift': 0.0,
                'min_drift': 0.0,
                'std_deviation': 0.0
            }
        
        return stats
    
    def get_recent_alerts(self, hours: int = 24, acknowledged: bool = None) -> List[Dict]:
        """
        Get recent drift alerts.
        
        Args:
            hours: Number of hours to look back
            acknowledged: Filter by acknowledgment status
            
        Returns:
            List of alert dictionaries
        """
        since = datetime.now() - timedelta(hours=hours)
        
        query = '''
            SELECT timestamp, alert_type, drift_value, threshold, message, acknowledged
            FROM drift_alerts 
            WHERE timestamp >= ?
        '''
        params = [since]
        
        if acknowledged is not None:
            query += ' AND acknowledged = ?'
            params.append(acknowledged)
        
        query += ' ORDER BY timestamp DESC'
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'timestamp': row[0],
                    'type': row[1],
                    'drift': row[2],
                    'threshold': row[3],
                    'message': row[4],
                    'acknowledged': bool(row[5])
                })
            
            return alerts
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Acknowledge a drift alert.
        
        Args:
            alert_id: ID of alert to acknowledge
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'UPDATE drift_alerts SET acknowledged = TRUE WHERE id = ?',
                    (alert_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def export_data(self, output_path: str, hours: int = 168):  # Default 1 week
        """
        Export drift data to JSON file.
        
        Args:
            output_path: Path to output JSON file
            hours: Number of hours to export
        """
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            # Export measurements
            cursor = conn.execute('''
                SELECT timestamp, offset_seconds, ntp_server, sync_success, system_time, ntp_time
                FROM drift_measurements 
                WHERE timestamp >= ?
                ORDER BY timestamp
            ''', (since,))
            
            measurements = []
            for row in cursor.fetchall():
                measurements.append({
                    'timestamp': row[0],
                    'offset_seconds': row[1],
                    'ntp_server': row[2],
                    'sync_success': bool(row[3]),
                    'system_time': row[4],
                    'ntp_time': row[5]
                })
            
            # Export alerts
            cursor = conn.execute('''
                SELECT timestamp, alert_type, drift_value, threshold, message, acknowledged
                FROM drift_alerts 
                WHERE timestamp >= ?
                ORDER BY timestamp
            ''', (since,))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'timestamp': row[0],
                    'alert_type': row[1],
                    'drift_value': row[2],
                    'threshold': row[3],
                    'message': row[4],
                    'acknowledged': bool(row[5])
                })
        
        # Write to file
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'measurements': measurements,
            'alerts': alerts,
            'statistics': self.get_drift_statistics(hours)
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def start_monitoring(self, time_sync, interval: int = 300):  # Default 5 minutes
        """
        Start continuous monitoring in background thread.
        
        Args:
            time_sync: AtomicTimeSync instance to monitor
            interval: Monitoring interval in seconds
        """
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._monitoring_loop,
            args=(time_sync, interval),
            daemon=True
        )
        self.thread.start()
    
    def _monitoring_loop(self, time_sync, interval: int):
        """Background monitoring loop."""
        while self.running:
            try:
                # Force a sync to get current offset
                if time_sync.sync_with_ntp():
                    self.record_drift(
                        offset_seconds=time_sync.offset,
                        ntp_server=getattr(time_sync, 'current_server', None),
                        sync_success=True
                    )
                else:
                    # Record failed sync
                    self.record_drift(
                        offset_seconds=0.0,
                        sync_success=False
                    )
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)


# Default alert callback
def console_alert_callback(alert_data: Dict):
    """Default alert callback that prints to console."""
    print(f"\n🚨 DRIFT ALERT: {alert_data['message']}")
    print(f"   Type: {alert_data['type']}")
    print(f"   Drift: {alert_data['drift']:.3f}s")
    print(f"   Threshold: {alert_data['threshold']:.3f}s")
    print(f"   Time: {alert_data['timestamp']}")


if __name__ == '__main__':
    # Test drift monitor
    monitor = DriftMonitor()
    monitor.add_alert_callback(console_alert_callback)
    
    print("Testing drift monitor...")
    
    # Simulate some drift measurements
    import random
    
    for i in range(10):
        drift = random.uniform(-0.2, 0.2)
        monitor.record_drift(drift, sync_success=True)
        print(f"Recorded drift: {drift:.3f}s")
        time.sleep(0.1)
    
    # Get statistics
    stats = monitor.get_drift_statistics(1)
    print(f"\nStatistics: {stats}")
    
    # Get alerts
    alerts = monitor.get_recent_alerts(1)
    print(f"Alerts: {len(alerts)}")
    
    # Export data
    monitor.export_data('drift_export.json', 1)
    print("Data exported to drift_export.json")
