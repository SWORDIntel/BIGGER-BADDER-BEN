#!/usr/bin/env python3
"""
Time Synchronization Module for Atomic Clock Display

Synchronizes with atomic clocks via NTP and provides accurate time data.
"""

import time
import socket
import struct
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict
import ntplib
import pytz
from dateutil import tz


class TimeSyncError(Exception):
    """Exception raised for time synchronization errors."""
    pass


class AtomicTimeSync:
    """Synchronize with atomic clock servers via NTP."""
    
    # Primary NTP servers (atomic clock sources)
    NTP_SERVERS = [
        'time.nist.gov',      # NIST (USA)
        'ptbtime1.ptb.de',    # PTB (Germany)
        'time.npl.co.uk',     # NPL (UK)
        'ntp.nict.jp',        # NICT (Japan)
        'tick.usno.navy.mil', # USNO (USA)
        'time.google.com',    # Google (fallback)
        'pool.ntp.org',       # NTP Pool (fallback)
    ]
    
    def __init__(self, preferred_server: Optional[str] = None):
        """
        Initialize time synchronization.
        
        Args:
            preferred_server: Preferred NTP server to use first
        """
        self.preferred_server = preferred_server
        self.ntp_client = ntplib.NTPClient()
        self.offset = 0.0
        self.last_sync = None
        self.sync_status = False
        self.sync_attempts = 0
        
    def sync_with_ntp(self, server: Optional[str] = None, timeout: int = 5) -> bool:
        """
        Synchronize with NTP server.
        
        Args:
            server: NTP server hostname (uses preferred or first available if None)
            timeout: Request timeout in seconds
            
        Returns:
            True if synchronization successful, False otherwise
        """
        servers_to_try = []
        
        if server:
            servers_to_try.append(server)
        elif self.preferred_server:
            servers_to_try.append(self.preferred_server)
        
        # Add all servers as fallbacks
        servers_to_try.extend(self.NTP_SERVERS)
        
        for ntp_server in servers_to_try:
            try:
                self.sync_attempts += 1
                response = self.ntp_client.request(ntp_server, version=3, timeout=timeout)
                
                # Calculate offset from system time
                ntp_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
                system_time = datetime.now(timezone.utc)
                self.offset = (response.tx_time - time.time())
                
                self.last_sync = datetime.now(timezone.utc)
                self.sync_status = True
                
                return True
                
            except (ntplib.NTPException, socket.gaierror, socket.timeout, OSError) as e:
                continue
        
        # All servers failed
        self.sync_status = False
        return False
    
    def get_atomic_time(self, location: Optional[str] = None) -> datetime:
        """
        Get atomic clock time, optionally for a specific location.
        
        Args:
            location: Location identifier (for future location-specific queries)
            
        Returns:
            Current atomic clock time as datetime object
        """
        if not self.sync_status:
            # Try to sync if not synchronized
            self.sync_with_ntp()
        
        if self.sync_status:
            # Return synchronized time
            return datetime.now(timezone.utc) + timedelta(seconds=self.offset)
        else:
            # Fallback to system time
            return datetime.now(timezone.utc)
    
    def calculate_offset(self) -> float:
        """
        Calculate offset from system time.
        
        Returns:
            Offset in seconds (positive means system is slow)
        """
        if not self.sync_status:
            self.sync_with_ntp()
        
        return self.offset
    
    def is_synchronized(self) -> bool:
        """
        Check if currently synchronized with atomic clock.
        
        Returns:
            True if synchronized, False otherwise
        """
        # Check if sync is stale (older than 1 hour)
        if self.last_sync:
            time_since_sync = (datetime.now(timezone.utc) - self.last_sync).total_seconds()
            if time_since_sync > 3600:  # 1 hour
                self.sync_status = False
        
        return self.sync_status
    
    def get_sync_info(self) -> Dict:
        """
        Get synchronization status information.
        
        Returns:
            Dictionary with sync status, offset, last sync time, etc.
        """
        return {
            'synchronized': self.sync_status,
            'offset_seconds': self.offset,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_attempts': self.sync_attempts,
        }
    
    def get_time_for_timezone(self, timezone_name: str) -> datetime:
        """
        Get current time in specified timezone.
        
        Args:
            timezone_name: Timezone name (e.g., 'America/Denver', 'Europe/Berlin')
            
        Returns:
            Current time in specified timezone
        """
        utc_time = self.get_atomic_time()
        tz_obj = pytz.timezone(timezone_name)
        return utc_time.astimezone(tz_obj)


# Convenience function for quick synchronization
def sync_with_ntp(server: Optional[str] = None) -> AtomicTimeSync:
    """
    Quick function to create and sync AtomicTimeSync instance.
    
    Args:
        server: Optional NTP server hostname
        
    Returns:
        Synchronized AtomicTimeSync instance
    """
    sync = AtomicTimeSync(preferred_server=server)
    sync.sync_with_ntp()
    return sync


if __name__ == '__main__':
    # Test time synchronization
    print("Testing atomic clock synchronization...")
    sync = AtomicTimeSync()
    
    if sync.sync_with_ntp():
        print(f"✓ Synchronized successfully")
        print(f"  Offset: {sync.offset:.3f} seconds")
        print(f"  UTC Time: {sync.get_atomic_time()}")
        print(f"  Sync Info: {sync.get_sync_info()}")
    else:
        print("✗ Synchronization failed, using system time")
        print(f"  System UTC Time: {datetime.now(timezone.utc)}")
