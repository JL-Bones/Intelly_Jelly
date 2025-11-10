#!/bin/bash

###############################################################################
# Intelly Jelly Service Manager
# This script manages Intelly Jelly as a systemd service on Ubuntu
#
# Usage: ./service_manager.sh [setup|enable|disable|start|stop|status|remove]
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service configuration
SERVICE_NAME="intelly-jelly"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"

# Detect Python3 path
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo -e "${RED}Error: python3 not found in PATH${NC}"
    exit 1
fi

# Detect current user
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" == "root" ]; then
    echo -e "${YELLOW}Warning: Running as root. The service will run as root.${NC}"
    echo -e "${YELLOW}Consider running this script as a regular user with sudo privileges.${NC}"
    SERVICE_USER="root"
    SERVICE_GROUP="root"
    USER_HOME="/root"
else
    SERVICE_USER="$CURRENT_USER"
    SERVICE_GROUP=$(id -gn)
    USER_HOME="$HOME"
fi

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if script is run with sudo for operations that need it
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This operation requires sudo privileges."
        echo "Please run: sudo ./service_manager.sh $1"
        exit 1
    fi
}

# Function to check if service file exists
service_exists() {
    [ -f "$SERVICE_FILE" ]
}

# Function to check if service is active
service_active() {
    systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null
}

# Function to check if service is enabled
service_enabled() {
    systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null
}

# Function to validate project directory
validate_project() {
    if [ ! -f "$PROJECT_DIR/app.py" ]; then
        print_error "app.py not found in $PROJECT_DIR"
        print_info "Make sure you're running this script from the Intelly Jelly project directory"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found in $PROJECT_DIR"
        exit 1
    fi
    
    print_success "Project directory validated: $PROJECT_DIR"
}

# Function to check dependencies
check_dependencies() {
    print_info "Checking Python dependencies..."
    
    if ! $PYTHON_PATH -c "import flask" 2>/dev/null; then
        print_warning "Flask is not installed. Installing dependencies..."
        $PYTHON_PATH -m pip install -r "$PROJECT_DIR/requirements.txt"
    else
        print_success "Python dependencies are installed"
    fi
}

# Function to check .env file
check_env_file() {
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        print_warning ".env file not found!"
        print_info "Please create a .env file with your GOOGLE_API_KEY"
        print_info "You can use .env.example as a template:"
        print_info "  cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env"
        print_info "  nano $PROJECT_DIR/.env"
        return 1
    else
        print_success ".env file found"
        return 0
    fi
}

# Function to setup the service
setup_service() {
    check_sudo "setup"
    
    print_info "Setting up Intelly Jelly service..."
    
    # Validate project
    validate_project
    
    # Check dependencies
    check_dependencies
    
    # Check .env file (warning only)
    check_env_file || print_warning "Service will be created but may not start without .env file"
    
    # Create systemd service file
    print_info "Creating systemd service file..."
    
    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Intelly Jelly - AI-Powered Media Organizer
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_GROUP}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${USER_HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PYTHON_PATH} ${PROJECT_DIR}/app.py
Restart=on-failure
RestartSec=10
StandardOutput=append:${PROJECT_DIR}/intelly_jelly.log
StandardError=append:${PROJECT_DIR}/intelly_jelly.log

[Install]
WantedBy=multi-user.target
EOF

    if [ $? -eq 0 ]; then
        print_success "Service file created: $SERVICE_FILE"
    else
        print_error "Failed to create service file"
        exit 1
    fi
    
    # Reload systemd
    print_info "Reloading systemd daemon..."
    systemctl daemon-reload
    
    print_success "Service setup completed!"
    print_info "Service name: ${SERVICE_NAME}"
    print_info "To enable auto-start: sudo ./service_manager.sh enable"
    print_info "To start the service: sudo ./service_manager.sh start"
}

# Function to enable the service
enable_service() {
    check_sudo "enable"
    
    if ! service_exists; then
        print_error "Service not found. Run setup first:"
        echo "  sudo ./service_manager.sh setup"
        exit 1
    fi
    
    print_info "Enabling ${SERVICE_NAME} service..."
    systemctl enable "$SERVICE_NAME"
    
    if service_enabled; then
        print_success "Service enabled (will start on boot)"
    else
        print_error "Failed to enable service"
        exit 1
    fi
}

