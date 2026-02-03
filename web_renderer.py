#!/usr/bin/env python3
"""
Web-based Renderer for Atomic Clock Display

Provides a web interface using Flask.
"""

import json
import threading
from datetime import datetime
from typing import Dict, Tuple, Optional
from flask import Flask, render_template_string, jsonify
from renderer_interface import ClockRenderer, register_renderer


@register_renderer("web")
class WebRenderer(ClockRenderer):
    """Web-based renderer using Flask."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.width = 800
        self.height = 600
        self.current_time = None
        self.corner_times = {}
        self.showing_help = False
        self.server_thread = None
        self.running = False
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template_string(self._get_html_template())
        
        @self.app.route('/api/time')
        def get_time():
            """API endpoint to get current time data."""
            data = {
                'current_time': self.current_time.isoformat() if self.current_time else None,
                'corner_times': self.corner_times,
                'showing_help': self.showing_help
            }
            return jsonify(data)
        
        @self.app.route('/api/help')
        def toggle_help():
            """Toggle help overlay."""
            self.showing_help = not self.showing_help
            return jsonify({'showing_help': self.showing_help})
    
    def _get_html_template(self) -> str:
        """Get HTML template for the web interface."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Atomic Clock Display</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0ff;
            overflow: hidden;
        }
        
        .container {
            width: 100vw;
            height: 100vh;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .main-clock {
            text-align: center;
        }
        
        .time {
            font-size: 4rem;
            font-weight: bold;
            text-shadow: 0 0 10px #0ff;
        }
        
        .date {
            font-size: 1.5rem;
            margin-top: 0.5rem;
        }
        
        .corner {
            position: absolute;
            font-size: 1.2rem;
        }
        
        .corner.top-left { top: 2rem; left: 2rem; }
        .corner.top-right { top: 2rem; right: 2rem; }
        .corner.bottom-left { bottom: 2rem; left: 2rem; }
        .corner.bottom-right { bottom: 2rem; right: 2rem; }
        
        .corner-name {
            font-weight: bold;
            color: #0f0;
        }
        
        .corner-time {
            margin-top: 0.25rem;
        }
        
        .corner-offset {
            font-size: 0.9rem;
            color: #888;
        }
        
        .help-overlay {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 139, 0.9);
            border: 2px solid #ff0;
            padding: 2rem;
            border-radius: 0.5rem;
            display: none;
        }
        
        .help-overlay.show {
            display: block;
        }
        
        .help-title {
            color: #ff0;
            font-weight: bold;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .help-content {
            line-height: 1.5;
        }
        
        .status-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: #800;
            color: #fff;
            padding: 0.5rem;
            text-align: center;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-clock">
            <div class="time" id="main-time">--:--:--</div>
            <div class="date" id="main-date">----/--/--</div>
        </div>
        
        <div class="corner top-left" id="corner-tl">
            <div class="corner-name">--</div>
            <div class="corner-time">--:--:--</div>
            <div class="corner-offset">UTC--:--</div>
        </div>
        
        <div class="corner top-right" id="corner-tr">
            <div class="corner-name">--</div>
            <div class="corner-time">--:--:--</div>
            <div class="corner-offset">UTC--:--</div>
        </div>
        
        <div class="corner bottom-left" id="corner-bl">
            <div class="corner-name">--</div>
            <div class="corner-time">--:--:--</div>
            <div class="corner-offset">UTC--:--</div>
        </div>
        
        <div class="corner bottom-right" id="corner-br">
            <div class="corner-name">--</div>
            <div class="corner-time">--:--:--</div>
            <div class="corner-offset">UTC--:--</div>
        </div>
        
        <div class="help-overlay" id="help-overlay">
            <div class="help-title">Atomic Clock - Help</div>
            <div class="help-content">
                <div>Commands:</div>
                <div>  h - Toggle this help</div>
                <div>  r - Refresh time sync</div>
                <div>  s - Show sync status</div>
                <div>  Click anywhere to close help</div>
            </div>
        </div>
        
        <div class="status-bar">
            Atomic Clock Display | Press 'h' for help
        </div>
    </div>
    
    <script>
        function updateDisplay() {
            fetch('/api/time')
                .then(response => response.json())
                .then(data => {
                    if (data.current_time) {
                        const time = new Date(data.current_time);
                        document.getElementById('main-time').textContent = 
                            time.toTimeString().split(' ')[0];
                        document.getElementById('main-date').textContent = 
                            time.toISOString().split('T')[0];
                    }
                    
                    // Update corner clocks
                    const corners = ['top-left', 'top-right', 'bottom-left', 'bottom-right'];
                    const cornerIds = ['tl', 'tr', 'bl', 'br'];
                    
                    corners.forEach((corner, index) => {
                        const cornerData = data.corner_times[corner];
                        const element = document.getElementById(`corner-${cornerIds[index]}`);
                        
                        if (cornerData) {
                            element.querySelector('.corner-name').textContent = cornerData.name;
                            element.querySelector('.corner-time').textContent = cornerData.time;
                            element.querySelector('.corner-offset').textContent = `UTC${cornerData.utc_offset}`;
                        }
                    });
                    
                    // Update help overlay
                    const helpOverlay = document.getElementById('help-overlay');
                    if (data.showing_help) {
                        helpOverlay.classList.add('show');
                    } else {
                        helpOverlay.classList.remove('show');
                    }
                })
                .catch(error => console.error('Error updating display:', error));
        }
        
        // Toggle help on click
        document.addEventListener('click', function() {
            fetch('/api/help')
                .then(response => response.json())
                .then(data => {
                    // Help will be updated on next refresh
                });
        });
        
        // Update display every second
        setInterval(updateDisplay, 1000);
        
        // Initial update
        updateDisplay();
    </script>
</body>
</html>
        """
    
    def initialize(self, width: int, height: int) -> bool:
        """Initialize the web server."""
        self.width = width
        self.height = height
        
        try:
            # Start Flask server in a separate thread
            self.server_thread = threading.Thread(
                target=self.app.run,
                kwargs={'host': self.host, 'port': self.port, 'debug': False, 'use_reloader': False},
                daemon=True
            )
            self.server_thread.start()
            self.running = True
            
            print(f"Web renderer started at http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"Failed to start web renderer: {e}")
            return False
    
    def update_display(self, current_time: datetime, corner_times: Dict[str, Dict]) -> None:
        """Update the display data (web interface updates via JS polling)."""
        self.current_time = current_time
        self.corner_times = corner_times
    
    def update_size(self, width: int, height: int) -> None:
        """Update display size."""
        self.width = width
        self.height = height
    
    def cleanup(self) -> None:
        """Cleanup web server resources."""
        self.running = False
        # Flask doesn't provide a clean way to stop the server from within
        # The thread will exit when the main process exits
    
    def handle_keypress(self, key: str) -> bool:
        """Handle keyboard input (not applicable to web renderer)."""
        return False
    
    def show_help(self) -> None:
        """Show help overlay."""
        self.showing_help = True
    
    def hide_help(self) -> None:
        """Hide help overlay."""
        self.showing_help = False
    
    def get_size(self) -> Tuple[int, int]:
        """Get current display size."""
        return (self.width, self.height)
