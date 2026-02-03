# Space-Age Atomic Clock Display Application

A **FUTURISTIC SPACE-AGE** terminal-based atomic clock display application that shows real-time atomic clock times from various locations around the world with stunning sci-fi visual effects. Built using EKI (Enhanced Kitty Installer) and DCP (DSOS Control Plane) technologies.

## Features

### 🚀 Space-Age Visual Design

The clock features a **truly futuristic space-age aesthetic** with:

- **Full-Screen Space Background**: Eliminates all black spaces - entire terminal filled with starfield
- **Orbital Rings**: Multiple planets orbiting around the clock face
- **Starfield**: Twinkling stars throughout the background
- **Satellite Traces**: Moving satellite paths around the clock
- **Energy Grid**: Futuristic grid overlay patterns
- **Holographic Effects**: Shimmering holographic displays
- **Radar Sweeps**: Animated radar scanning effects
- **Circuit Patterns**: Sci-fi circuit board aesthetics
- **Nebula Clouds**: Colorful nebula effects
- **Pulsar Beams**: Bright pulsar energy beams
- **Wormhole Effects**: Portal-like visual effects
- **Quantum Fields**: Advanced quantum field visualizations

### Complex Clock Face Design
- **Multi-layered Design**: Multiple concentric circles with decorative rings
- **Detailed Markers**: 
  - 60 minute/second tick marks
  - Distinctive hour markers (diamonds for cardinal positions, squares for others)
  - Different styles for 12/3/6/9 vs other hours
- **Sophisticated Hands**: 
  - Thick hour hand with diamond tip
  - Medium minute hand with arrow tip
  - Thin second hand with dot tip
- **Decorative Elements**:
  - Cardinal point indicators (N/S/E/W arrows)
  - Decorative center hub with star pattern
  - Inner decorative patterns
  - Enhanced corner displays with double borders

### Core Features
- **Real-time Atomic Clock Display**: Complex circular clock face showing current UTC time
- **Multiple Location Times**: Display times from atomic clock facilities worldwide:
  - NIST (Boulder, CO, USA)
  - PTB (Braunschweig, Germany)
  - NPL (London, UK)
  - NICT (Tokyo, Japan)
- **NTP Synchronization**: Automatic synchronization with atomic clock servers via NTP
- **Terminal Graphics**: Beautiful ASCII/Unicode art rendering using terminal graphics
- **EKI/DCP Integration**: Seamless integration with Enhanced Kitty Installer and DSOS Control Plane
- **Self-Bootstrapping**: Fully automatic installation and setup - no manual configuration needed
- **Responsive Design**: Automatically adjusts to terminal size changes
- **Error Handling**: Robust error handling with fallback mechanisms

## Installation

### 🚀 Auto-Launch Setup (Recommended)

To automatically launch the clock on system boot/login:

```bash
cd clock
./auto_launch.sh
```

This will:
- Set up systemd service (if running as root)
- Add to shell startup files (.bashrc/.zshrc)
- Create desktop autostart entry
- Configure automatic launch on login

**The clock will now launch automatically every time you log in!**

### Self-Bootstrapping Installation (Recommended)

The application includes a fully self-bootstrapping installation system that automatically sets up everything:

```bash
cd clock/
./bootstrap.sh
```

This will:
- Check for Python 3.8+
- Create virtual environment automatically
- Install all dependencies automatically
- Verify configuration
- Make all scripts executable
- **No user prompts required** - fully automatic!

### Prerequisites

- Python 3.8 or higher (will be checked automatically)
- Terminal with Unicode support (Kitty terminal recommended for best experience)
- Internet connection for NTP synchronization

### Install Dependencies

**Option 1: Self-bootstrapping (recommended)**
```bash
cd clock/
./bootstrap.sh
```

**Option 2: Using the launcher (auto-bootstraps on first run)**
```bash
cd clock/
./launch.sh  # Automatically bootstraps if needed
```

**Option 3: Manual installation**
```bash
cd clock/
pip3 install -r requirements.txt
```

### Optional: Install for System-Wide Use

```bash
chmod +x atomic_clock.py
sudo cp atomic_clock.py /usr/local/bin/atomic-clock
```

## Usage

### Quick Start (Recommended)

**First-time setup (self-bootstrapping):**
```bash
cd clock/
./bootstrap.sh
```

**Launch application:**
```bash
./launch.sh
```

The launcher automatically bootstraps on first run if needed - no manual setup required!

On Windows:
```cmd
cd clock
bootstrap.bat  # First time
launch.bat     # Run application
```

### Basic Usage

```bash
cd clock/
python3 atomic_clock.py
```

### Launcher Options

The launcher script (`launch.sh` or `launch.bat`) provides several options:

```bash
# Check dependencies and configuration
./launch.sh --check

# Install dependencies only
./launch.sh --install

# Launch with custom options (all options passed to application)
./launch.sh --ntp-server time.nist.gov
./launch.sh --update-interval 0.5
./launch.sh --locations custom_locations.json

# Skip dependency checks
./launch.sh --no-check
```

### Command Line Options

