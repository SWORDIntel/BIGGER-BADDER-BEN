#!/bin/bash
#
# Atomic Clock Display Launcher
# Launches the atomic clock application with proper environment setup
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Application name
APP_NAME="Atomic Clock Display"
PYTHON_SCRIPT="atomic_clock.py"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        echo "Please install Python 3.8 or higher"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8 or higher is required (found: $PYTHON_VERSION)"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Function to check and install dependencies (self-bootstrapping)
check_dependencies() {
    print_info "Bootstrapping environment..."
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Auto-create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv 2>/dev/null || {
            print_warning "venv module not available, using system Python"
            USE_VENV=false
        }
        USE_VENV=true
    else
        USE_VENV=true
    fi
    
    # Activate virtual environment if it exists
    if [ "$USE_VENV" = true ] && [ -d "venv" ]; then
        print_info "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Auto-install dependencies without prompting
    print_info "Checking and installing Python packages..."
    
    # Upgrade pip first
    python3 -m pip install --upgrade pip --quiet 2>/dev/null || true
    
    # Install all requirements automatically
    print_info "Installing dependencies from requirements.txt..."
    python3 -m pip install -r requirements.txt --quiet 2>/dev/null || {
        print_warning "Silent install failed, trying verbose..."
        python3 -m pip install -r requirements.txt || {
            print_error "Failed to install dependencies"
            exit 1
        }
    }
    
    # Verify critical packages with correct import names
    MISSING_CRITICAL=()
    
    # Check ntplib
    if ! python3 -c "import ntplib" 2>/dev/null; then
        MISSING_CRITICAL+=("ntplib")
    fi
    
    # Check pytz
    if ! python3 -c "import pytz" 2>/dev/null; then
        MISSING_CRITICAL+=("pytz")
    fi
    
    # Check python-dateutil (imports as dateutil, but check both ways)
    if ! python3 -c "from dateutil import parser" 2>/dev/null && \
       ! python3 -c "import dateutil" 2>/dev/null; then
        MISSING_CRITICAL+=("python-dateutil")
    fi
    
    if [ ${#MISSING_CRITICAL[@]} -gt 0 ]; then
        print_error "Critical packages missing: ${MISSING_CRITICAL[*]}"
        print_info "Attempting manual installation..."
        for pkg in "${MISSING_CRITICAL[@]}"; do
            python3 -m pip install "$pkg" --quiet 2>/dev/null || {
                print_warning "Silent install failed for $pkg, trying verbose..."
                python3 -m pip install "$pkg" || {
                    print_error "Failed to install $pkg"
                    exit 1
                }
            }
        done
        # Verify again after installation
        for pkg in "${MISSING_CRITICAL[@]}"; do
            if [ "$pkg" = "python-dateutil" ]; then
                if ! python3 -c "from dateutil import parser" 2>/dev/null && \
                   ! python3 -c "import dateutil" 2>/dev/null; then
                    print_error "Still missing: $pkg"
                    exit 1
                fi
            else
                if ! python3 -c "import $pkg" 2>/dev/null; then
                    print_error "Still missing: $pkg"
                    exit 1
                fi
            fi
        done
    fi
    
    print_success "Environment bootstrapped successfully"
}

# Function to check terminal compatibility
check_terminal() {
    print_info "Checking terminal compatibility..."
    
    # Check terminal size
    if command_exists tput; then
        COLS=$(tput cols)
        LINES=$(tput lines)
        
        if [ "$COLS" -lt 80 ] || [ "$LINES" -lt 24 ]; then
            print_warning "Terminal size is ${COLS}x${LINES}, recommended: 80x24 or larger"
        else
            print_success "Terminal size: ${COLS}x${LINES}"
        fi
    fi
    
    # Check if running in Kitty terminal
    if [ -n "$KITTY_WINDOW_ID" ]; then
        print_success "Running in Kitty terminal (EKI integration enabled)"
    else
        print_info "Not running in Kitty terminal (some features may be limited)"
    fi
}

# Function to check configuration
check_config() {
    print_info "Checking configuration..."
    
    if [ ! -f "config/locations.json" ]; then
        print_error "Configuration file not found: config/locations.json"
        exit 1
    fi
    
    # Validate JSON
    if ! python3 -c "import json; json.load(open('config/locations.json'))" 2>/dev/null; then
        print_error "Invalid JSON in config/locations.json"
        exit 1
    fi
    
    print_success "Configuration valid"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -c, --check            Check dependencies and configuration only"
    echo "  -i, --install          Install dependencies and exit"
    echo "  --bootstrap            Run full bootstrap script"
    echo "  -l, --locations FILE   Use custom locations config file"
    echo "  -n, --ntp-server HOST Use specific NTP server"
    echo "  -u, --update-interval SEC Set update interval in seconds"
    echo "  -f, --fullscreen       Enable fullscreen mode"
    echo "  --no-check             Skip dependency checks"
    echo "  --no-auto-bootstrap    Disable automatic bootstrapping"
    echo ""
    echo "Examples:"
    echo "  $0                     # Launch with default settings"
    echo "  $0 --ntp-server time.nist.gov"
    echo "  $0 --update-interval 0.5"
    echo "  $0 --locations custom_locations.json"
}

# Parse command line arguments
ARGS=()
SKIP_CHECKS=false
AUTO_BOOTSTRAP=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -c|--check)
            check_python
            check_dependencies
            check_terminal
            check_config
            print_success "All checks passed!"
            exit 0
            ;;
        -i|--install)
            check_python
            check_dependencies
            print_success "Installation complete!"
            exit 0
            ;;
        --bootstrap)
            # Run full bootstrap
            if [ -f "bootstrap.sh" ]; then
                ./bootstrap.sh
                exit $?
            else
                print_error "bootstrap.sh not found"
                exit 1
            fi
            ;;
        --no-check)
            SKIP_CHECKS=true
            AUTO_BOOTSTRAP=false
            shift
            ;;
        --no-auto-bootstrap)
            AUTO_BOOTSTRAP=false
            shift
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Auto-bootstrap if enabled and needed
BOOTSTRAP_DONE=false
if [ "$AUTO_BOOTSTRAP" = true ] && [ "$SKIP_CHECKS" = false ]; then
    # Check if bootstrap is needed - verify imports with correct names
    NEEDS_BOOTSTRAP=false
    if [ ! -d "venv" ]; then
        NEEDS_BOOTSTRAP=true
    else
        # Activate venv for checks
        if [ -d "venv" ]; then
            source venv/bin/activate 2>/dev/null || true
        fi
        # Check all required packages
        if ! python3 -c "import ntplib" 2>/dev/null || \
           ! python3 -c "import pytz" 2>/dev/null || \
           (! python3 -c "from dateutil import parser" 2>/dev/null && \
            ! python3 -c "import dateutil" 2>/dev/null); then
            NEEDS_BOOTSTRAP=true
        fi
    fi
    
    if [ "$NEEDS_BOOTSTRAP" = true ]; then
        print_info "Auto-bootstrapping environment..."
        check_python
        check_dependencies  # This now auto-installs everything
        BOOTSTRAP_DONE=true
    fi
fi

# Main execution
main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  $APP_NAME"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || true
    fi
    
    # Run checks unless skipped (fully automatic)
    if [ "$SKIP_CHECKS" = false ]; then
        check_python
        # Only bootstrap if not already done
        if [ "$BOOTSTRAP_DONE" = false ]; then
            check_dependencies  # Now fully automatic, no prompts
        fi
        check_terminal
        check_config
    fi
    
    # Check if Python script exists
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "Application script not found: $PYTHON_SCRIPT"
        exit 1
    fi
    
    # Make script executable
    chmod +x "$PYTHON_SCRIPT"
    
    print_info "Launching atomic clock..."
    echo ""
    
    # Ensure virtual environment is activated
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || true
    fi
    
    # Launch application with arguments
    print_info "Launching space-age atomic clock..."
    if [ ${#ARGS[@]} -gt 0 ]; then
        python3 "$PYTHON_SCRIPT" "${ARGS[@]}"
    else
        python3 "$PYTHON_SCRIPT"
    fi
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "Application exited successfully"
    else
        print_error "Application exited with code $EXIT_CODE"
        exit $EXIT_CODE
    fi
}

# Run main function
main
