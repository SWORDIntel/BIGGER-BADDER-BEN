#!/usr/bin/env python3
"""
Interactive Command Palette and Help Overlay for Atomic Clock Display

Provides an interactive command palette with search and help functionality.
"""

import curses
import curses.ascii
from typing import List, Dict, Optional, Callable, Tuple
from datetime import datetime
import re


class Command:
    """Represents a command in the palette."""
    
    def __init__(self, name: str, description: str, key: str, 
                 action: Callable[[], None], category: str = "General"):
        """
        Initialize a command.
        
        Args:
            name: Command name
            description: Command description
            key: Keyboard shortcut
            action: Function to execute when command is selected
            category: Command category for grouping
        """
        self.name = name
        self.description = description
        self.key = key
        self.action = action
        self.category = category


class CommandPalette:
    """Interactive command palette with search and help functionality."""
    
    def __init__(self, stdscr):
        """
        Initialize command palette.
        
        Args:
            stdscr: Curses screen object
        """
        self.stdscr = stdscr
        self.commands: List[Command] = []
        self.filtered_commands: List[Command] = []
        self.selected_index = 0
        self.search_text = ""
        self.showing = False
        self.showing_help = False
        self.categories = set()
        
        # Color pairs
        self.colors = {
            'selected': curses.color_pair(1) if curses.has_colors() else curses.A_REVERSE,
            'normal': curses.color_pair(0),
            'category': curses.color_pair(2) if curses.has_colors() else curses.A_BOLD,
            'search': curses.color_pair(3) if curses.has_colors() else curses.A_UNDERLINE,
            'help': curses.color_pair(4) if curses.has_colors() else curses.A_NORMAL,
        }
        
        # Initialize colors if available
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Selected
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Category
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Search
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Help
    
    def add_command(self, name: str, description: str, key: str, 
                   action: Callable[[], None], category: str = "General"):
        """Add a command to the palette."""
        command = Command(name, description, key, action, category)
        self.commands.append(command)
        self.categories.add(category)
    
    def show(self) -> Optional[Command]:
        """
        Show the command palette and return selected command.
        
        Returns:
            Selected command or None if cancelled
        """
        self.showing = True
        self.search_text = ""
        self.selected_index = 0
        self._update_filtered_commands()
        
        while self.showing:
            self._draw()
            key = self.stdscr.getch()
            
            if not self._handle_input(key):
                break
        
        self.showing = False
        return self.filtered_commands[self.selected_index] if self.selected_index < len(self.filtered_commands) else None
    
    def show_help(self) -> None:
        """Show help overlay."""
        self.showing_help = True
        
        while self.showing_help:
            self._draw_help()
            key = self.stdscr.getch()
            
            if key in [curses.ascii.ESC, ord('q'), ord('h'), ord(' ')]:
                self.showing_help = False
    
    def _update_filtered_commands(self):
        """Update filtered commands based on search text."""
        if not self.search_text:
            self.filtered_commands = self.commands.copy()
        else:
            search_lower = self.search_text.lower()
            self.filtered_commands = [
                cmd for cmd in self.commands
                if (search_lower in cmd.name.lower() or 
                    search_lower in cmd.description.lower() or
                    search_lower in cmd.category.lower() or
                    search_lower in cmd.key.lower())
            ]
        
        # Reset selection if out of bounds
        if self.selected_index >= len(self.filtered_commands):
            self.selected_index = max(0, len(self.filtered_commands) - 1)
    
    def _handle_input(self, key: int) -> bool:
        """Handle keyboard input."""
        if key == curses.ascii.ESC or key == ord('q'):
            return False  # Exit palette
        
        elif key == curses.KEY_UP or key == curses.KEY_PPAGE:
            self.selected_index = max(0, self.selected_index - 1)
        
        elif key == curses.KEY_DOWN or key == curses.KEY_NPAGE:
            self.selected_index = min(len(self.filtered_commands) - 1, self.selected_index + 1)
        
        elif key == curses.KEY_HOME:
            self.selected_index = 0
        
        elif key == curses.KEY_END:
            self.selected_index = len(self.filtered_commands) - 1
        
        elif key == ord('\n') or key == curses.KEY_ENTER:
            if self.selected_index < len(self.filtered_commands):
                command = self.filtered_commands[self.selected_index]
                command.action()
                return False  # Exit after executing
        
        elif key == curses.KEY_BACKSPACE or key == 127:
            if self.search_text:
                self.search_text = self.search_text[:-1]
                self._update_filtered_commands()
        
        elif key == ord('h'):
            self.show_help()
        
        elif curses.ascii.isprint(key):
            self.search_text += chr(key)
            self._update_filtered_commands()
        
        return True  # Continue showing palette
    
    def _draw(self):
        """Draw the command palette."""
        if not self.stdscr:
            return
        
        height, width = self.stdscr.getmaxyx()
        
        # Calculate palette dimensions
        max_width = min(width - 4, 80)
        max_height = min(height - 4, 20)
        
        palette_width = max_width
        palette_height = min(max_height, len(self.filtered_commands) + 4)
        
        # Center the palette
        start_x = (width - palette_width) // 2
        start_y = (height - palette_height) // 2
        
        # Draw palette background
        for y in range(palette_height):
            for x in range(palette_width):
                if start_y + y < height and start_x + x < width:
                    self.stdscr.addch(start_y + y, start_x + x, ' ', self.colors['help'])
        
        # Draw border
        if start_y + palette_height - 1 < height:
            self.stdscr.addstr(start_y + palette_height - 1, start_x, 
                             "─" * palette_width, self.colors['help'])
        
        # Draw title
        title = "Command Palette"
        title_x = start_x + (palette_width - len(title)) // 2
        if start_y < height and title_x + len(title) <= width:
            self.stdscr.addstr(start_y, title_x, title, self.colors['help'] | curses.A_BOLD)
        
        # Draw search box
        search_label = "Search: "
        search_y = start_y + 2
        if search_y < height:
            self.stdscr.addstr(search_y, start_x + 2, search_label, self.colors['help'])
            search_x = start_x + 2 + len(search_label)
            search_display = self.search_text[-(palette_width - len(search_label) - 4):]
            if search_x + len(search_display) <= width:
                self.stdscr.addstr(search_y, search_x, search_display, self.colors['search'])
        
        # Draw commands
        current_category = None
        command_y = start_y + 4
        
        for i, command in enumerate(self.filtered_commands):
            if command_y >= height - 1:
                break
            
            # Draw category header if changed
            if command.category != current_category:
                current_category = command.category
                if command_y < height:
                    self.stdscr.addstr(command_y, start_x + 2, f"[{current_category}]", 
                                     self.colors['category'])
                command_y += 1
            
            if command_y >= height - 1:
                break
            
            # Highlight selected command
            attr = self.colors['selected'] if i == self.selected_index else self.colors['normal']
            
            # Format command line
            line = f"{command.key:3} {command.name}"
            if len(line) < palette_width - 10:
                line += " - " + command.description[:palette_width - len(line) - 3]
            
            # Truncate if too long
            if len(line) > palette_width - 4:
                line = line[:palette_width - 7] + "..."
            
            if start_x + 2 < width and command_y < height:
                self.stdscr.addstr(command_y, start_x + 2, line, attr)
            
            command_y += 1
        
        # Draw instructions
        if start_y + palette_height - 2 < height:
            instructions = "↑↓ Navigate | Enter Execute | ESC/ q Quit | h Help"
            inst_x = start_x + (palette_width - len(instructions)) // 2
            self.stdscr.addstr(start_y + palette_height - 2, inst_x, 
                             instructions, self.colors['help'])
        
        self.stdscr.refresh()
    
    def _draw_help(self):
        """Draw help overlay."""
        if not self.stdscr:
            return
        
        height, width = self.stdscr.getmaxyx()
        
        # Help content
        help_content = [
            "Atomic Clock Display - Help",
            "",
            "═══════════════════════════════════════════════════════════════",
            "",
            "COMMAND PALETTE:",
            "  Ctrl+P or /     - Open command palette",
            "  ESC             - Close palette/help",
            "",
            "KEYBOARD SHORTCUTS:",
            "  h               - Toggle this help",
            "  q / ESC         - Quit application",
            "  r               - Refresh time synchronization",
            "  s               - Show sync status",
            "  + / -           - Increase/decrease update interval",
            "  f               - Toggle fullscreen mode",
            "  c               - Cycle color themes",
            "  t               - Toggle 12/24 hour format",
            "  d               - Toggle date display",
            "  l               - Reload configuration",
            "  e               - Export drift data",
            "  a               - Show drift alerts",
            "  Ctrl+R          - Reset drift monitoring",
            "",
            "COMMAND PALETTE SEARCH:",
            "  Type any text to filter commands",
            "  Use arrow keys to navigate",
            "  Press Enter to execute selected command",
            "",
            "RENDERERS:",
            "  --renderer curses  - Terminal UI (default)",
            "  --renderer web     - Web interface",
            "  --renderer ansi    - ANSI/Kitty graphics",
            "",
            "═══════════════════════════════════════════════════════════════",
            "",
            "Press any key to close help"
        ]
        
        # Calculate overlay dimensions
        max_width = max(len(line) for line in help_content) + 4
        overlay_height = len(help_content) + 2
        
        max_width = min(max_width, width - 4)
        overlay_height = min(overlay_height, height - 4)
        
        # Center the overlay
        start_x = (width - max_width) // 2
        start_y = (height - overlay_height) // 2
        
        # Draw overlay background
        for y in range(overlay_height):
            for x in range(max_width):
                if start_y + y < height and start_x + x < width:
                    self.stdscr.addch(start_y + y, start_x + x, ' ', self.colors['help'])
        
        # Draw help content
        for i, line in enumerate(help_content):
            if start_y + i + 1 >= height:
                break
            
            # Truncate line if too long
            display_line = line[:max_width - 4]
            
            # Apply formatting based on content
            attr = self.colors['help']
            if line.startswith("════"):
                attr |= curses.A_BOLD
            elif line.endswith(":") and not line.startswith(" "):
                attr = self.colors['category']
            elif line.startswith("  "):
                attr = self.colors['normal']
            elif line == "Atomic Clock Display - Help":
                attr |= curses.A_BOLD | curses.A_UNDERLINE
            
            self.stdscr.addstr(start_y + i + 1, start_x + 2, display_line, attr)
        
        self.stdscr.refresh()


