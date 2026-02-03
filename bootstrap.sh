#!/bin/bash
#
# Atomic Clock Bootstrap Script
# Fully self-bootstrapping installation and setup
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║         ATOMIC CLOCK DISPLAY - BOOTSTRAP                 ║"
    echo "║                                                           ║"
    echo "║         Self-Bootstrapping Installation                   ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[BOOTSTRAP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check for Python 3
check_python() {
    print_step "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required (found: $PYTHON_VERSION)"
            return 1
        fi
    else
        print_error "Python 3 not found"
        echo ""
        echo "Please install Python 3.8 or higher:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        echo "  Fedora/RHEL:   sudo dnf install python3 python3-pip"
        echo "  macOS:         brew install python3"
        echo "  Or download from: https://www.python.org/downloads/"
        return 1
    fi
}

# Create virtual environment
setup_venv() {
    print_step "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        return 0
    fi
    
    if python3 -m venv venv 2>/dev/null; then
        print_success "Virtual environment created"
        return 0
    else
        print_warning "Failed to create venv, using system Python"
        return 1
    fi
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    
    # Activate venv if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    else
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    fi
    
    # Upgrade pip
    print_step "Upgrading pip..."
    $PIP_CMD install --upgrade pip --quiet 2>/dev/null || true
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_step "Installing packages from requirements.txt..."
        if $PIP_CMD install -r requirements.txt --quiet 2>/dev/null; then
            print_success "All dependencies installed"
        else
            print_warning "Silent install failed, trying verbose..."
            if $PIP_CMD install -r requirements.txt; then
                print_success "Dependencies installed"
            else
                print_error "Failed to install dependencies"
                return 1
            fi
        fi
    else
        print_error "requirements.txt not found"
        return 1
    fi
    
    # Verify critical packages
    print_step "Verifying installation..."
    MISSING=()
    for pkg in ntplib pytz python-dateutil; do
        if ! $PYTHON_CMD -c "import ${pkg//-/_}" 2>/dev/null; then
            MISSING+=("$pkg")
        fi
    done
    
    if [ ${#MISSING[@]} -gt 0 ]; then
        print_warning "Missing packages: ${MISSING[*]}, installing..."
        for pkg in "${MISSING[@]}"; do
            $PIP_CMD install "$pkg" --quiet || $PIP_CMD install "$pkg"
        done
    fi
    
    print_success "Installation verified"
    return 0
}

# Verify configuration
verify_config() {
    print_step "Verifying configuration..."
    
    if [ ! -f "config/locations.json" ]; then
        print_error "Configuration file not found: config/locations.json"
        return 1
    fi
    
    if python3 -c "import json; json.load(open('config/locations.json'))" 2>/dev/null; then
        print_success "Configuration valid"
        return 0
    else
        print_error "Invalid JSON in config/locations.json"
        return 1
    fi
}

# Make scripts executable
make_executable() {
    print_step "Making scripts executable..."
    chmod +x atomic_clock.py launch.sh bootstrap.sh 2>/dev/null || true
    chmod +x time_sync.py location_manager.py clock_renderer.py 2>/dev/null || true
    print_success "Scripts made executable"
}

setup_auto_launch() {
    if [ -x "./auto_launch.sh" ]; then
        print_step "Configuring auto-launch..."
        ./auto_launch.sh
        print_success "Auto-launch configured"
    else
        print_warning "auto_launch.sh not found; skipping auto-launch setup"
    fi
    echo ""
}

# Main bootstrap function
main() {
    print_banner
    
    print_step "Starting bootstrap process..."
    echo ""
    
    # Check Python
    if ! check_python; then
        exit 1
    fi
    echo ""
    
    # Setup virtual environment
    setup_venv
    echo ""
    
    # Install dependencies
    if ! install_dependencies; then
        exit 1
    fi
    echo ""
    
    # Verify configuration
    if ! verify_config; then
        exit 1
    fi
    echo ""
    
    # Make scripts executable
    make_executable
    echo ""

    # Configure auto-launch for space-age clock
    setup_auto_launch
    
    
    # Success message
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║              BOOTSTRAP COMPLETE!                          ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    print_success "Atomic Clock Display is ready to use!"
    echo ""
    echo "To launch the application:"
    echo "  ./launch.sh"
    echo ""
    echo "Or directly:"
    echo "  python3 atomic_clock.py"
    echo ""
}

# Run bootstrap
main
