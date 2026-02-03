#!/bin/bash
# Auto-launch script for Space-Age Atomic Clock
# This script sets up auto-launch on system boot/login

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOCK_DIR="$SCRIPT_DIR"
CLOCK_SCRIPT="$CLOCK_DIR/atomic_clock.py"
LAUNCH_SCRIPT="$CLOCK_DIR/launch.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   SPACE-AGE ATOMIC CLOCK - AUTO-LAUNCH SETUP            ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root for systemd service
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Setting up system-wide auto-launch...${NC}"
    
    # Create systemd user service
    SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SYSTEMD_USER_DIR"
    
    SERVICE_FILE="$SYSTEMD_USER_DIR/atomic-clock.service"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Space-Age Atomic Clock
After=graphical.target network.target

[Service]
Type=simple
ExecStart=$LAUNCH_SCRIPT
Restart=always
RestartSec=10
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF
    
    # Enable and start service
    systemctl --user daemon-reload
    systemctl --user enable atomic-clock.service
    systemctl --user start atomic-clock.service
    
    echo -e "${GREEN}✓ Systemd service installed and started${NC}"
    echo -e "${CYAN}  Service: $SERVICE_FILE${NC}"
    echo -e "${CYAN}  Status: systemctl --user status atomic-clock.service${NC}"
    
else
    echo -e "${YELLOW}Setting up user-level auto-launch...${NC}"
    
    # Add to .bashrc/.zshrc
    SHELL_RC=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if [ -n "$SHELL_RC" ]; then
        AUTO_LAUNCH_LINE="# Auto-launch Space-Age Atomic Clock"
        AUTO_LAUNCH_CMD="[ -f '$LAUNCH_SCRIPT' ] && '$LAUNCH_SCRIPT' &"
        
        if ! grep -q "Auto-launch Space-Age Atomic Clock" "$SHELL_RC"; then
            echo "" >> "$SHELL_RC"
            echo "$AUTO_LAUNCH_LINE" >> "$SHELL_RC"
            echo "$AUTO_LAUNCH_CMD" >> "$SHELL_RC"
            echo -e "${GREEN}✓ Added auto-launch to $SHELL_RC${NC}"
        else
            echo -e "${YELLOW}⚠ Auto-launch already configured in $SHELL_RC${NC}"
        fi
    fi
    
    # Create desktop entry for autostart
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$AUTOSTART_DIR"
    
    DESKTOP_FILE="$AUTOSTART_DIR/atomic-clock.desktop"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Space-Age Atomic Clock
Comment=Futuristic atomic clock display
Exec=$LAUNCH_SCRIPT
Icon=clock
Terminal=true
Categories=Utility;Clock;
X-GNOME-Autostart-enabled=true
EOF
    
    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ Desktop autostart entry created${NC}"
    echo -e "${CYAN}  File: $DESKTOP_FILE${NC}"
fi

# Create quick launch alias
ALIAS_LINE="alias atomic-clock='cd $CLOCK_DIR && $LAUNCH_SCRIPT'"
if [ -f "$HOME/.bashrc" ] && ! grep -q "alias atomic-clock" "$HOME/.bashrc"; then
    echo "" >> "$HOME/.bashrc"
    echo "$ALIAS_LINE" >> "$HOME/.bashrc"
    echo -e "${GREEN}✓ Added 'atomic-clock' alias${NC}"
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   AUTO-LAUNCH CONFIGURATION COMPLETE                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}The Space-Age Atomic Clock will now launch automatically!${NC}"
echo ""
echo -e "${YELLOW}To launch manually:${NC}"
echo -e "  ${BLUE}cd $CLOCK_DIR && ./launch.sh${NC}"
echo -e "  ${BLUE}atomic-clock${NC}  (if alias was added)"
echo ""
echo -e "${YELLOW}To disable auto-launch:${NC}"
if [ "$EUID" -eq 0 ]; then
    echo -e "  ${BLUE}systemctl --user disable atomic-clock.service${NC}"
else
    echo -e "  ${BLUE}Remove from: $SHELL_RC${NC}"
    echo -e "  ${BLUE}Remove: $DESKTOP_FILE${NC}"
fi
echo ""
