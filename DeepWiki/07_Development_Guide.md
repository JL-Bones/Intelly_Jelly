# Development Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Setup](#development-setup)
4. [Code Style & Standards](#code-style--standards)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Contributing](#contributing)
8. [Deployment](#deployment)

---

## Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Git**: Version control
- **Google API Key**: For AI functionality

### Quick Start

```bash
# Clone repository
git clone https://github.com/JL-Bones/Intelly_Jelly.git
cd Intelly_Jelly

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run application
python app.py
```

Access at: http://localhost:7000

---

## Project Structure

```
Intelly_Jelly/
├── app.py                      # Flask application entry point
├── config.json                 # Public configuration
├── .env                        # Secret configuration (not in git)
├── .env.example               # Environment template
├── instructions.md            # AI prompt instructions
├── requirements.txt           # Python dependencies
├── README.md                  # User documentation
├── Starting_prompt.md         # Original design specification
├── .gitignore                # Git ignore rules
│
├── backend/                   # Backend modules
│   ├── ai_processor.py        # AI integration
│   ├── backend_orchestrator.py # Main coordinator
│   ├── config_manager.py      # Configuration handling
│   ├── file_watcher.py        # File system monitoring
│   └── job_store.py           # Job state management
│
├── templates/                 # HTML templates
│   ├── index.html            # Dashboard page
│   └── settings.html         # Settings page
│
├── test_folders/             # Test directories (created at runtime)
│   ├── downloading/          # Test downloading folder
│   ├── completed/            # Test completed folder
│   └── library/              # Test library folder
│
├── DeepWiki/                 # Comprehensive documentation
│   ├── 01_Architecture_Overview.md
│   ├── 02_Backend_Components.md
│   ├── 03_Frontend_Interface.md
│   ├── 04_Configuration_Guide.md
│   ├── 05_Processing_Workflows.md
│   ├── 06_File_Organization_Rules.md
│   └── 07_Development_Guide.md
│
└── intelly_jelly.log         # Application log file (created at runtime)
```

### File Purposes

**Root Level**:
- `app.py`: Main application entry point, Flask routes
- `config.json`: Runtime configuration (paths, settings)
- `.env`: API keys and secrets
- `instructions.md`: AI prompt template
- `requirements.txt`: Python package dependencies

**Backend**:
- `ai_processor.py`: Google AI API integration
- `backend_orchestrator.py`: Coordinates all backend operations
- `config_manager.py`: Configuration loading and monitoring
- `file_watcher.py`: File system event handling
- `job_store.py`: Thread-safe job state storage

**Templates**:
- `index.html`: Dashboard with job monitoring
- `settings.html`: Configuration interface

**Generated**:
- `test_folders/`: Created automatically for testing
- `intelly_jelly.log`: Application log output
- `__pycache__/`: Python bytecode cache

---

## Development Setup

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### IDE Setup

#### VS Code

Recommended extensions:
- Python (Microsoft)
- Pylance
- Python Debugger

**settings.json**:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

**launch.json** (for debugging):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload",
                "--port", "7000"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

#### PyCharm

1. Open project
2. Configure Python interpreter (use virtual environment)
3. Mark `backend` as sources root
4. Configure Flask run configuration:
   - Script path: `app.py`
   - Environment variables: Load from `.env`

### Environment Variables

Create `.env` file:
```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (future use)
OPENAI_API_KEY=your_openai_key_if_needed
```

**Security**:
- Never commit `.env` to git
- Use different keys for dev/prod
- Rotate keys regularly

### Development Configuration

For development, use test folders:

**config.json**:
```json
{
  "DOWNLOADING_PATH": "./test_folders/downloading",
  "COMPLETED_PATH": "./test_folders/completed",
  "LIBRARY_PATH": "./test_folders/library",
  "DEBOUNCE_SECONDS": 2,
  "AI_BATCH_SIZE": 3,
  "DRY_RUN_MODE": true
}
```

This configuration:
- Uses local test folders
- Reduces debounce time for faster testing
- Small batch size for quick iteration
- Dry run mode prevents actual file moves

---

## Code Style & Standards

### Python Style Guide

Follow **PEP 8** with these specifics:

**Indentation**: 4 spaces (not tabs)

**Line Length**: 
- Max 120 characters (flexible)
- Break long lines logically

**Imports**:
```python
# Standard library
import os
import threading
from typing import Dict, List, Optional

# Third-party
import requests
from flask import Flask, jsonify

# Local
from backend.job_store import JobStore
from backend.config_manager import ConfigManager
```

**Naming Conventions**:
```python
# Classes: PascalCase
class JobStore:
    pass

# Functions/methods: snake_case
def get_all_jobs():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_BATCH_SIZE = 100

# Private: leading underscore
def _internal_method():
    pass
```

**Type Hints**:
```python
def process_batch(self, file_paths: List[str]) -> List[Dict]:
    pass

def get_job(self, job_id: str) -> Optional[Job]:
    pass
```

**Docstrings**:
```python
def complex_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
    """
    pass
```

### Logging Standards

**Log Levels**:
```python
logger.debug("Detailed information for debugging")
logger.info("Informational messages about normal operations")
logger.warning("Warning about potential issues")
logger.error("Error occurred but application continues")
logger.critical("Critical error, application may not continue")
```

**Good Logging Practices**:
```python
# Include context
logger.info(f"Processing job {job_id} with {len(files)} files")

# Log exceptions with traceback
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {type(e).__name__}: {e}", exc_info=True)

# Use appropriate levels
logger.debug(f"File path calculated: {path}")  # Details
logger.info(f"Job {job_id} completed")  # Progress
logger.warning(f"Job {job_id} not found")  # Potential issues
logger.error(f"Failed to move file: {e}")  # Actual errors
```

### Thread Safety

**Always use locks for shared resources**:
```python
class ThreadSafeClass:
    def __init__(self):
        self._data = {}
        self._lock = threading.RLock()
    
    def safe_operation(self):
        with self._lock:
            # All data access here
            self._data['key'] = 'value'
```

**Common patterns**:
- Use `threading.RLock()` for reentrant locks
- Use `with self._lock:` context manager
- Lock all reads and writes to shared data
- Keep locked sections small

---

## Testing

### Manual Testing

#### Test File Detection

```bash
# 1. Start application
python app.py

# 2. Add test file
echo "test" > test_folders/downloading/test.mkv

# 3. Check logs
tail -f intelly_jelly.log

# 4. Check dashboard
# Open http://localhost:7000
```

#### Test AI Processing

```bash
# 1. Enable dry run mode in config.json
{
  "DRY_RUN_MODE": true
}

# 2. Add file with recognizable name
cp movie.2020.1080p.mkv test_folders/downloading/

# 3. Wait for debounce timer

# 4. Check dashboard for AI result
```

#### Test File Organization

```bash
# 1. Disable dry run mode
{
  "DRY_RUN_MODE": false
}

# 2. Add file to downloading
cp test.mkv test_folders/downloading/

# 3. Wait for AI processing

# 4. Move to completed
mv test_folders/downloading/test.mkv test_folders/completed/

# 5. Check library for organized file
ls test_folders/library/
```

### Unit Testing (Future)

Framework recommendation: `pytest`

```python
# test_job_store.py
def test_add_job():
    store = JobStore()
    job = store.add_job("/path/file.mkv", "file.mkv")
    
    assert job.job_id is not None
    assert job.status == JobStatus.QUEUED_FOR_AI
    assert store.get_job(job.job_id) == job

def test_update_job():
    store = JobStore()
    job = store.add_job("/path/file.mkv", "file.mkv")
    
    store.update_job(job.job_id, JobStatus.COMPLETED, new_path="/library/file.mkv")
    
    updated = store.get_job(job.job_id)
    assert updated.status == JobStatus.COMPLETED
    assert updated.new_path == "/library/file.mkv"
```

### Integration Testing (Future)

```python
# test_integration.py
def test_full_workflow():
    # Setup
    setup_test_environment()
    
    # Add file to downloading
    create_test_file("test_folders/downloading/movie.mkv")
    
    # Wait for processing
    time.sleep(10)
    
    # Verify job created
    jobs = get_all_jobs()
    assert len(jobs) == 1
    assert jobs[0].status == JobStatus.PENDING_COMPLETION
    
    # Move to completed
    move_file("downloading/movie.mkv", "completed/movie.mkv")
    
    # Wait for organization
    time.sleep(2)
    
    # Verify file organized
    assert file_exists("test_folders/library/Movies/Movie Title (2020).mkv")
```

---

## Debugging

### Enable Debug Logging

```python
# In app.py, change logging level
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    ...
)
```

### Common Issues & Solutions

#### Issue: "No jobs are being created"

**Check**:
1. File watcher started?
   - Look for: `Started watching: ./test_folders/downloading`
2. File actually in downloading folder?
   - Verify path in config.json
3. File is not a directory?
   - Watchers ignore directories

**Debug**:
```python
# Add to backend_orchestrator.py
def _on_file_detected(self, file_path: str, relative_path: str):
    print(f"DEBUG: File detected: {file_path}")
    logger.info(f"File detected in downloading folder: {relative_path}")
    ...
```

#### Issue: "AI processing not happening"

**Check**:
1. API key set in .env?
   - `echo $GOOGLE_API_KEY` (Linux/Mac)
   - `echo %GOOGLE_API_KEY%` (Windows)
2. Debounce timer waiting?
   - Wait DEBOUNCE_SECONDS after last file
3. Jobs stuck in QUEUED_FOR_AI?
   - Check dashboard

**Debug**:
```python
# Check AI processor
def process_batch(self, file_paths: List[str]) -> List[Dict]:
    logger.info(f"DEBUG: process_batch called with {len(file_paths)} files")
    logger.info(f"DEBUG: API key present: {bool(self.config_manager.get_env('GOOGLE_API_KEY'))}")
    ...
```

#### Issue: "Files not being organized"

**Check**:
1. Job status is PENDING_COMPLETION?
2. File actually in completed folder?
3. Library path writable?
4. Dry run mode disabled?

**Debug**:
```python
# Check file completion handler
def _on_file_completed(self, file_path: str, relative_path: str):
    logger.info(f"DEBUG: File completion detected: {file_path}")
    logger.info(f"DEBUG: Looking for job with path: {relative_path}")
    job = self.job_store.get_job_by_path(relative_path)
    logger.info(f"DEBUG: Job found: {job is not None}")
    ...
```

### Using Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use Python 3.7+
breakpoint()
```

**Debugger commands**:
- `n`: Next line
- `s`: Step into function
- `c`: Continue execution
- `p variable`: Print variable
- `l`: List source code
- `q`: Quit debugger

### Flask Debug Mode

```python
# In app.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True, threaded=True)
```

**Features**:
- Auto-reload on code changes
- Interactive debugger in browser
- Detailed error pages

**Warning**: Never use debug=True in production!

---

## Contributing

### Workflow

1. **Fork repository**

2. **Create feature branch**:
```bash
git checkout -b feature/new-feature
```

3. **Make changes**:
- Follow code style guidelines
- Add appropriate logging
- Update documentation

4. **Test changes**:
- Manual testing
- Check logs for errors
- Verify in web UI

5. **Commit changes**:
```bash
git add .
git commit -m "Add new feature: description"
```

6. **Push to fork**:
```bash
git push origin feature/new-feature
```

7. **Create pull request**

### Commit Message Format

```
Type: Brief description

Detailed explanation of changes:
- Change 1
- Change 2
- Change 3

Closes #123
```

**Types**:
- `Feature`: New functionality
- `Fix`: Bug fix
- `Docs`: Documentation only
- `Style`: Code style/formatting
- `Refactor`: Code restructuring
- `Test`: Adding tests
- `Chore`: Maintenance tasks

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Changes are well-documented
- [ ] Logging is appropriate
- [ ] Thread safety considered
- [ ] Error handling present
- [ ] Tested manually
- [ ] No sensitive data in commits

---

## Deployment

### Production Setup

#### 1. Prepare Environment

```bash
# Create production directory
mkdir /opt/intelly_jelly
cd /opt/intelly_jelly

# Clone repository
git clone https://github.com/JL-Bones/Intelly_Jelly.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Application

```bash
# Create .env
cp .env.example .env
nano .env
# Add production API keys

# Create config.json
nano config.json
```

**Production config.json**:
```json
{
  "DOWNLOADING_PATH": "/mnt/downloads/processing",
  "COMPLETED_PATH": "/mnt/downloads/completed",
  "LIBRARY_PATH": "/mnt/media/library",
  "INSTRUCTIONS_FILE_PATH": "/opt/intelly_jelly/instructions.md",
  "DEBOUNCE_SECONDS": 10,
  "AI_BATCH_SIZE": 20,
  "AI_PROVIDER": "google",
  "AI_MODEL": "gemini-pro",
  "DRY_RUN_MODE": false,
  "ENABLE_WEB_SEARCH": false
}
```

#### 3. Set Up Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/intelly_jelly.service
```

**intelly_jelly.service**:
```ini
[Unit]
Description=Intelly Jelly Media Organizer
After=network.target

[Service]
Type=simple
User=mediauser
WorkingDirectory=/opt/intelly_jelly
Environment="PATH=/opt/intelly_jelly/venv/bin"
ExecStart=/opt/intelly_jelly/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable intelly_jelly
sudo systemctl start intelly_jelly

# Check status
sudo systemctl status intelly_jelly

# View logs
sudo journalctl -u intelly_jelly -f
```

#### 4. Set Up Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/intelly_jelly
```

**nginx config**:
```nginx
server {
    listen 80;
    server_name media.example.com;
    
    location / {
        proxy_pass http://localhost:7000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/intelly_jelly /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d media.example.com
```

### Monitoring

#### Log Rotation

```bash
sudo nano /etc/logrotate.d/intelly_jelly
```

```
/opt/intelly_jelly/intelly_jelly.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 mediauser mediauser
    sharedscripts
    postrotate
        systemctl reload intelly_jelly
    endscript
}
```

#### Health Check Script

```bash
#!/bin/bash
# health_check.sh

if curl -f http://localhost:7000/ > /dev/null 2>&1; then
    echo "OK: Intelly Jelly is running"
    exit 0
else
    echo "ERROR: Intelly Jelly is down"
    systemctl restart intelly_jelly
    exit 1
fi
```

### Backup Strategy

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backups/intelly_jelly"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /opt/intelly_jelly/config.json \
    /opt/intelly_jelly/instructions.md \
    /opt/intelly_jelly/.env

# Keep last 30 days
find "$BACKUP_DIR" -name "config_*.tar.gz" -mtime +30 -delete
```

### Updates

```bash
cd /opt/intelly_jelly

# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart intelly_jelly
```

---

## Summary

This development guide provides:

1. **Setup**: Quick start and environment configuration
2. **Structure**: Clear project organization
3. **Standards**: Code style and best practices
4. **Testing**: Manual and automated testing approaches
5. **Debugging**: Common issues and solutions
6. **Contributing**: Git workflow and guidelines
7. **Deployment**: Production setup and maintenance

For questions or issues, refer to the DeepWiki documentation or create a GitHub issue.