class CommandPaletteManager:
    """Manages command palette integration with the main application."""
    
    def __init__(self, app):
        """
        Initialize command palette manager.
        
        Args:
            app: AtomicClockApp instance
        """
        self.app = app
        self.palette = None
        self.commands_registered = False
    
    def initialize(self, stdscr):
        """Initialize command palette with curses screen."""
        self.palette = CommandPalette(stdscr)
        self._register_commands()
        self.commands_registered = True
    
    def _register_commands(self):
        """Register all available commands."""
        if not self.palette:
            return
        
        # Navigation commands
        self.palette.add_command(
            "Help", "Show this help overlay", "h",
            self._show_help, "Navigation"
        )
        
        self.palette.add_command(
            "Quit", "Exit the application", "q",
            self._quit_app, "Navigation"
        )
        
        # Time commands
        self.palette.add_command(
            "Refresh", "Refresh time synchronization", "r",
            self._refresh_sync, "Time"
        )
        
        self.palette.add_command(
            "Sync Status", "Show synchronization status", "s",
            self._show_sync_status, "Time"
        )
        
        self.palette.add_command(
            "Toggle Format", "Switch between 12/24 hour format", "t",
            self._toggle_time_format, "Time"
        )
        
        self.palette.add_command(
            "Toggle Date", "Show/hide date display", "d",
            self._toggle_date_display, "Time"
        )
        
        # Display commands
        self.palette.add_command(
            "Fullscreen", "Toggle fullscreen mode", "f",
            self._toggle_fullscreen, "Display"
        )
        
        self.palette.add_command(
            "Cycle Theme", "Cycle through color themes", "c",
            self._cycle_theme, "Display"
        )
        
        self.palette.add_command(
            "Increase Interval", "Increase update interval", "+",
            self._increase_interval, "Display"
        )
        
        self.palette.add_command(
            "Decrease Interval", "Decrease update interval", "-",
            self._decrease_interval, "Display"
        )
        
        # Configuration commands
        self.palette.add_command(
            "Reload Config", "Reload configuration files", "l",
            self._reload_config, "Configuration"
        )
        
        # Monitoring commands
        self.palette.add_command(
            "Export Data", "Export drift monitoring data", "e",
            self._export_data, "Monitoring"
        )
        
        self.palette.add_command(
            "Show Alerts", "Show drift alerts", "a",
            self._show_alerts, "Monitoring"
        )
        
        self.palette.add_command(
            "Reset Monitoring", "Reset drift monitoring", "Ctrl+R",
            self._reset_monitoring, "Monitoring"
        )
    
    def show_palette(self) -> bool:
        """
        Show command palette.
        
        Returns:
            True if a command was executed, False otherwise
        """
        if not self.palette:
            return False
        
        command = self.palette.show()
        return command is not None
    
    def show_help(self):
        """Show help overlay."""
        if self.palette:
            self.palette.show_help()
    
    # Command implementations
    def _show_help(self):
        """Show help overlay."""
        self.show_help()
    
    def _quit_app(self):
        """Quit the application."""
        self.app.running = False
    
    def _refresh_sync(self):
        """Refresh time synchronization."""
        if hasattr(self.app, 'time_sync'):
            self.app.time_sync.sync_with_ntp()
    
    def _show_sync_status(self):
        """Show synchronization status."""
        if hasattr(self.app, '_show_sync_status'):
            self.app._show_sync_status()
    
    def _toggle_time_format(self):
        """Toggle between 12/24 hour format."""
        if hasattr(self.app, 'time_format_24h'):
            self.app.time_format_24h = not self.app.time_format_24h
    
    def _toggle_date_display(self):
        """Toggle date display."""
        if hasattr(self.app, 'show_date'):
            self.app.show_date = not self.app.show_date
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if hasattr(self.app, 'fullscreen'):
            self.app.fullscreen = not self.app.fullscreen
    
    def _cycle_theme(self):
        """Cycle through color themes."""
        if hasattr(self.app, 'color_theme'):
            themes = ['default', 'dark', 'light', 'blue', 'green']
            current_index = themes.index(self.app.color_theme) if self.app.color_theme in themes else 0
            self.app.color_theme = themes[(current_index + 1) % len(themes)]
    
    def _increase_interval(self):
        """Increase update interval."""
        if hasattr(self.app, 'update_interval'):
            self.app.update_interval = min(self.app.update_interval + 0.1, 5.0)
    
    def _decrease_interval(self):
        """Decrease update interval."""
        if hasattr(self.app, 'update_interval'):
            self.app.update_interval = max(self.app.update_interval - 0.1, 0.1)
    
    def _reload_config(self):
        """Reload configuration files."""
        if hasattr(self.app, 'location_manager'):
            self.app.location_manager.load_locations()
    
    def _export_data(self):
        """Export drift monitoring data."""
        if hasattr(self.app, 'drift_monitor'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"drift_export_{timestamp}.json"
            self.app.drift_monitor.export_data(filename)
    
    def _show_alerts(self):
        """Show drift alerts."""
        if hasattr(self.app, 'drift_monitor'):
            alerts = self.app.drift_monitor.get_recent_alerts(24)
            # This would need to be displayed in the UI
            print(f"Recent alerts: {len(alerts)}")
    
    def _reset_monitoring(self):
        """Reset drift monitoring."""
        if hasattr(self.app, 'drift_monitor'):
            self.app.drift_monitor.stop_monitoring()
            self.app.drift_monitor.start_monitoring(self.app.time_sync)