# Function to disable the service
disable_service() {
    check_sudo "disable"
    
    if ! service_exists; then
        print_error "Service not found"
        exit 1
    fi
    
    print_info "Disabling ${SERVICE_NAME} service..."
    systemctl disable "$SERVICE_NAME"
    
    if ! service_enabled; then
        print_success "Service disabled (will not start on boot)"
    else
        print_error "Failed to disable service"
        exit 1
    fi
}

# Function to start the service
start_service() {
    check_sudo "start"
    
    if ! service_exists; then
        print_error "Service not found. Run setup first:"
        echo "  sudo ./service_manager.sh setup"
        exit 1
    fi
    
    if service_active; then
        print_warning "Service is already running"
        return 0
    fi
    
    print_info "Starting ${SERVICE_NAME} service..."
    systemctl start "$SERVICE_NAME"
    
    sleep 2
    
    if service_active; then
        print_success "Service started successfully"
        print_info "Access the web interface at: http://localhost:7000"
        print_info "View logs: journalctl -u ${SERVICE_NAME} -f"
    else
        print_error "Failed to start service"
        print_info "Check logs with: journalctl -u ${SERVICE_NAME} -n 50"
        exit 1
    fi
}

# Function to stop the service
stop_service() {
    check_sudo "stop"
    
    if ! service_exists; then
        print_error "Service not found"
        exit 1
    fi
    
    if ! service_active; then
        print_warning "Service is not running"
        return 0
    fi
    
    print_info "Stopping ${SERVICE_NAME} service..."
    systemctl stop "$SERVICE_NAME"
    
    sleep 2
    
    if ! service_active; then
        print_success "Service stopped"
    else
        print_error "Failed to stop service"
        exit 1
    fi
}

# Function to check service status
check_status() {
    if ! service_exists; then
        print_warning "Service is not installed"
        echo ""
        print_info "To install the service, run:"
        echo "  sudo ./service_manager.sh setup"
        return 0
    fi
    
    print_info "Service Status:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check if service is active
    if service_active; then
        print_success "Service is running"
    else
        print_warning "Service is not running"
    fi
    
    # Check if service is enabled
    if service_enabled; then
        print_success "Service is enabled (starts on boot)"
    else
        print_warning "Service is disabled (does not start on boot)"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Show detailed status
    print_info "Detailed Status:"
    systemctl status "$SERVICE_NAME" --no-pager || true
    
    echo ""
    print_info "Recent Logs (last 10 lines):"
    journalctl -u "$SERVICE_NAME" -n 10 --no-pager || true
}

# Function to remove the service
remove_service() {
    check_sudo "remove"
    
    if ! service_exists; then
        print_warning "Service is not installed"
        return 0
    fi
    
    print_warning "This will remove the ${SERVICE_NAME} service"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Operation cancelled"
        return 0
    fi
    
    # Stop service if running
    if service_active; then
        print_info "Stopping service..."
        systemctl stop "$SERVICE_NAME"
    fi
    
    # Disable service if enabled
    if service_enabled; then
        print_info "Disabling service..."
        systemctl disable "$SERVICE_NAME"
    fi
    
    # Remove service file
    print_info "Removing service file..."
    rm -f "$SERVICE_FILE"
    
    # Reload systemd
    print_info "Reloading systemd daemon..."
    systemctl daemon-reload
    systemctl reset-failed
    
    print_success "Service removed successfully"
}

# Function to display usage
show_usage() {
    echo "Intelly Jelly Service Manager"
    echo ""
    echo "Usage: ./service_manager.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup    - Install and configure the systemd service"
    echo "  enable   - Enable service to start on boot"
    echo "  disable  - Disable service from starting on boot"
    echo "  start    - Start the service"
    echo "  stop     - Stop the service"
    echo "  status   - Show service status and recent logs"
    echo "  remove   - Uninstall the service"
    echo ""
    echo "Examples:"
    echo "  sudo ./service_manager.sh setup   # First time setup"
    echo "  sudo ./service_manager.sh start   # Start the service"
    echo "  ./service_manager.sh status       # Check status (no sudo needed)"
    echo ""
    echo "Quick Start:"
    echo "  1. sudo ./service_manager.sh setup    # Setup service"
    echo "  2. sudo ./service_manager.sh enable   # Enable auto-start"
    echo "  3. sudo ./service_manager.sh start    # Start service"
    echo "  4. ./service_manager.sh status        # Check if running"
    echo ""
}

# Main script logic
main() {
    case "${1:-}" in
        setup)
            setup_service
            ;;
        enable)
            enable_service
            ;;
        disable)
            disable_service
            ;;
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        status)
            check_status
            ;;
        remove)
            remove_service
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
