#!/usr/bin/env python3
"""
Complex Atomic Clock Renderer

Renders a sophisticated atomic clock face with multiple decorative elements,
concentric circles, detailed markers, and complex visual design.
"""

import math
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple
import shutil


class ClockRenderer:
    """Render complex atomic clock face in terminal."""
    
    def __init__(self, width: int = 80, height: int = 24):
        """
        Initialize clock renderer.
        
        Args:
            width: Terminal width in characters
            height: Terminal height in characters
        """
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Account for terminal character aspect ratio (typically ~2:1 height:width)
        # This makes circles appear circular instead of squashed
        self.aspect_ratio = 2.0  # Terminal chars are ~2x taller than wide
        # Use more of the width to fill screen and eliminate black spaces
        self.radius = min(width // 2, height) // 2.5  # Larger radius to fill width
        
        # Unicode characters for SPACE-AGE EXTREMELY complex drawing
        self.chars = {
            # Circles and dots - multiple sizes
            'circle': '○',
            'circle_thick': '◉',
            'circle_double': '◎',
            'filled': '●',
            'filled_large': '◉',
            'small_dot': '·',
            'medium_dot': '•',
            'large_dot': '●',
            'dot_white': '○',
            'dot_black': '●',
            
            # SPACE-AGE SYMBOLS
            'planet': '◉',
            'star': '✦',
            'star_bright': '★',
            'star_sparkle': '✧',
            'comet': '☄',
            'satellite': '🛰',
            'rocket': '🚀',
            'galaxy': '🌌',
            'nebula': '✨',
            'orbit': '◯',
            'ring_planet': '◯',
            'asteroid': '•',
            'pulsar': '⚡',
            'quasar': '◉',
            'wormhole': '◉',
            'energy': '⚡',
            'laser': '─',
            'beam': '│',
            'grid': '┼',
            'circuit': '┼',
            'hologram': '◯',
            'scan': '─',
            'radar': '◯',
            
            # Lines and borders - many variations
            'hand': '─',
            'hand_thick': '━',
            'hand_thin': '─',
            'hand_double': '═',
            'vertical': '│',
            'vertical_thick': '┃',
            'horizontal': '─',
            'horizontal_thick': '━',
            'double_h': '═',
            'double_v': '║',
            'diagonal_ul_br': '╲',
            'diagonal_ur_bl': '╱',
            
            # Box drawing - complete set
            'corner_tl': '┌',
            'corner_tr': '┐',
            'corner_bl': '└',
            'corner_br': '┘',
            'corner_tl_round': '╭',
            'corner_tr_round': '╮',
            'corner_bl_round': '╰',
            'corner_br_round': '╯',
            'corner_tl_double': '╔',
            'corner_tr_double': '╗',
            'corner_bl_double': '╚',
            'corner_br_double': '╝',
            'line_h': '─',
            'line_v': '│',
            'line_h_double': '═',
            'line_v_double': '║',
            'line_h_thick': '━',
            'line_v_thick': '┃',
            'cross': '┼',
            'cross_h': '├',
            'cross_v': '┬',
            'cross_double': '╬',
            'cross_thick': '┿',
            
            # Decorative symbols - extensive collection
            'star': '✦',
            'star_filled': '★',
            'star_outline': '☆',
            'star_sparkle': '✧',
            'diamond': '◆',
            'diamond_filled': '◆',
            'diamond_outline': '◇',
            'square': '■',
            'square_outline': '□',
            'square_small': '▪',
            'square_large': '▬',
            'triangle': '▲',
            'triangle_outline': '△',
            'triangle_down': '▼',
            'triangle_left': '◄',
            'triangle_right': '►',
            'arrow_up': '↑',
            'arrow_down': '↓',
            'arrow_left': '←',
            'arrow_right': '→',
            'arrow_double_up': '⇑',
            'arrow_double_down': '⇓',
            'arrow_double_left': '⇐',
            'arrow_double_right': '⇒',
            'arrow_cross': '↔',
            'arrow_vertical': '↕',
            
            # Additional decorative
            'sun': '☀',
            'moon': '☾',
            'sparkle': '✨',
            'ring': '◯',
            'ring_thick': '◉',
            'bullet': '•',
            'bullet_large': '●',
            'check': '✓',
            'cross_mark': '✗',
            'infinity': '∞',
            'pi': 'π',
            'sigma': 'Σ',
            'omega': 'Ω',
        }
    
    def update_size(self, width: int, height: int):
        """Update terminal size and recalculate layout."""
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 3
    
    def clear_screen(self):
        """Clear terminal screen."""
        sys.stdout.write('\033[2J')
        sys.stdout.write('\033[H')
        sys.stdout.flush()
    
    def move_cursor(self, x: int, y: int):
        """Move cursor to position."""
        sys.stdout.write(f'\033[{y};{x}H')
    
    def set_color(self, color_code: int, bold: bool = False):
        """Set text color with optional bold."""
        if bold:
            sys.stdout.write(f'\033[1;{color_code}m')
        else:
            sys.stdout.write(f'\033[{color_code}m')
    
    def reset_color(self):
        """Reset to default color."""
        sys.stdout.write('\033[0m')
    
    def render_clock_face(self, hour: int, minute: int, second: int):
        """Render SPACE-AGE EXTREMELY complex circular clock face with hands."""
        # Clear screen first
        self.clear_screen()
        
        # Fill entire screen with space-age background FIRST to eliminate black spaces
        self._draw_space_age_background()
        
        # Convert to 12-hour format
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
        
        # Calculate angles (0° = 12 o'clock, clockwise)
        hour_angle = math.radians((hour_12 * 30 + minute * 0.5) - 90)
        minute_angle = math.radians((minute * 6) - 90)
        second_angle = math.radians((second * 6) - 90)
        
        # SPACE-AGE outer decorative rings (layered complexity)
        self._draw_decorative_ring(self.center_x, self.center_y, self.radius + 6, 'outer_outer')
        self._draw_decorative_ring(self.center_x, self.center_y, self.radius + 4, 'outer')
        self._draw_decorative_ring(self.center_x, self.center_y, self.radius + 2, 'outer_inner')
        
        # Draw ornate outer border with multiple layers
        self._draw_ornate_border()
        
        # Draw main clock face circle (thick, multiple layers)
        self._draw_thick_circle(self.center_x, self.center_y, self.radius)
        self._draw_thick_circle(self.center_x, self.center_y, self.radius - 1)  # Second layer
        
        # Draw multiple inner decorative rings
        self._draw_decorative_ring(self.center_x, self.center_y, self.radius - 2, 'inner_outer')
        self._draw_decorative_ring(self.center_x, self.center_y, self.radius - 3, 'inner')
        self._draw_decorative_ring(self.center_x, self.center_y, self.radius - 4, 'inner_inner')
        
        # Draw minute/second tick marks (60 marks) - multiple layers
        self._draw_minute_marks()
        self._draw_second_marks()  # Additional second marks
        
        # Draw hour markers with different styles - enhanced
        self._draw_complex_hour_markers()
        self._draw_hour_decorations()  # Additional hour decorations
        
        # Draw decorative elements at cardinal points - multiple layers
        self._draw_cardinal_decorations()
        self._draw_cardinal_rings()  # Rings around cardinal points
        
        # Draw ornate patterns between hours
        self._draw_inter_hour_patterns()
        
        # Draw radial decorative lines
        self._draw_radial_decorations()
        
        # Draw hands with EXTREMELY clear design - draw shadows first, then hands
        # Draw hand shadows/outlines FIRST for depth (behind hands)
        self._draw_hand_shadows(hour_angle, minute_angle, second_angle)
        
        # Draw hands with MUCH clearer appearance - multiple passes for visibility
        # Draw hour hand multiple times for extra thickness
        for _ in range(2):
            self._draw_complex_hand(self.center_x, self.center_y, hour_angle, self.radius * 0.5, 'hour')
        self._draw_complex_hand(self.center_x, self.center_y, hour_angle, self.radius * 0.5, 'hour')
        
        # Draw minute hand multiple times for extra thickness
        for _ in range(2):
            self._draw_complex_hand(self.center_x, self.center_y, minute_angle, self.radius * 0.75, 'minute')
        self._draw_complex_hand(self.center_x, self.center_y, minute_angle, self.radius * 0.75, 'minute')
        
        # Draw second hand (single pass but very clear)
        self._draw_complex_hand(self.center_x, self.center_y, second_angle, self.radius * 0.9, 'second')
        
        # Draw hand highlights for extra clarity
        self._draw_hand_highlights(hour_angle, minute_angle, second_angle)
        
        # Draw center hub with decorative elements - multiple layers
        self._draw_center_hub()
        self._draw_center_rings()  # Additional center rings
        
        # Draw multiple inner decorative patterns
        self._draw_inner_pattern()
        self._draw_spiral_pattern()
        self._draw_geometric_pattern()
        
        # Draw corner decorations
        self._draw_corner_ornaments()
        
        # Draw additional decorative elements
        self._draw_ornamental_fill()
        
        # Draw SPACE-AGE decorations - futuristic sci-fi elements
        self._draw_space_age_background()
        self._draw_orbital_rings()
        self._draw_starfield()
        self._draw_planet_orbits()
        self._draw_satellite_traces()
        self._draw_energy_grid()
        self._draw_holographic_effects()
        self._draw_radar_sweeps()
        self._draw_circuit_patterns()
        self._draw_nebula_clouds()
        self._draw_pulsar_beams()
        self._draw_wormhole_effects()
        self._draw_quantum_fields()
        self._draw_metallic_effects()
        self._draw_shadow_layers()
        self._draw_complex_border_patterns()
        self._draw_layered_decorations()
        self._draw_geometric_overlays()
        self._draw_radial_sweeps()
        self._draw_concentric_ornaments()
        self._draw_astronomical_symbols()
        self._draw_mathematical_patterns()
        
        sys.stdout.flush()
    
    def _draw_thick_circle(self, cx: int, cy: int, radius: int):
        """Draw EXTREMELY thick circle with multiple ornate layers."""
        # Layer 1: Outer thick border
        for angle in range(0, 360, 1):
            rad = math.radians(angle)
            x = int(cx + radius * self.aspect_ratio * math.cos(rad))
            y = int(cy + radius * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(36, bold=True)  # Bright cyan
                sys.stdout.write(self.chars['filled_large'])
                self.reset_color()
        
        # Layer 2: Decorative middle layer
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            x = int(cx + (radius - 0.5) * self.aspect_ratio * math.cos(rad))
            y = int(cy + (radius - 0.5) * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(36)  # Cyan
                sys.stdout.write(self.chars['circle_double'])
                self.reset_color()
        
        # Layer 3: Inner decorative layer
        for angle in range(0, 360, 3):
            rad = math.radians(angle)
            x = int(cx + (radius - 1) * self.aspect_ratio * math.cos(rad))
            y = int(cy + (radius - 1) * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(33)  # Yellow
                sys.stdout.write(self.chars['circle'])
                self.reset_color()
        
        # Layer 4: Innermost accent layer
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x = int(cx + (radius - 1.5) * self.aspect_ratio * math.cos(rad))
            y = int(cy + (radius - 1.5) * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(35)  # Magenta
                sys.stdout.write(self.chars['medium_dot'])
                self.reset_color()
    
    def _draw_decorative_ring(self, cx: int, cy: int, radius: int, ring_type: str):
        """Draw decorative ring around clock with multiple styles."""
        ring_configs = {
            'outer_outer': {'char': self.chars['star'], 'color': 35, 'step': 12, 'bold': True},
            'outer': {'char': self.chars['small_dot'], 'color': 35, 'step': 8, 'bold': False},
            'outer_inner': {'char': self.chars['medium_dot'], 'color': 36, 'step': 6, 'bold': False},
            'inner_outer': {'char': self.chars['diamond_outline'], 'color': 33, 'step': 15, 'bold': False},
            'inner': {'char': self.chars['medium_dot'], 'color': 33, 'step': 6, 'bold': False},
            'inner_inner': {'char': self.chars['small_dot'], 'color': 37, 'step': 4, 'bold': False},
        }
        
        config = ring_configs.get(ring_type, {'char': self.chars['small_dot'], 'color': 37, 'step': 8, 'bold': False})
        
        for angle in range(0, 360, config['step']):
            rad = math.radians(angle)
            x = int(cx + radius * self.aspect_ratio * math.cos(rad))
            y = int(cy + radius * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(config['color'], bold=config['bold'])
                sys.stdout.write(config['char'])
                self.reset_color()
    
    def _draw_minute_marks(self):
        """Draw minute/second tick marks (60 marks total), accounting for aspect ratio."""
        for minute in range(0, 60):
            angle = math.radians((minute * 6) - 90)
            
            # Determine mark style based on position
            if minute % 5 == 0:
                # Major marks (at 5-minute intervals) - longer
                outer_radius = self.radius
                inner_radius = self.radius - 2
                char = self.chars['filled']
                color = 33  # Yellow
            elif minute % 1 == 0:
                # Minor marks (every minute) - shorter
                outer_radius = self.radius
                inner_radius = self.radius - 1
                char = self.chars['small_dot']
                color = 37  # White
            
            # Draw mark - multiply X by aspect ratio
            outer_x = int(self.center_x + outer_radius * self.aspect_ratio * math.cos(angle))
            outer_y = int(self.center_y + outer_radius * math.sin(angle))
            inner_x = int(self.center_x + inner_radius * self.aspect_ratio * math.cos(angle))
            inner_y = int(self.center_y + inner_radius * math.sin(angle))
            
            if 1 <= outer_x <= self.width and 1 <= outer_y <= self.height:
                self.move_cursor(outer_x, outer_y)
                self.set_color(color)
                sys.stdout.write(char)
                self.reset_color()
    
    def _draw_complex_hour_markers(self):
        """Draw hour markers with different styles, accounting for aspect ratio."""
        for hour in range(1, 13):
            angle = math.radians((hour * 30) - 90)
            
            # Different styles for different hour positions
            if hour in [12, 3, 6, 9]:  # Cardinal positions
                # Large decorative markers
                marker_length = 3
                marker_char = self.chars['diamond']
                marker_color = 31  # Red
                num_color = 31  # Red, bold
                num_bold = True
            elif hour in [1, 2, 4, 5, 7, 8, 10, 11]:  # Other positions
                # Medium markers
                marker_length = 2
                marker_char = self.chars['square']
                marker_color = 33  # Yellow
                num_color = 37  # White
                num_bold = False
            
            # Draw marker line - multiply X by aspect ratio
            for i in range(marker_length):
                marker_radius = self.radius - i
                marker_x = int(self.center_x + marker_radius * self.aspect_ratio * math.cos(angle))
                marker_y = int(self.center_y + marker_radius * math.sin(angle))
                
                if 1 <= marker_x <= self.width and 1 <= marker_y <= self.height:
                    self.move_cursor(marker_x, marker_y)
                    self.set_color(marker_color)
                    sys.stdout.write(marker_char)
                    self.reset_color()
            
            # Draw hour number with decorative background
            num_x = int(self.center_x + (self.radius + 3) * self.aspect_ratio * math.cos(angle))
            num_y = int(self.center_y + (self.radius + 3) * math.sin(angle))
            
            if 1 <= num_x <= self.width and 1 <= num_y <= self.height:
                self.move_cursor(num_x, num_y)
                self.set_color(num_color, bold=num_bold)
                sys.stdout.write(str(hour))
                self.reset_color()
    
    def _draw_cardinal_decorations(self):
        """Draw decorative elements at cardinal points, accounting for aspect ratio."""
        decorations = [
            (0, '↑', 32),    # North - Green arrow up
            (90, '→', 34),   # East - Blue arrow right
            (180, '↓', 31),  # South - Red arrow down
            (270, '←', 35),  # West - Magenta arrow left
        ]
        
        for angle_deg, char, color in decorations:
            angle = math.radians(angle_deg - 90)
            # Multiply X by aspect ratio
            deco_x = int(self.center_x + (self.radius + 5) * self.aspect_ratio * math.cos(angle))
            deco_y = int(self.center_y + (self.radius + 5) * math.sin(angle))
            
            if 1 <= deco_x <= self.width and 1 <= deco_y <= self.height:
                self.move_cursor(deco_x, deco_y)
                self.set_color(color, bold=True)
                sys.stdout.write(char)
                self.reset_color()
    
    def _draw_complex_hand(self, cx: int, cy: int, angle: float, length: int, hand_type: str):
        """Draw EXTREMELY clear and visible hand with multiple layers for maximum visibility."""
        # Determine hand style with MUCH clearer appearance
        if hand_type == 'hour':
            color = 31  # Red - very visible
            bg_color = 90  # Dark gray for outline
            char = self.chars['filled']
            tip_char = self.chars['diamond']
            steps = int(length * 0.8)
            thickness = 3  # Make hour hand very thick
        elif hand_type == 'minute':
            color = 32  # Green - very visible
            bg_color = 90  # Dark gray for outline
            char = self.chars['filled']
            tip_char = self.chars['arrow_up']
            steps = int(length * 0.9)
            thickness = 2  # Make minute hand thick
        else:  # second
            color = 33  # Yellow - very visible
            bg_color = 90  # Dark gray for outline
            char = self.chars['filled']
            tip_char = self.chars['filled']
            steps = int(length)
            thickness = 1  # Second hand thinner but still clear
        
        # Calculate end point
        end_x = int(cx + length * self.aspect_ratio * math.cos(angle))
        end_y = int(cy + length * math.sin(angle))
        
        # Draw hand outline/shadow FIRST for depth and clarity
        for offset_angle in [-0.05, 0.05]:  # Slight angle offsets for outline
            outline_angle = angle + offset_angle
            for i in range(steps):
                t = i / steps
                x = int(cx + t * length * self.aspect_ratio * math.cos(outline_angle))
                y = int(cy + t * length * math.sin(outline_angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(bg_color)  # Dark outline
                    sys.stdout.write(char)
                    self.reset_color()
        
        # Draw main hand line - MUCH thicker and clearer
        for i in range(steps):
            t = i / steps
            base_x = cx + t * length * self.aspect_ratio * math.cos(angle)
            base_y = cy + t * length * math.sin(angle)
            
            # Draw multiple pixels for thickness
            for thickness_offset in range(-thickness, thickness + 1):
                # Perpendicular offset for thickness
                perp_angle = angle + math.pi / 2
                offset_x = thickness_offset * 0.3 * self.aspect_ratio * math.cos(perp_angle)
                offset_y = thickness_offset * 0.3 * math.sin(perp_angle)
                
                x = int(base_x + offset_x)
                y = int(base_y + offset_y)
                
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(color, bold=True)  # Always bold for clarity
                    # Use filled characters for better visibility
                    sys.stdout.write(char)
                    self.reset_color()
        
        # Draw hand tip - MUCH larger and clearer
        if 1 <= end_x <= self.width and 1 <= end_y <= self.height:
            # Draw tip outline first
            for tip_offset_x in [-1, 0, 1]:
                for tip_offset_y in [-1, 0, 1]:
                    tip_x = end_x + tip_offset_x
                    tip_y = end_y + tip_offset_y
                    if 1 <= tip_x <= self.width and 1 <= tip_y <= self.height:
                        self.move_cursor(tip_x, tip_y)
                        if tip_offset_x == 0 and tip_offset_y == 0:
                            # Center - main tip
                            self.set_color(color, bold=True)
                            sys.stdout.write(tip_char)
                        else:
                            # Outline
                            self.set_color(bg_color)
                            sys.stdout.write(tip_char)
                        self.reset_color()
        
        # Draw additional tip highlight for extra clarity
        if 1 <= end_x <= self.width and 1 <= end_y <= self.height:
            self.move_cursor(end_x, end_y)
            self.set_color(37, bold=True)  # Bright white highlight
            sys.stdout.write(tip_char)
            self.reset_color()
    
    def _draw_center_hub(self):
        """Draw EXTREMELY ornate center hub with multiple decorative layers."""
        # Outer decorative ring - stars
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = int(self.center_x + 3 * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + 3 * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(35, bold=True)  # Bright magenta
                sys.stdout.write(self.chars['star_filled'])
                self.reset_color()
        
        # Middle decorative ring - diamonds
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            x = int(self.center_x + 2.5 * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + 2.5 * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(36)  # Cyan
                sys.stdout.write(self.chars['diamond'])
                self.reset_color()
        
        # Inner ring - dots
        for angle in range(0, 360, 20):
            rad = math.radians(angle)
            x = int(self.center_x + 2 * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + 2 * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(33)  # Yellow
                sys.stdout.write(self.chars['medium_dot'])
                self.reset_color()
        
        # Center core - multiple layers
        # Outer center ring
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x = int(self.center_x + 1.5 * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + 1.5 * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(37, bold=True)  # Bright white
                sys.stdout.write(self.chars['star'])
                self.reset_color()
        
        # Center dot - large and bold
        self.move_cursor(self.center_x, self.center_y)
        self.set_color(37, bold=True)  # Bright white
        sys.stdout.write(self.chars['filled_large'])
        self.reset_color()
        
        # Inner decorative pattern - sparkles
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = int(self.center_x + 1 * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + 1 * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(36, bold=True)  # Bright cyan
                sys.stdout.write(self.chars['star_sparkle'] if 'star_sparkle' in self.chars else self.chars['star'])
                self.reset_color()
        
        # Innermost pattern - small dots
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            x = int(self.center_x + 0.5 * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + 0.5 * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(33, bold=True)  # Bright yellow
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
    
    def _draw_ornate_border(self):
        """Draw extremely ornate outer border with multiple decorative layers."""
        # Outer border with stars
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = int(self.center_x + (self.radius + 7) * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + (self.radius + 7) * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(35, bold=True)  # Bright magenta
                sys.stdout.write(self.chars['star'])
                self.reset_color()
        
        # Second border layer with diamonds
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            x = int(self.center_x + (self.radius + 5) * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + (self.radius + 5) * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(36)  # Cyan
                sys.stdout.write(self.chars['diamond_outline'])
                self.reset_color()
    
    def _draw_second_marks(self):
        """Draw additional second marks for extra detail."""
        for second in range(0, 60, 5):
            if second % 5 != 0:  # Skip if already drawn as minute mark
                angle = math.radians((second * 6) - 90)
                x = int(self.center_x + (self.radius - 0.5) * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + (self.radius - 0.5) * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(90)  # Gray
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_hour_decorations(self):
        """Draw additional decorative elements around hour markers."""
        for hour in range(1, 13):
            angle = math.radians((hour * 30) - 90)
            
            # Draw decorative brackets around hour numbers
            for offset_angle in [-5, 5]:
                deco_angle = angle + math.radians(offset_angle)
                deco_radius = self.radius + 4
                x = int(self.center_x + deco_radius * self.aspect_ratio * math.cos(deco_angle))
                y = int(self.center_y + deco_radius * math.sin(deco_angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(33)  # Yellow
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_cardinal_rings(self):
        """Draw decorative rings around cardinal points."""
        for angle_deg in [0, 90, 180, 270]:
            angle = math.radians(angle_deg - 90)
            center_x = int(self.center_x + (self.radius + 5) * self.aspect_ratio * math.cos(angle))
            center_y = int(self.center_y + (self.radius + 5) * math.sin(angle))
            
            # Draw small ring around each cardinal point
            for ring_angle in range(0, 360, 30):
                ring_rad = math.radians(ring_angle)
                x = int(center_x + 2 * self.aspect_ratio * math.cos(ring_rad))
                y = int(center_y + 2 * math.sin(ring_rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_inter_hour_patterns(self):
        """Draw ornate patterns between hour markers."""
        for hour in range(1, 13):
            # Angle halfway between this hour and next
            mid_angle = math.radians(((hour * 30 + (hour % 12 + 1) * 30) / 2) - 90)
            
            # Draw decorative pattern
            for i in range(3):
                pattern_radius = self.radius - 1 + i * 0.5
                x = int(self.center_x + pattern_radius * self.aspect_ratio * math.cos(mid_angle))
                y = int(self.center_y + pattern_radius * math.sin(mid_angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(37)  # White
                    sys.stdout.write(self.chars['medium_dot'])
                    self.reset_color()
    
    def _draw_radial_decorations(self):
        """Draw radial decorative lines from center."""
        for angle_deg in range(0, 360, 30):
            angle = math.radians(angle_deg - 90)
            # Draw radial line segments
            for radius in range(2, self.radius - 3, 2):
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(90)  # Gray
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_hand_shadows(self, hour_angle: float, minute_angle: float, second_angle: float):
        """Draw EXTENSIVE shadows/outlines behind clock hands for maximum depth and clarity."""
        # Draw comprehensive shadow for hour hand
        hour_length = self.radius * 0.5
        shadow_offset = 0.1
        for i in range(int(hour_length * 0.8)):
            t = i / (hour_length * 0.8)
            shadow_angle = hour_angle + shadow_offset
            shadow_x = int(self.center_x + t * hour_length * self.aspect_ratio * math.cos(shadow_angle))
            shadow_y = int(self.center_y + t * hour_length * math.sin(shadow_angle))
            if 1 <= shadow_x <= self.width and 1 <= shadow_y <= self.height:
                self.move_cursor(shadow_x, shadow_y)
                self.set_color(90)  # Dark gray shadow
                sys.stdout.write(self.chars['filled'])
                self.reset_color()
        
        # Draw comprehensive shadow for minute hand
        minute_length = self.radius * 0.75
        for i in range(int(minute_length * 0.9)):
            t = i / (minute_length * 0.9)
            shadow_angle = minute_angle + shadow_offset
            shadow_x = int(self.center_x + t * minute_length * self.aspect_ratio * math.cos(shadow_angle))
            shadow_y = int(self.center_y + t * minute_length * math.sin(shadow_angle))
            if 1 <= shadow_x <= self.width and 1 <= shadow_y <= self.height:
                self.move_cursor(shadow_x, shadow_y)
                self.set_color(90)  # Dark gray shadow
                sys.stdout.write(self.chars['filled'])
                self.reset_color()
        
        # Draw comprehensive shadow for second hand
        second_length = self.radius * 0.9
        for i in range(int(second_length)):
            t = i / second_length
            shadow_angle = second_angle + shadow_offset
            shadow_x = int(self.center_x + t * second_length * self.aspect_ratio * math.cos(shadow_angle))
            shadow_y = int(self.center_y + t * second_length * math.sin(shadow_angle))
            if 1 <= shadow_x <= self.width and 1 <= shadow_y <= self.height:
                self.move_cursor(shadow_x, shadow_y)
                self.set_color(90)  # Dark gray shadow
                sys.stdout.write(self.chars['filled'])
                self.reset_color()
    
    def _draw_hand_highlights(self, hour_angle: float, minute_angle: float, second_angle: float):
        """Draw bright highlights on clock hands for maximum visibility."""
        # Draw bright highlight line down center of hour hand
        hour_length = self.radius * 0.5
        for i in range(int(hour_length * 0.8)):
            t = i / (hour_length * 0.8)
            highlight_x = int(self.center_x + t * hour_length * self.aspect_ratio * math.cos(hour_angle))
            highlight_y = int(self.center_y + t * hour_length * math.sin(hour_angle))
            if 1 <= highlight_x <= self.width and 1 <= highlight_y <= self.height:
                self.move_cursor(highlight_x, highlight_y)
                self.set_color(37, bold=True)  # Bright white highlight
                sys.stdout.write(self.chars['filled'])
                self.reset_color()
        
        # Draw bright highlight line down center of minute hand
        minute_length = self.radius * 0.75
        for i in range(int(minute_length * 0.9)):
            t = i / (minute_length * 0.9)
            highlight_x = int(self.center_x + t * minute_length * self.aspect_ratio * math.cos(minute_angle))
            highlight_y = int(self.center_y + t * minute_length * math.sin(minute_angle))
            if 1 <= highlight_x <= self.width and 1 <= highlight_y <= self.height:
                self.move_cursor(highlight_x, highlight_y)
                self.set_color(37, bold=True)  # Bright white highlight
                sys.stdout.write(self.chars['filled'])
                self.reset_color()
        
        # Draw bright highlight line down center of second hand
        second_length = self.radius * 0.9
        for i in range(int(second_length)):
            t = i / second_length
            highlight_x = int(self.center_x + t * second_length * self.aspect_ratio * math.cos(second_angle))
            highlight_y = int(self.center_y + t * second_length * math.sin(second_angle))
            if 1 <= highlight_x <= self.width and 1 <= highlight_y <= self.height:
                self.move_cursor(highlight_x, highlight_y)
                self.set_color(37, bold=True)  # Bright white highlight
                sys.stdout.write(self.chars['filled'])
                self.reset_color()
    
    def _draw_center_rings(self):
        """Draw additional decorative rings around center hub."""
        # Multiple concentric rings
        for ring_radius in [3, 4, 5]:
            for angle in range(0, 360, 10):
                rad = math.radians(angle)
                x = int(self.center_x + ring_radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + ring_radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(35)  # Magenta
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_spiral_pattern(self):
        """Draw spiral decorative pattern."""
        for turn in range(0, 3):
            for step in range(0, 360, 5):
                angle = math.radians(step + turn * 120)
                radius = 4 + step / 60
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height and radius < self.radius - 2:
                    self.move_cursor(x, y)
                    self.set_color(33)  # Yellow
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_geometric_pattern(self):
        """Draw complex geometric patterns."""
        # Hexagonal pattern
        for side in range(6):
            angle = math.radians(side * 60 - 90)
            for i in range(1, self.radius - 2):
                x = int(self.center_x + i * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + i * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_corner_ornaments(self):
        """Draw ornate decorations in corners of clock area."""
        corners = [
            (self.center_x - self.radius * self.aspect_ratio - 3, self.center_y - self.radius - 3),
            (self.center_x + self.radius * self.aspect_ratio + 3, self.center_y - self.radius - 3),
            (self.center_x - self.radius * self.aspect_ratio - 3, self.center_y + self.radius + 3),
            (self.center_x + self.radius * self.aspect_ratio + 3, self.center_y + self.radius + 3),
        ]
        
        for cx, cy in corners:
            # Draw decorative pattern around corner
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x = int(cx + 2 * self.aspect_ratio * math.cos(rad))
                y = int(cy + 2 * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(35)  # Magenta
                    sys.stdout.write(self.chars['star'])
                    self.reset_color()
    
    def _draw_ornamental_fill(self):
        """Draw additional ornamental fill patterns throughout."""
        # Fill with small decorative elements
        for angle_deg in range(0, 360, 20):
            angle = math.radians(angle_deg - 90)
            for radius_offset in [1, 2, 3]:
                radius = self.radius - 6 + radius_offset
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(90)  # Gray
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
        
        # Additional sparkle effects
        for i in range(20):
            angle = math.radians(i * 18 - 90)
            radius = self.radius - 4 + (i % 3)
            x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
            y = int(self.center_y + radius * math.sin(angle))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(33, bold=True)  # Bright yellow
                sys.stdout.write(self.chars['sparkle'] if 'sparkle' in self.chars else self.chars['star'])
                self.reset_color()
    
    def _draw_inner_pattern(self):
        """Draw decorative inner pattern, accounting for aspect ratio."""
        # Spiral or radial pattern - multiply X by aspect ratio
        for radius in range(3, self.radius - 5, 2):
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(90)  # Bright black (gray)
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_metallic_effects(self):
        """Draw metallic/shiny effects throughout clock."""
        # Metallic highlights at various angles
        for highlight_angle in range(0, 360, 30):
            angle = math.radians(highlight_angle - 90)
            for radius_offset in range(2, self.radius - 2, 3):
                x = int(self.center_x + radius_offset * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius_offset * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(37, bold=True)  # Bright white for metallic effect
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_shadow_layers(self):
        """Draw multiple shadow layers for depth."""
        # Shadow layer 1 - outer shadows
        for angle in range(0, 360, 5):
            rad = math.radians(angle - 90)
            x = int(self.center_x + (self.radius + 1) * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + (self.radius + 1) * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(90)  # Gray shadow
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
        
        # Shadow layer 2 - inner shadows
        for angle in range(0, 360, 10):
            rad = math.radians(angle - 90)
            x = int(self.center_x + (self.radius - 3) * self.aspect_ratio * math.cos(rad))
            y = int(self.center_y + (self.radius - 3) * math.sin(rad))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(90)  # Gray shadow
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
    
    def _draw_ornate_filigree(self):
        """Draw ornate filigree patterns."""
        # Complex filigree between elements
        for base_angle in range(0, 360, 15):
            angle = math.radians(base_angle - 90)
            # Draw filigree branches
            for branch in range(3):
                branch_angle = angle + math.radians(branch * 5 - 5)
                for length in range(2, 4):
                    x = int(self.center_x + (self.radius - length) * self.aspect_ratio * math.cos(branch_angle))
                    y = int(self.center_y + (self.radius - length) * math.sin(branch_angle))
                    if 1 <= x <= self.width and 1 <= y <= self.height:
                        self.move_cursor(x, y)
                        self.set_color(33)  # Yellow
                        sys.stdout.write(self.chars['small_dot'])
                        self.reset_color()
    
    def _draw_complex_border_patterns(self):
        """Draw extremely complex border patterns."""
        # Multiple border pattern layers
        for border_layer in range(3):
            radius_offset = self.radius + 8 + border_layer
            step = 8 - border_layer * 2
            color = 35 + border_layer  # Varying colors
            
            for angle in range(0, 360, step):
                rad = math.radians(angle - 90)
                x = int(self.center_x + radius_offset * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + radius_offset * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(color % 8, bold=(border_layer == 0))
                    if border_layer == 0:
                        sys.stdout.write(self.chars['star'])
                    elif border_layer == 1:
                        sys.stdout.write(self.chars['diamond'])
                    else:
                        sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_layered_decorations(self):
        """Draw multiple layered decorative elements."""
        # Layer decorations at different depths
        for layer in range(5):
            layer_radius = self.radius - 6 + layer
            layer_step = 12 - layer * 2
            
            for angle in range(0, 360, layer_step):
                rad = math.radians(angle - 90)
                x = int(self.center_x + layer_radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + layer_radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    color = 33 + (layer % 4)  # Rotate colors
                    self.set_color(color)
                    chars_list = [self.chars['small_dot'], self.chars['medium_dot'], 
                                 self.chars['star'], self.chars['diamond']]
                    sys.stdout.write(chars_list[layer % len(chars_list)])
                    self.reset_color()
    
    def _draw_geometric_overlays(self):
        """Draw geometric pattern overlays."""
        # Overlay geometric shapes
        for shape_type in range(3):
            shape_angle_offset = shape_type * 120
            for point in range(6):
                angle = math.radians(point * 60 + shape_angle_offset - 90)
                radius = self.radius - 3 + shape_type
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan
                    sys.stdout.write(self.chars['square'] if shape_type % 2 == 0 else self.chars['diamond'])
                    self.reset_color()
    
    def _draw_radial_sweeps(self):
        """Draw radial sweep decorative patterns."""
        # Radial sweep lines
        for sweep_angle in range(0, 360, 20):
            angle = math.radians(sweep_angle - 90)
            for radius in range(4, self.radius - 2, 2):
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(90)  # Gray
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_concentric_ornaments(self):
        """Draw concentric ornamental rings."""
        # Multiple concentric ornamental rings
        for ring_num in range(8):
            ring_radius = 2 + ring_num * 1.5
            if ring_radius >= self.radius - 2:
                break
            
            for angle in range(0, 360, 8):
                rad = math.radians(angle - 90)
                x = int(self.center_x + ring_radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + ring_radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    # Alternate colors and characters
                    if ring_num % 2 == 0:
                        self.set_color(35)  # Magenta
                        char = self.chars['small_dot']
                    else:
                        self.set_color(33)  # Yellow
                        char = self.chars['medium_dot']
                    sys.stdout.write(char)
                    self.reset_color()
    
    def _draw_mandala_patterns(self):
        """Draw mandala-style radial patterns."""
        # Complex mandala with multiple layers
        for layer in range(4):
            for petal in range(8):
                base_angle = math.radians(petal * 45 - 90)
                for segment in range(3):
                    angle = base_angle + math.radians(segment * 5 - 5)
                    radius = self.radius - 5 + layer * 2
                    x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                    y = int(self.center_y + radius * math.sin(angle))
                    if 1 <= x <= self.width and 1 <= y <= self.height:
                        self.move_cursor(x, y)
                        self.set_color(35 + layer)  # Varying colors
                        sys.stdout.write(self.chars['star'] if segment == 1 else self.chars['small_dot'])
                        self.reset_color()
    
    def _draw_celtic_knots(self):
        """Draw Celtic knot-style interwoven patterns."""
        # Simplified Celtic knot pattern
        for knot_angle in range(0, 360, 30):
            angle = math.radians(knot_angle - 90)
            for offset in [-2, 0, 2]:
                knot_radius = self.radius - 4
                x = int(self.center_x + (knot_radius + offset) * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + (knot_radius + offset) * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(32)  # Green
                    sys.stdout.write(self.chars['diamond'])
                    self.reset_color()
    
    def _draw_arabesque_patterns(self):
        """Draw arabesque-style flowing patterns."""
        # Flowing arabesque curves
        for curve_start in range(0, 360, 45):
            for point in range(5):
                angle = math.radians(curve_start + point * 8 - 90)
                radius = self.radius - 2 + point
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_baroque_ornaments(self):
        """Draw baroque-style ornate decorations."""
        # Baroque scrolls and flourishes
        for scroll_pos in range(0, 360, 60):
            angle = math.radians(scroll_pos - 90)
            for flourish in range(4):
                flourish_angle = angle + math.radians(flourish * 3 - 6)
                radius = self.radius - 1
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(flourish_angle))
                y = int(self.center_y + radius * math.sin(flourish_angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(33, bold=True)  # Bright yellow
                    sys.stdout.write(self.chars['star_filled'])
                    self.reset_color()
    
    def _draw_rosette_patterns(self):
        """Draw rosette decorative patterns."""
        # Multiple rosettes around the clock
        for rosette_num in range(6):
            rosette_angle = math.radians(rosette_num * 60 - 90)
            rosette_center_x = int(self.center_x + (self.radius - 3) * self.aspect_ratio * math.cos(rosette_angle))
            rosette_center_y = int(self.center_y + (self.radius - 3) * math.sin(rosette_angle))
            
            # Draw rosette petals
            for petal in range(6):
                petal_angle = rosette_angle + math.radians(petal * 60)
                x = int(rosette_center_x + 1.5 * self.aspect_ratio * math.cos(petal_angle))
                y = int(rosette_center_y + 1.5 * math.sin(petal_angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(35)  # Magenta
                    sys.stdout.write(self.chars['star'])
                    self.reset_color()
    
    def _draw_guilloche_patterns(self):
        """Draw guilloche (engine-turned) patterns."""
        # Complex interwoven guilloche
        for wave in range(3):
            for angle_deg in range(0, 360, 2):
                angle = math.radians(angle_deg - 90)
                # Wave pattern
                radius = self.radius - 3 + math.sin(angle * 3 + wave * 2) * 1.5
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(90)  # Gray
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_heraldic_elements(self):
        """Draw heraldic-style decorative elements."""
        # Heraldic symbols at cardinal and ordinal points
        heraldic_positions = [0, 45, 90, 135, 180, 225, 270, 315]
        symbols = [self.chars['star'], self.chars['diamond'], self.chars['square'], 
                  self.chars['triangle'], self.chars['circle'], self.chars['star_filled'],
                  self.chars['diamond'], self.chars['square']]
        
        for i, pos in enumerate(heraldic_positions):
            angle = math.radians(pos - 90)
            x = int(self.center_x + (self.radius - 2) * self.aspect_ratio * math.cos(angle))
            y = int(self.center_y + (self.radius - 2) * math.sin(angle))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(31 + (i % 6))  # Varying colors
                sys.stdout.write(symbols[i % len(symbols)])
                self.reset_color()
    
    def _draw_astronomical_symbols(self):
        """Draw astronomical symbols around clock."""
        # Astronomical symbols
        symbols = ['☀', '☾', '★', '✦']  # Sun, moon, star, sparkle
        for i, symbol in enumerate(symbols):
            angle = math.radians(i * 90 - 90)
            x = int(self.center_x + (self.radius + 6) * self.aspect_ratio * math.cos(angle))
            y = int(self.center_y + (self.radius + 6) * math.sin(angle))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(33, bold=True)  # Bright yellow
                sys.stdout.write(symbol)
                self.reset_color()
    
    def _draw_alchemical_symbols(self):
        """Draw alchemical-style symbols."""
        # Alchemical circle patterns
        for circle_layer in range(3):
            radius = 5 + circle_layer
            for angle in range(0, 360, 12):
                rad = math.radians(angle - 90)
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(35)  # Magenta
                    sys.stdout.write(self.chars['circle'] if circle_layer % 2 == 0 else self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_mathematical_patterns(self):
        """Draw mathematical pattern overlays."""
        # Fibonacci spiral approximation
        phi = 1.618
        for turn in range(8):
            for step in range(0, 90, 5):
                angle = math.radians(step + turn * 90 - 90)
                radius = 2 * phi ** (turn / 4)
                if radius < self.radius - 2:
                    x = int(self.center_x + radius * self.aspect_ratio * math.cos(angle))
                    y = int(self.center_y + radius * math.sin(angle))
                    if 1 <= x <= self.width and 1 <= y <= self.height:
                        self.move_cursor(x, y)
                        self.set_color(90)  # Gray
                        sys.stdout.write(self.chars['small_dot'])
                        self.reset_color()
    
    def _draw_fractal_elements(self):
        """Draw fractal-like recursive patterns."""
        # Simplified fractal branches
        def draw_branch(cx, cy, angle, length, depth):
            if depth <= 0 or length < 1:
                return
            end_x = int(cx + length * self.aspect_ratio * math.cos(angle))
            end_y = int(cy + length * math.sin(angle))
            if 1 <= end_x <= self.width and 1 <= end_y <= self.height:
                self.move_cursor(end_x, end_y)
                self.set_color(36)  # Cyan
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
            # Recursive branches
            if depth > 0:
                draw_branch(end_x, end_y, angle + math.radians(30), length * 0.6, depth - 1)
                draw_branch(end_x, end_y, angle - math.radians(30), length * 0.6, depth - 1)
        
        # Draw fractal branches from center
        for start_angle in range(0, 360, 60):
            draw_branch(self.center_x, self.center_y, math.radians(start_angle - 90), 3, 2)
    
    def _draw_space_age_background(self):
        """Fill ENTIRE screen with space-age background to eliminate ALL black spaces."""
        # Fill EVERY pixel of the screen with space background
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                self.move_cursor(x, y)
                # Calculate distance from center
                dist_from_center = math.sqrt(((x - self.center_x) / self.aspect_ratio) ** 2 + (y - self.center_y) ** 2)
                
                if dist_from_center > self.radius + 8:  # Outside clock area - fill with space
                    # Space background with stars and nebula
                    if (x + y + second) % 11 == 0:  # Twinkling stars
                        self.set_color(37, bold=True)  # Bright white stars
                        sys.stdout.write(self.chars['star'])
                    elif (x + y) % 13 == 0:  # Medium stars
                        self.set_color(37)  # White stars
                        sys.stdout.write(self.chars['small_dot'])
                    elif (x + y) % 17 == 0:  # Dim stars
                        self.set_color(90)  # Gray stars
                        sys.stdout.write(self.chars['small_dot'])
                    else:
                        # Deep space background
                        self.set_color(90)  # Dark space
                        sys.stdout.write(' ')
                else:
                    # Inside clock area - subtle space background
                    if (x + y) % 23 == 0:  # Very sparse stars inside
                        self.set_color(90)  # Very dim
                        sys.stdout.write(self.chars['small_dot'])
                    else:
                        # Transparent (will be overwritten by clock elements)
                        self.set_color(90)
                        sys.stdout.write(' ')
                self.reset_color()
    
    def _draw_orbital_rings(self):
        """Draw orbital rings around clock like planets."""
        for ring_num in range(3):
            orbit_radius = self.radius + 8 + ring_num * 3
            for angle in range(0, 360, 5):
                rad = math.radians(angle - 90)
                x = int(self.center_x + orbit_radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + orbit_radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan orbit
                    sys.stdout.write(self.chars['orbit'])
                    self.reset_color()
            
            # Draw planet on orbit
            planet_angle = math.radians((second * 6 + ring_num * 120) - 90)
            planet_x = int(self.center_x + orbit_radius * self.aspect_ratio * math.cos(planet_angle))
            planet_y = int(self.center_y + orbit_radius * math.sin(planet_angle))
            if 1 <= planet_x <= self.width and 1 <= planet_y <= self.height:
                self.move_cursor(planet_x, planet_y)
                self.set_color(33, bold=True)  # Bright yellow planet
                sys.stdout.write(self.chars['planet'])
                self.reset_color()
    
    def _draw_starfield(self):
        """Draw starfield background."""
        import random
        random.seed(42)  # Deterministic stars
        for _ in range(100):
            star_x = random.randint(1, self.width)
            star_y = random.randint(1, self.height)
            dist_from_center = math.sqrt(((star_x - self.center_x) / self.aspect_ratio) ** 2 + (star_y - self.center_y) ** 2)
            if dist_from_center > self.radius + 5:  # Outside clock
                self.move_cursor(star_x, star_y)
                brightness = random.choice([37, 37, 90])  # Mostly bright stars
                self.set_color(brightness, bold=(brightness == 37))
                sys.stdout.write(self.chars['star'] if brightness == 37 else self.chars['small_dot'])
                self.reset_color()
    
    def _draw_planet_orbits(self):
        """Draw multiple planet orbits."""
        for orbit in range(4):
            orbit_radius = self.radius + 6 + orbit * 2
            for angle in range(0, 360, 3):
                rad = math.radians(angle - 90)
                x = int(self.center_x + orbit_radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + orbit_radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(35)  # Magenta orbit
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_satellite_traces(self):
        """Draw satellite movement traces."""
        for sat in range(3):
            trace_angle = math.radians((second * 6 + sat * 120) - 90)
            trace_radius = self.radius + 10
            for offset in range(-3, 4):
                angle = trace_angle + math.radians(offset * 2)
                x = int(self.center_x + trace_radius * self.aspect_ratio * math.cos(angle))
                y = int(self.center_y + trace_radius * math.sin(angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(32)  # Green trace
                    sys.stdout.write(self.chars['small_dot'])
                    self.reset_color()
    
    def _draw_energy_grid(self):
        """Draw futuristic energy grid."""
        # Horizontal grid lines
        for y in range(2, self.height, 4):
            for x in range(1, self.width + 1):
                dist_from_center = math.sqrt(((x - self.center_x) / self.aspect_ratio) ** 2 + (y - self.center_y) ** 2)
                if dist_from_center > self.radius + 3:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan grid
                    sys.stdout.write(self.chars['scan'])
                    self.reset_color()
        
        # Vertical grid lines
        for x in range(5, self.width, 10):
            for y in range(1, self.height + 1):
                dist_from_center = math.sqrt(((x - self.center_x) / self.aspect_ratio) ** 2 + (y - self.center_y) ** 2)
                if dist_from_center > self.radius + 3:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan grid
                    sys.stdout.write(self.chars['beam'])
                    self.reset_color()
    
    def _draw_holographic_effects(self):
        """Draw holographic shimmer effects."""
        for angle in range(0, 360, 15):
            rad = math.radians(angle - 90)
            for radius_offset in range(2, 5):
                radius = self.radius + radius_offset
                x = int(self.center_x + radius * self.aspect_ratio * math.cos(rad))
                y = int(self.center_y + radius * math.sin(rad))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(36, bold=True)  # Bright cyan hologram
                    sys.stdout.write(self.chars['hologram'])
                    self.reset_color()
    
    def _draw_radar_sweeps(self):
        """Draw radar sweep effects."""
        sweep_angle = math.radians((second * 6) - 90)
        for radius in range(3, self.radius + 5):
            x = int(self.center_x + radius * self.aspect_ratio * math.cos(sweep_angle))
            y = int(self.center_y + radius * math.sin(sweep_angle))
            if 1 <= x <= self.width and 1 <= y <= self.height:
                self.move_cursor(x, y)
                self.set_color(32, bold=True)  # Bright green radar
                sys.stdout.write(self.chars['radar'])
                self.reset_color()
    
    def _draw_circuit_patterns(self):
        """Draw circuit board patterns."""
        for circuit_y in range(3, self.height - 2, 5):
            for circuit_x in range(5, self.width - 4, 8):
                dist_from_center = math.sqrt(((circuit_x - self.center_x) / self.aspect_ratio) ** 2 + (circuit_y - self.center_y) ** 2)
                if dist_from_center > self.radius + 2:
                    self.move_cursor(circuit_x, circuit_y)
                    self.set_color(33)  # Yellow circuit
                    sys.stdout.write(self.chars['circuit'])
                    self.reset_color()
    
    def _draw_nebula_clouds(self):
        """Draw nebula cloud effects."""
        for cloud in range(5):
            cloud_angle = math.radians(cloud * 72 - 90)
            cloud_radius = self.radius + 12
            cloud_x = int(self.center_x + cloud_radius * self.aspect_ratio * math.cos(cloud_angle))
            cloud_y = int(self.center_y + cloud_radius * math.sin(cloud_angle))
            for offset in range(-2, 3):
                for offset2 in range(-2, 3):
                    x = cloud_x + offset
                    y = cloud_y + offset2
                    if 1 <= x <= self.width and 1 <= y <= self.height:
                        self.move_cursor(x, y)
                        self.set_color(35)  # Magenta nebula
                        sys.stdout.write(self.chars['nebula'])
                        self.reset_color()
    
    def _draw_pulsar_beams(self):
        """Draw pulsar beam effects."""
        for pulsar in range(4):
            pulsar_angle = math.radians(pulsar * 90 - 90)
            for beam_length in range(5, 15):
                x = int(self.center_x + (self.radius + beam_length) * self.aspect_ratio * math.cos(pulsar_angle))
                y = int(self.center_y + (self.radius + beam_length) * math.sin(pulsar_angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(33, bold=True)  # Bright yellow pulsar
                    sys.stdout.write(self.chars['pulsar'])
                    self.reset_color()
    
    def _draw_wormhole_effects(self):
        """Draw wormhole/portal effects."""
        for portal in range(2):
            portal_angle = math.radians(portal * 180 - 90)
            portal_radius = self.radius + 15
            portal_x = int(self.center_x + portal_radius * self.aspect_ratio * math.cos(portal_angle))
            portal_y = int(self.center_y + portal_radius * math.sin(portal_angle))
            for ring in range(3):
                for angle in range(0, 360, 10):
                    rad = math.radians(angle)
                    x = int(portal_x + ring * self.aspect_ratio * math.cos(rad))
                    y = int(portal_y + ring * math.sin(rad))
                    if 1 <= x <= self.width and 1 <= y <= self.height:
                        self.move_cursor(x, y)
                        self.set_color(35, bold=True)  # Bright magenta wormhole
                        sys.stdout.write(self.chars['wormhole'])
                        self.reset_color()
    
    def _draw_quantum_fields(self):
        """Draw quantum field effects."""
        for field in range(6):
            field_angle = math.radians(field * 60 - 90)
            field_radius = self.radius + 7
            for wave in range(3):
                wave_radius = field_radius + wave
                x = int(self.center_x + wave_radius * self.aspect_ratio * math.cos(field_angle))
                y = int(self.center_y + wave_radius * math.sin(field_angle))
                if 1 <= x <= self.width and 1 <= y <= self.height:
                    self.move_cursor(x, y)
                    self.set_color(36)  # Cyan quantum field
                    sys.stdout.write(self.chars['energy'])
                    self.reset_color()
    
    def render_corner_time(self, location_info: Dict, corner: str):
        """Display EXTREMELY enhanced time information in corner with ornate decorations."""
        if not location_info:
            return
        
        # Determine corner coordinates - larger box for more info
        box_width = 26
        box_height = 5
        
        if corner == 'top_left':
            x, y = 1, 1
        elif corner == 'top_right':
            x, y = self.width - box_width + 1, 1
        elif corner == 'bottom_left':
            x, y = 1, self.height - box_height + 1
        elif corner == 'bottom_right':
            x, y = self.width - box_width + 1, self.height - box_height + 1
        else:
            return
        
        # Draw EXTREMELY ornate corner box with multiple decorative layers
        self._draw_ultra_ornate_corner_box(x, y, box_width, box_height)
        
        # Write location name (bold, colored) with decorative prefix
        self.move_cursor(x + 2, y + 1)
        self.set_color(32, bold=True)  # Green, bold
        name = location_info.get('name', 'N/A')
        sys.stdout.write(f" {self.chars['star']} {name} {self.chars['star']} ".ljust(box_width - 3))
        self.reset_color()
        
        # Write city name with decorative elements
        self.move_cursor(x + 2, y + 2)
        self.set_color(36)  # Cyan
        city = location_info.get('city', '')
        sys.stdout.write(f" {self.chars['diamond_outline']} {city[:20]} ".ljust(box_width - 3))
        self.reset_color()
        
        # Write time (large, bold) with decorative borders
        self.move_cursor(x + 2, y + 3)
        self.set_color(37, bold=True)  # White, bold
        time_str = location_info.get('time', 'N/A')
        offset_str = location_info.get('utc_offset', '')
        display_time = f" {self.chars['arrow_right']} {time_str} {offset_str} {self.chars['arrow_left']} ".ljust(box_width - 3)
        sys.stdout.write(display_time)
        self.reset_color()
        
        # Write date if available
        self.move_cursor(x + 2, y + 4)
        self.set_color(33)  # Yellow
        date_str = location_info.get('date', '')
        if date_str:
            display_date = f" {self.chars['circle']} {date_str} {self.chars['circle']} ".ljust(box_width - 3)
        else:
            display_date = " " * (box_width - 3)
        sys.stdout.write(display_date)
        self.reset_color()
        
        sys.stdout.flush()
    
    def _draw_ultra_ornate_corner_box(self, x: int, y: int, width: int, height: int):
        """Draw EXTREMELY ornate box with multiple decorative layers."""
        # Outer border - double line
        self.move_cursor(x, y)
        self.set_color(36, bold=True)  # Bright cyan
        sys.stdout.write(self.chars['corner_tl_double'])
        sys.stdout.write(self.chars['line_h_double'] * (width - 2))
        sys.stdout.write(self.chars['corner_tr_double'])
        
        # Sides with decorative elements
        for i in range(1, height - 1):
            self.move_cursor(x, y + i)
            sys.stdout.write(self.chars['line_v_double'])
            # Decorative side elements
            if i % 2 == 0:
                self.move_cursor(x + 1, y + i)
                self.set_color(35)  # Magenta
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
            self.move_cursor(x + width - 1, y + i)
            self.set_color(36, bold=True)
            sys.stdout.write(self.chars['line_v_double'])
            self.reset_color()
            if i % 2 == 0:
                self.move_cursor(x + width - 2, y + i)
                self.set_color(35)  # Magenta
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
        
        # Bottom border
        self.move_cursor(x, y + height - 1)
        self.set_color(36, bold=True)
        sys.stdout.write(self.chars['corner_bl_double'])
        sys.stdout.write(self.chars['line_h_double'] * (width - 2))
        sys.stdout.write(self.chars['corner_br_double'])
        self.reset_color()
        
        # Decorative corner elements - multiple layers
        corner_decorations = [
            (x + 1, y + 1, self.chars['star'], 35),
            (x + width - 2, y + 1, self.chars['star'], 35),
            (x + 1, y + height - 2, self.chars['star'], 35),
            (x + width - 2, y + height - 2, self.chars['star'], 35),
            (x + 2, y + 1, self.chars['diamond'], 36),
            (x + width - 3, y + 1, self.chars['diamond'], 36),
            (x + 2, y + height - 2, self.chars['diamond'], 36),
            (x + width - 3, y + height - 2, self.chars['diamond'], 36),
        ]
        
        for deco_x, deco_y, char, color in corner_decorations:
            if 1 <= deco_x <= self.width and 1 <= deco_y <= self.height:
                self.move_cursor(deco_x, deco_y)
                self.set_color(color)
                sys.stdout.write(char)
                self.reset_color()
        
        # Additional decorative border elements
        for i in range(2, width - 2, 3):
            # Top decorative elements
            if 1 <= x + i <= self.width and 1 <= y <= self.height:
                self.move_cursor(x + i, y)
                self.set_color(33)  # Yellow
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
            # Bottom decorative elements
            if 1 <= x + i <= self.width and 1 <= y + height - 1 <= self.height:
                self.move_cursor(x + i, y + height - 1)
                self.set_color(33)  # Yellow
                sys.stdout.write(self.chars['small_dot'])
                self.reset_color()
    
    def update_display(self, current_time: datetime, corner_times: Dict[str, Dict]):
        """Update entire display with complex clock face."""
        self.clear_screen()
        
        # Render complex main clock face
        self.render_clock_face(
            current_time.hour,
            current_time.minute,
            current_time.second
        )
        
        # Render enhanced corner times
        for corner, time_info in corner_times.items():
            self.render_corner_time(time_info, corner)
        
        # Display EXTREMELY ornate UTC time at bottom center
        self.move_cursor(self.center_x - 12, self.height - 2)
        self.set_color(35, bold=True)  # Bright magenta
        utc_str = current_time.strftime(" ═══ UTC: %H:%M:%S ═══ ")
        sys.stdout.write(utc_str)
        self.reset_color()
        
        # Display ornate date above UTC time
        self.move_cursor(self.center_x - 12, self.height - 3)
        self.set_color(33, bold=True)  # Bright yellow
        date_str = current_time.strftime(" ★ %Y-%m-%d ★ ")
        sys.stdout.write(date_str)
        self.reset_color()
        
        # Additional decorative elements around UTC display
        for offset in [-14, 14]:
            x = self.center_x + offset
            if 1 <= x <= self.width and 1 <= self.height - 2 <= self.height:
                self.move_cursor(x, self.height - 2)
                self.set_color(36, bold=True)  # Bright cyan
                sys.stdout.write(self.chars['star'])
                self.reset_color()
        
        # Decorative line above date
        self.move_cursor(self.center_x - 12, self.height - 4)
        self.set_color(36)  # Cyan
        sys.stdout.write(self.chars['line_h_double'] * 24)
        self.reset_color()
        
        sys.stdout.flush()


def get_terminal_size() -> Tuple[int, int]:
    """Get current terminal size."""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except:
        return 80, 24


if __name__ == '__main__':
    # Test complex clock renderer
    print("Testing complex clock renderer...")
    
    width, height = get_terminal_size()
    renderer = ClockRenderer(width, height)
    
    # Test with current time
    now = datetime.now()
    corner_times = {
        'top_left': {'name': 'NIST', 'city': 'Boulder, CO', 'time': '14:30:45', 'utc_offset': '-07:00'},
        'top_right': {'name': 'PTB', 'city': 'Braunschweig', 'time': '23:30:45', 'utc_offset': '+01:00'},
        'bottom_left': {'name': 'NPL', 'city': 'London, UK', 'time': '22:30:45', 'utc_offset': '+00:00'},
        'bottom_right': {'name': 'NICT', 'city': 'Tokyo, Japan', 'time': '07:30:45', 'utc_offset': '+09:00'},
    }
    
    renderer.update_display(now, corner_times)
    
    print("\nPress Enter to exit...")
    input()
