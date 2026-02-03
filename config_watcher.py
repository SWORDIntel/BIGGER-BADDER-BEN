#!/usr/bin/env python3
"""
Configuration Watcher for Atomic Clock Display

Watches for file changes and triggers live reloading of configuration.
"""

import os
import time
import threading
from typing import Callable, Optional
from pathlib import Path


class ConfigWatcher:
    """Watch configuration files for changes and trigger callbacks."""
    
    def __init__(self, config_path: str, callback: Callable[[], None], poll_interval: float = 1.0):
        """
        Initialize configuration watcher.
        
        Args:
            config_path: Path to configuration file to watch
            callback: Function to call when configuration changes
            poll_interval: Polling interval in seconds
        """
        self.config_path = Path(config_path)
        self.callback = callback
        self.poll_interval = poll_interval
        self.running = False
        self.thread = None
        self.last_mtime = None
        
        # Get initial modification time
        self._update_mtime()
    
    def _update_mtime(self):
        """Update the last modification time."""
        try:
            if self.config_path.exists():
                self.last_mtime = self.config_path.stat().st_mtime
            else:
                self.last_mtime = None
        except OSError:
            self.last_mtime = None
    
    def _watch_loop(self):
        """Main watching loop."""
        while self.running:
            try:
                if self.config_path.exists():
                    current_mtime = self.config_path.stat().st_mtime
                    
                    # Check if file was modified
                    if self.last_mtime is not None and current_mtime > self.last_mtime:
                        # Wait a brief moment to ensure file write is complete
                        time.sleep(0.1)
                        
                        # Verify file is still newer (avoid false triggers)
                        new_mtime = self.config_path.stat().st_mtime
                        if new_mtime > self.last_mtime:
                            self.last_mtime = new_mtime
                            try:
                                self.callback()
                            except Exception as e:
                                print(f"Error in config reload callback: {e}", file=sys.stderr)
                    else:
                        self.last_mtime = current_mtime
                else:
                    # File doesn't exist, reset mtime
                    self.last_mtime = None
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"Error watching config file: {e}", file=sys.stderr)
                time.sleep(self.poll_interval)
    
    def start(self):
        """Start watching for configuration changes."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop watching for configuration changes."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def is_running(self) -> bool:
        """Check if watcher is currently running."""
        return self.running


class MultiConfigWatcher:
    """Watch multiple configuration files simultaneously."""
    
    def __init__(self, poll_interval: float = 1.0):
        """
        Initialize multi-configuration watcher.
        
        Args:
            poll_interval: Polling interval in seconds
        """
        self.poll_interval = poll_interval
        self.watchers = []
        self.running = False
        self.thread = None
    
    def add_config(self, config_path: str, callback: Callable[[], None]):
        """
        Add a configuration file to watch.
        
        Args:
            config_path: Path to configuration file
            callback: Function to call when configuration changes
        """
        watcher = ConfigWatcher(config_path, callback, self.poll_interval)
        self.watchers.append(watcher)
        
        # Start immediately if already running
        if self.running:
            watcher.start()
    
    def start(self):
        """Start watching all configuration files."""
        if self.running:
            return
        
        self.running = True
        for watcher in self.watchers:
            watcher.start()
    
    def stop(self):
        """Stop watching all configuration files."""
        self.running = False
        for watcher in self.watchers:
            watcher.stop()
    
    def is_running(self) -> bool:
        """Check if any watchers are currently running."""
        return self.running


if __name__ == '__main__':
    # Test configuration watcher
    import sys
    
    def test_callback():
        print("Configuration file changed!")
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        watcher = ConfigWatcher(config_file, test_callback)
        watcher.start()
        
        print(f"Watching {config_file} for changes...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping watcher...")
            watcher.stop()
    else:
        print("Usage: python config_watcher.py <config_file>")