```bash
# Use custom locations configuration
python3 atomic_clock.py --locations config/locations.json

# Specify preferred NTP server
python3 atomic_clock.py --ntp-server time.nist.gov

# Set custom update interval (in seconds)
python3 atomic_clock.py --update-interval 0.5

# Enable fullscreen mode
python3 atomic_clock.py --fullscreen
```

### Keyboard Shortcuts

While the application is running:

- `q` or `ESC` - Quit application
- `r` - Refresh/Re-sync with atomic clocks
- `s` - Show synchronization status
- `+` - Increase update interval
- `-` - Decrease update interval
- `f` - Toggle fullscreen mode (placeholder)

## Configuration

### Location Configuration

Edit `config/locations.json` to add or modify atomic clock locations:

```json
{
  "locations": [
    {
      "id": "nist",
      "name": "NIST",
      "city": "Boulder, CO",
      "timezone": "America/Denver",
      "ntp_server": "time.nist.gov",
      "corner": "top_left"
    }
  ]
}
```

**Location Fields:**
- `id`: Unique identifier for the location
- `name`: Short name (e.g., "NIST", "PTB")
- `city`: City name for display
- `timezone`: Timezone name (pytz format, e.g., "America/Denver")
- `ntp_server`: NTP server hostname
- `corner`: Corner position (`top_left`, `top_right`, `bottom_left`, `bottom_right`)

### Available Atomic Clock Servers

The application supports multiple atomic clock NTP servers:

- **NIST** (USA): `time.nist.gov`
- **PTB** (Germany): `ptbtime1.ptb.de`
- **NPL** (UK): `time.npl.co.uk`
- **NICT** (Japan): `ntp.nict.jp`
- **USNO** (USA): `tick.usno.navy.mil`
- **Google** (Fallback): `time.google.com`
- **NTP Pool** (Fallback): `pool.ntp.org`

## Architecture

### Components

1. **time_sync.py**: NTP synchronization and atomic clock time retrieval
2. **location_manager.py**: Location configuration and timezone management
3. **clock_renderer.py**: Terminal graphics rendering using ASCII/Unicode art
4. **atomic_clock.py**: Main application with event loop and integration

### Integration with EKI/DCP

The application integrates with:

- **EKI (Enhanced Kitty Installer)**: Uses Kitty Graphics Protocol for terminal rendering
- **DCP (DSOS Control Plane)**: Registers as a DCP module for session management

#### DCP Integration

If DCP is available, the atomic clock automatically registers as a module:

```python
from DCP.core.unified_control_plane import UnifiedControlPlane

ucp = UnifiedControlPlane()
ucp.register_module("atomic_clock", {
    "capabilities": ["time_display", "ntp_sync"],
    "update_interval": 1.0
})
```

#### EKI Integration

The application detects if running in a Kitty terminal and enables enhanced features:

- Terminal graphics protocol support
- Session persistence
- Performance optimizations

## Troubleshooting

### Synchronization Issues

If atomic clock synchronization fails:

1. **Check Internet Connection**: Ensure you have internet access
2. **Firewall**: Verify NTP ports (UDP 123) are not blocked
3. **Server Availability**: Try a different NTP server with `--ntp-server`
4. **Fallback**: The application will use system time if NTP fails

### Display Issues

If the clock display looks incorrect:

1. **Terminal Size**: Ensure terminal is at least 80x24 characters
2. **Unicode Support**: Verify terminal supports Unicode characters
3. **Font**: Use a monospace font with Unicode support
4. **Kitty Terminal**: For best results, use Kitty terminal

### Error Messages

- **"Config file not found"**: Ensure `config/locations.json` exists
- **"Synchronization failed"**: Check network connectivity and NTP server availability
- **"Too many errors"**: Application will exit after 10 consecutive errors

## Testing

Run unit tests:

```bash
cd clock/
python3 -m pytest tests/test_atomic_clock.py -v
```

Or use unittest:

```bash
python3 tests/test_atomic_clock.py
```

## Development

### Project Structure

```
clock/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── atomic_clock.py           # Main application
├── time_sync.py              # NTP synchronization
├── clock_renderer.py         # Terminal rendering
├── location_manager.py       # Location management
├── config/
│   └── locations.json        # Location configuration
├── assets/
│   └── clock_face.svg        # Clock face template (optional)
└── tests/
    └── test_atomic_clock.py  # Unit tests
```

### Adding New Locations

1. Edit `config/locations.json`
2. Add new location entry with required fields
3. Restart application

### Extending Functionality

The application is designed to be extensible:

- **Custom Renderers**: Implement new rendering backends in `clock_renderer.py`
- **Additional Time Sources**: Add new time sources in `time_sync.py`
- **DCP Modules**: Extend DCP integration for additional features

## License

This application is part of the DSMIL System and follows the same licensing terms.

## Acknowledgments

- **NIST**: National Institute of Standards and Technology (USA)
- **PTB**: Physikalisch-Technische Bundesanstalt (Germany)
- **NPL**: National Physical Laboratory (UK)
- **NICT**: National Institute of Information and Communications Technology (Japan)
- **EKI**: Enhanced Kitty Installer
- **DCP**: DSOS Control Plane

## Future Enhancements

- Additional atomic clock locations
- Customizable clock face designs
- Historical time data display
- Time difference calculations
- Alarm/timer functionality
- Export time data to file
- Web-based interface option
- Mobile app integration
