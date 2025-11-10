# Intelly Jelly Service Setup Guide

This guide explains how to run Intelly Jelly as a systemd service on Ubuntu, allowing it to start automatically on boot and run in the background.

## Prerequisites

- Ubuntu Linux (or other systemd-based distributions)
- Python 3.8 or higher
- sudo privileges

## Quick Start

The `service_manager.sh` script provides a simple way to manage Intelly Jelly as a system service.

### 1. Setup the Service

First, install and configure the service:

```bash
sudo ./service_manager.sh setup
```

This will:
- Validate your project directory and dependencies
- Create a systemd service file at `/etc/systemd/system/intelly-jelly.service`
- Configure the service to run as your current user
- Check for the `.env` file (required for operation)

**Important:** Make sure you have created a `.env` file with your `GOOGLE_API_KEY` before starting the service:

```bash
cp .env.example .env
nano .env  # Add your API key
```

### 2. Enable Auto-Start (Optional)

To make the service start automatically on system boot:

```bash
sudo ./service_manager.sh enable
```

### 3. Start the Service

Start the Intelly Jelly service:

```bash
sudo ./service_manager.sh start
```

The web interface will be available at: `http://localhost:7000`

### 4. Check Status

Check if the service is running:

```bash
./service_manager.sh status
```

This command doesn't require sudo and will show:
- Whether the service is running
- Whether it's enabled for auto-start
- Recent log entries

## All Available Commands

The service manager supports the following commands:

| Command | Description | Requires Sudo |
|---------|-------------|---------------|
| `setup` | Install and configure the systemd service | Yes |
| `enable` | Enable service to start on boot | Yes |
| `disable` | Disable service from starting on boot | Yes |
| `start` | Start the service | Yes |
| `stop` | Stop the service | Yes |
| `status` | Show service status and recent logs | No |
| `remove` | Uninstall the service completely | Yes |

## Usage Examples

### Basic Operation

```bash
# Setup for the first time
sudo ./service_manager.sh setup

# Start the service
sudo ./service_manager.sh start

# Check if it's running
./service_manager.sh status

# Stop the service
sudo ./service_manager.sh stop
```

### Auto-Start Configuration

```bash
# Enable auto-start on boot
sudo ./service_manager.sh enable

# Disable auto-start
sudo ./service_manager.sh disable
```

### Maintenance

```bash
# Check status and logs
./service_manager.sh status

# Remove the service completely
sudo ./service_manager.sh remove
```

## Viewing Logs

### Real-Time Logs

To watch logs in real-time:

```bash
journalctl -u intelly-jelly -f
```

### Recent Logs

To view the last 50 log entries:

```bash
journalctl -u intelly-jelly -n 50
```

### Logs Since Boot

To view all logs since the last boot:

```bash
journalctl -u intelly-jelly -b
```

### Application Log File

The service also writes to the application's own log file:

```bash
tail -f intelly_jelly.log
```

## Troubleshooting

### Service Won't Start

1. **Check the .env file exists:**
   ```bash
   ls -la .env
   ```
   If missing, create it from `.env.example` and add your API key.

2. **Check Python dependencies:**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **View detailed error logs:**
   ```bash
   journalctl -u intelly-jelly -n 50
   ```

### Permission Issues

If you encounter permission errors:

1. Ensure the script is executable:
   ```bash
   chmod +x service_manager.sh
   ```

2. Make sure you're using sudo for operations that require it:
   ```bash
   sudo ./service_manager.sh setup
   ```

### Service Running but Web Interface Not Accessible

1. Check if the service is actually running:
   ```bash
   ./service_manager.sh status
   ```

2. Verify the port is listening:
   ```bash
   sudo netstat -tulpn | grep 7000
   # or
   sudo ss -tulpn | grep 7000
   ```

3. Check for firewall rules:
   ```bash
   sudo ufw status
   ```

### Updating the Application

When you update the application code:

1. Stop the service:
   ```bash
   sudo ./service_manager.sh stop
   ```

2. Pull the latest changes:
   ```bash
   git pull
   ```

3. Update dependencies if needed:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. Start the service:
   ```bash
   sudo ./service_manager.sh start
   ```

## Service Configuration

The service is configured with the following settings:

- **Service Name:** `intelly-jelly`
- **Service File:** `/etc/systemd/system/intelly-jelly.service`
- **Working Directory:** Your project directory (auto-detected)
- **User:** Your current user (auto-detected)
- **Port:** 7000
- **Restart Policy:** Automatic restart on failure
- **Logs:** Written to both `journalctl` and `intelly_jelly.log`

## Advanced Usage

### Running as a Different User

By default, the service runs as the user who executes the setup command. To run as a different user:

1. Edit the generated service file:
   ```bash
   sudo nano /etc/systemd/system/intelly-jelly.service
   ```

2. Modify the `User` and `Group` lines

3. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
   ```

### Changing the Port

To change the default port (7000), you'll need to modify `app.py`:

1. Edit the file and change the port in the last line
2. Restart the service:
   ```bash
   sudo ./service_manager.sh stop
   sudo ./service_manager.sh start
   ```

## Uninstalling

To completely remove the service:

```bash
sudo ./service_manager.sh remove
```

This will:
- Stop the service if running
- Disable auto-start if enabled
- Remove the systemd service file
- Clean up systemd configuration

Note: This does not delete the application files or configuration, only the service setup.

## Security Considerations

- The service runs as your user account (not root) for better security
- The `.env` file should have restricted permissions (600 recommended):
  ```bash
  chmod 600 .env
  ```
- Logs may contain sensitive information - review log permissions as needed
- The web interface runs on localhost by default - use a reverse proxy (nginx/apache) for remote access

## Additional Resources

- [Intelly Jelly README](README.md) - Main application documentation
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Ubuntu systemd Guide](https://ubuntu.com/server/docs/service-management-with-systemd)
