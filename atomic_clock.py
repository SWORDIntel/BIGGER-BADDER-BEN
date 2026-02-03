#!/usr/bin/env python3
"""
Atomic Clock Display Application

Main application for displaying atomic clock times from various locations
around the world using EKI/DCP technologies.
"""

import sys
import os
import time
import signal
import argparse
import select
import termios
import tty
from datetime import datetime, timezone
from typing import Optional, Dict
import shutil

# Add parent directory to path for DCP imports (if available)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from time_sync import AtomicTimeSync, TimeSyncError
from location_manager import LocationManager
from clock_renderer import ClockRenderer, get_terminal_size


class AtomicClockApp:
    """Main atomic clock application."""
    
    def __init__(self, config_path: Optional[str] = None, ntp_server: Optional[str] = None,
                 update_interval: float = 1.0, fullscreen: bool = False):
        """
        Initialize atomic clock application.
        
        Args:
            config_path: Path to locations.json config file
            ntp_server: Preferred NTP server
            update_interval: Update interval in seconds
            fullscreen: Enable fullscreen mode
        """
        self.config_path = config_path
        self.ntp_server = ntp_server
        self.update_interval = update_interval
        self.fullscreen = fullscreen
        self.running = False
        self.old_terminal_settings = None
        
        # Initialize components
        self.time_sync = AtomicTimeSync(preferred_server=ntp_server)
        self.location_manager = LocationManager(config_path=config_path)
        self.renderer = None
        
        # DCP integration (optional)
        self.dcp_integrated = False
        self.eki_integrated = False
        
        # Error handling
        self.error_count = 0
        self.max_errors = 10
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGWINCH'):
            signal.signal(signal.SIGWINCH, self._resize_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def _resize_handler(self, signum, frame):
        """Handle terminal resize."""
        try:
            width, height = get_terminal_size()
            if self.renderer:
                self.renderer.update_size(width, height)
        except Exception as e:
            print(f"Error handling resize: {e}", file=sys.stderr)
    
    def initialize_display(self):
        """Setup terminal and graphics."""
        try:
            # Get terminal size
            width, height = get_terminal_size()
            
            # Initialize renderer
            self.renderer = ClockRenderer(width, height)
            
            # Setup terminal for non-blocking input
            self.old_terminal_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            
            # Clear screen and hide cursor
            sys.stdout.write('\033[?25l')  # Hide cursor
            sys.stdout.write('\033[2J')     # Clear screen
            sys.stdout.flush()
            
            return True
            
        except Exception as e:
            print(f"Error initializing display: {e}", file=sys.stderr)
            return False
    
    def integrate_dcp(self):
        """Integrate with DCP Unified Control Plane."""
        try:
            # Try to import DCP modules
            from DCP.core.unified_control_plane import UnifiedControlPlane
            
            ucp = UnifiedControlPlane()
            ucp.register_module("atomic_clock", {
                "capabilities": ["time_display", "ntp_sync"],
                "update_interval": self.update_interval,
                "locations": len(self.location_manager.locations)
            })
            
            self.dcp_integrated = True
            return True
            
        except ImportError:
            # DCP not available, continue without integration
            return False
        except Exception as e:
            print(f"Warning: DCP integration failed: {e}", file=sys.stderr)
            return False
    
    def integrate_eki(self):
        """Integrate with EKI terminal enhancements."""
        try:
            # EKI integration is primarily through Kitty Graphics Protocol
            # which is handled by the renderer
            # Additional EKI features can be added here
            
            # Check if running in Kitty terminal
            if os.environ.get('KITTY_WINDOW_ID'):
                self.eki_integrated = True
                return True
            
            return False
            
        except Exception as e:
            print(f"Warning: EKI integration check failed: {e}", file=sys.stderr)
            return False
    
    def update_loop(self):
        """Main update loop."""
        self.running = True
        
        # Initial synchronization
        print("Synchronizing with atomic clocks...", end='', flush=True)
        if self.time_sync.sync_with_ntp():
            print(" ✓")
        else:
            print(" ✗ (using system time)")
        
        # Get initial times
        current_time = self.time_sync.get_atomic_time()
        corner_times = {}
        
        for location in self.location_manager.locations:
            corner = location.get('corner')
            if corner:
                time_info = self.location_manager.get_corner_time_info(corner)
                if time_info:
                    corner_times[corner] = time_info
        
        # Initial render
        if self.renderer:
            self.renderer.update_display(current_time, corner_times)
        
        # Main loop
        last_update = time.time()
        last_sync = time.time()
        
        while self.running:
            try:
                current_time_real = time.time()
                
                # Check for keyboard input (non-blocking)
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    self._handle_keypress(key)
                
                # Update display at specified interval
                if current_time_real - last_update >= self.update_interval:
                    # Get current atomic time
                    current_time = self.time_sync.get_atomic_time()
                    
                    # Update corner times
                    corner_times = {}
                    for location in self.location_manager.locations:
                        corner = location.get('corner')
                        if corner:
                            time_info = self.location_manager.get_corner_time_info(corner)
                            if time_info:
                                corner_times[corner] = time_info
                    
                    # Render update
                    if self.renderer:
                        self.renderer.update_display(current_time, corner_times)
                    
                    last_update = current_time_real
                    self.error_count = 0  # Reset error count on successful update
                
                # Re-sync with NTP every 5 minutes
                if current_time_real - last_sync >= 300:
                    if self.time_sync.sync_with_ntp():
                        last_sync = current_time_real
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                self.error_count += 1
                if self.error_count >= self.max_errors:
                    print(f"\nToo many errors ({self.error_count}), exiting...", file=sys.stderr)
                    self.running = False
                    break
                # Continue running despite errors
                time.sleep(1)
    
    def _handle_keypress(self, key: str):
        """
        Handle keyboard input.
        
        Args:
            key: Key character pressed
        """
        if key == 'q' or key == '\x1b':  # 'q' or ESC
            self.running = False
        elif key == 'r':  # Refresh
            self.time_sync.sync_with_ntp()
        elif key == 's':  # Show sync status
            self._show_sync_status()
        elif key == '+':  # Increase update interval
            self.update_interval = min(self.update_interval + 0.1, 5.0)
        elif key == '-':  # Decrease update interval
            self.update_interval = max(self.update_interval - 0.1, 0.1)
        elif key == 'f':  # Toggle fullscreen (placeholder)
            pass  # Fullscreen toggle would require terminal-specific handling
    
    def _show_sync_status(self):
        """Display synchronization status."""
        sync_info = self.time_sync.get_sync_info()
        
        # Display status in top-right corner temporarily
        width, height = get_terminal_size()
        status_y = 1
        status_x = width - 30
        
        sys.stdout.write(f'\033[{status_y};{status_x}H')
        sys.stdout.write('\033[47;30m')  # White background, black text
        status = "SYNC" if sync_info['synchronized'] else "NO SYNC"
        offset = f"{sync_info['offset_seconds']:.3f}s"
        sys.stdout.write(f"{status} {offset}".ljust(29))
        sys.stdout.write('\033[0m')
        sys.stdout.flush()
    
    def handle_resize(self):
        """Handle terminal resize event."""
        try:
            width, height = get_terminal_size()
            if self.renderer:
                self.renderer.update_size(width, height)
                # Trigger immediate update
                current_time = self.time_sync.get_atomic_time()
                corner_times = {}
                for location in self.location_manager.locations:
                    corner = location.get('corner')
                    if corner:
                        time_info = self.location_manager.get_corner_time_info(corner)
                        if time_info:
                            corner_times[corner] = time_info
                self.renderer.update_display(current_time, corner_times)
        except Exception as e:
            print(f"Error handling resize: {e}", file=sys.stderr)
    
    def cleanup(self):
        """Cleanup on exit."""
        try:
            # Set running to False
            self.running = False
            
            # Restore terminal settings
            if self.old_terminal_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_terminal_settings)
            
            # Show cursor
            sys.stdout.write('\033[?25h')
            
            # Clear screen
            sys.stdout.write('\033[2J')
            sys.stdout.write('\033[H')
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Error during cleanup: {e}", file=sys.stderr)
    
    def run(self):
        """Run the application."""
        try:
            # Initialize display
            if not self.initialize_display():
                print("Failed to initialize display", file=sys.stderr)
                return 1
            
            # Integrate with DCP (optional)
            self.integrate_dcp()
            
            # Integrate with EKI (optional)
            self.integrate_eki()
            
            # Run update loop
            self.update_loop()
            
            return 0
            
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Atomic Clock Display - Real-time atomic clock times from around the world'
    )
    parser.add_argument(
        '--locations',
        type=str,
        help='Path to locations.json config file'
    )
    parser.add_argument(
        '--ntp-server',
        type=str,
        help='Preferred NTP server (e.g., time.nist.gov)'
    )
    parser.add_argument(
        '--update-interval',
        type=float,
        default=1.0,
        help='Update interval in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='Enable fullscreen mode'
    )
    
    args = parser.parse_args()
    
    # Create and run application
    app = AtomicClockApp(
        config_path=args.locations,
        ntp_server=args.ntp_server,
        update_interval=args.update_interval,
        fullscreen=args.fullscreen
    )
    
    sys.exit(app.run())


if __name__ == '__main__':
    main()
