#!/usr/bin/env python3
"""
Curses-based TUI Renderer for Atomic Clock Display

Provides a terminal-based interface using the curses library.
"""

import curses
import curses.ascii
from datetime import datetime
from typing import Dict, Tuple, Optional
from renderer_interface import ClockRenderer, register_renderer


@register_renderer("curses")
class CursesRenderer(ClockRenderer):
    """Curses-based terminal renderer."""
    
    def __init__(self):
        self.stdscr = None
        self.width = 0
        self.height = 0
        self.showing_help = False
        self.color_pairs = {}
        self.initialized = False
    
    def initialize(self, width: int, height: int) -> bool:
        """Initialize curses display."""
        try:
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            curses.curs_set(0)  # Hide cursor
            
            # Initialize colors
            curses.start_color()
            curses.use_default_colors()
            
            # Define color pairs
            self.color_pairs = {
                'default': curses.color_pair(0),
                'clock': curses.color_pair(1),
                'corner': curses.color_pair(2),
                'help': curses.color_pair(3),
                'status': curses.color_pair(4),
            }
            
            # Initialize color pairs (if terminal supports colors)
            if curses.has_colors():
                curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Clock text
                curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Corner labels
                curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)   # Help overlay
                curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)     # Status
            
            self.width = width
            self.height = height
            self.initialized = True
            
            return True
            
        except Exception as e:
            self.cleanup()
            return False
    
    def update_display(self, current_time: datetime, corner_times: Dict[str, Dict]) -> None:
        """Update the curses display."""
        if not self.stdscr or not self.initialized:
            return
        
        self.stdscr.clear()
        
        # Draw main clock in center
        self._draw_main_clock(current_time)
        
        # Draw corner clocks
        self._draw_corner_clocks(corner_times)
        
        # Draw status bar
        self._draw_status_bar(current_time)
        
        # Show help overlay if active
        if self.showing_help:
            self._draw_help_overlay()
        
        self.stdscr.refresh()
    
    def _draw_main_clock(self, current_time: datetime) -> None:
        """Draw the main UTC clock in the center."""
        time_str = current_time.strftime("%H:%M:%S")
        date_str = current_time.strftime("%Y-%m-%d")
        
        # Calculate center position
        clock_x = (self.width - len(time_str)) // 2
        clock_y = self.height // 2
        
        # Draw time
        self.stdscr.addstr(clock_y, clock_x, time_str, self.color_pairs['clock'] | curses.A_BOLD)
        
        # Draw date below time
        date_x = (self.width - len(date_str)) // 2
        self.stdscr.addstr(clock_y + 1, date_x, date_str, self.color_pairs['clock'])
    
    def _draw_corner_clocks(self, corner_times: Dict[str, Dict]) -> None:
        """Draw clocks in corners."""
        corner_positions = {
            'top_left': (2, 2),
            'top_right': (2, self.width - 20),
            'bottom_left': (self.height - 3, 2),
            'bottom_right': (self.height - 3, self.width - 20),
        }
        
        for corner, info in corner_times.items():
            if corner in corner_positions:
                y, x = corner_positions[corner]
                
                # Draw location name
                name = info.get('name', 'Unknown')
                self.stdscr.addstr(y, x, name, self.color_pairs['corner'] | curses.A_BOLD)
                
                # Draw time
                time_str = info.get('time', 'N/A')
                self.stdscr.addstr(y + 1, x, time_str, self.color_pairs['corner'])
                
                # Draw UTC offset
                offset = info.get('utc_offset', '')
                if offset:
                    self.stdscr.addstr(y + 2, x, f"UTC{offset}", self.color_pairs['corner'])
    
    def _draw_status_bar(self, current_time: datetime) -> None:
        """Draw status bar at bottom."""
        status_text = "Press 'h' for help | 'q' to quit | 'r' to refresh"
        
        # Draw status line
        self.stdscr.addstr(
            self.height - 1, 0,
            status_text[:self.width],
            self.color_pairs['status']
        )
    
    def _draw_help_overlay(self) -> None:
        """Draw help overlay."""
        if not self.stdscr:
            return
        
        help_text = [
            "Atomic Clock - Help",
            "",
            "Commands:",
            "  h - Toggle this help",
            "  q - Quit",
            "  r - Refresh time sync",
            "  s - Show sync status",
            "  + - Increase update interval",
            "  - - Decrease update interval",
            "  ESC - Quit",
            "",
            "Press any key to close help"
        ]
        
        # Calculate overlay dimensions
        max_width = max(len(line) for line in help_text) + 4
        overlay_height = len(help_text) + 2
        overlay_x = (self.width - max_width) // 2
        overlay_y = (self.height - overlay_height) // 2
        
        # Ensure overlay fits in screen
        overlay_x = max(0, min(overlay_x, self.width - max_width))
        overlay_y = max(0, min(overlay_y, self.height - overlay_height))
        
        # Draw overlay background
        for y in range(overlay_height):
            self.stdscr.addstr(
                overlay_y + y, overlay_x,
                " " * min(max_width, self.width - overlay_x),
                self.color_pairs['help']
            )
        
        # Draw help text
        for i, line in enumerate(help_text):
            text_x = overlay_x + 2
            text_y = overlay_y + i
            if text_x < self.width and text_y < self.height:
                self.stdscr.addstr(text_y, text_x, line, self.color_pairs['help'])
    
    def update_size(self, width: int, height: int) -> None:
        """Update display size."""
        self.width = width
        self.height = height
        
        # Resize terminal if possible
        if self.stdscr:
            try:
                curses.resizeterm(height, width)
            except curses.error:
                pass  # Some terminals don't support resize
    
    def cleanup(self) -> None:
        """Cleanup curses resources."""
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.curs_set(1)
            curses.endwin()
            self.stdscr = None
        self.initialized = False
    
    def handle_keypress(self, key: str) -> bool:
        """Handle keyboard input."""
        if not self.stdscr:
            return False
        
        # Handle special keys
        if key == curses.KEY_RESIZE:
            y, x = self.stdscr.getmaxyx()
            self.update_size(x, y)
            return True
        
        # Handle help toggle
        if key == 'h':
            if self.showing_help:
                self.hide_help()
            else:
                self.show_help()
            return True
        
        # Handle escape sequences
        if key == 27:  # ESC
            return True
        
        return False
    
    def show_help(self) -> None:
        """Show help overlay."""
        self.showing_help = True
    
    def hide_help(self) -> None:
        """Hide help overlay."""
        self.showing_help = False
    
    def get_size(self) -> Tuple[int, int]:
        """Get current display size."""
        if self.stdscr:
            try:
                y, x = self.stdscr.getmaxyx()
                return (x, y)
            except curses.error:
                pass
        return (self.width, self.height)
