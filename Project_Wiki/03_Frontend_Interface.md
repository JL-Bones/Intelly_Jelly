# Frontend Interface & API Reference

## Table of Contents
1. [Flask Application](#flask-application)
2. [Dashboard (index.html)](#dashboard-indexhtml)
3. [Settings Page (settings.html)](#settings-page-settingshtml)
4. [API Endpoints](#api-endpoints)
5. [JavaScript Functions](#javascript-functions)
6. [Responsive Design](#responsive-design)

---

## Flask Application

**File**: `app.py`

### Overview
The Flask application serves as the web server and API gateway, providing both HTML pages and RESTful API endpoints for the frontend to interact with the backend.

### Configuration

```python
app = Flask(__name__)
```

- **Host**: `0.0.0.0` (accessible from network)
- **Port**: `7000`
- **Debug**: `False` (production mode)
- **Threaded**: `True` (handles concurrent requests)

### Global Objects

| Object | Type | Description |
|--------|------|-------------|
| `config_manager` | ConfigManager | Configuration management |
| `job_store` | JobStore | Job state storage |
| `orchestrator` | BackendOrchestrator | Backend coordinator |
| `ai_processor` | AIProcessor | AI operations |
| `backend_thread` | Thread | Backend operation thread |

### Initialization Sequence

```python
# 1. Create test folders
os.makedirs('./test_folders/downloading', exist_ok=True)
os.makedirs('./test_folders/completed', exist_ok=True)
os.makedirs('./test_folders/library', exist_ok=True)

# 2. Start backend thread (daemon)
backend_thread = threading.Thread(target=start_backend, daemon=True)
backend_thread.start()

# 3. Start Flask server
app.run(host='0.0.0.0', port=7000, debug=False, threaded=True)
```

### Logging Configuration

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelly_jelly.log'),
        logging.StreamHandler()
    ]
)
```

- **Log File**: `intelly_jelly.log`
- **Console**: Also logs to stdout
- **Format**: Timestamp, logger name, level, message

---

## Dashboard (index.html)

**File**: `templates/index.html`

### Overview
The main dashboard provides real-time monitoring of all jobs with auto-refresh functionality, job management capabilities, and visual statistics.

### Page Structure

```html
<body>
  <div class="container">
    <header>...</header>
    <div class="stats">...</div>
    <div class="jobs-container">...</div>
  </div>
  <div class="modal" id="edit-modal">...</div>
  <div class="modal" id="reai-modal">...</div>
</body>
```

### Header Component

```html
<header>
  <h1>🍇 Intelly Jelly</h1>
  <div class="nav-links">
    <a href="/">Dashboard</a>
    <a href="/settings">Settings</a>
  </div>
</header>
```

**Features**:
- Application title with emoji
- Navigation links
- Responsive layout

### Statistics Panel

Displays 6 real-time statistics:

| Stat | Description | Color |
|------|-------------|-------|
| Total Jobs | All jobs in system | Purple |
| Queued | Waiting for AI | Purple |
| Processing | Being processed | Purple |
| Pending | Waiting for file | Purple |
| Completed | Successfully done | Purple |
| Failed | Errors occurred | Purple |

**Update Frequency**: Every 3 seconds via API

### Jobs Table

**Columns**:
1. **Original Path**: Relative path of file
2. **Status**: Current job status with colored badge
3. **New Name**: AI-suggested name
4. **Confidence**: AI confidence score (0-100%)
5. **Actions**: Edit and Re-AI buttons

**Status Badges**:
- 🟡 Queued for AI (yellow/red)
- 🔵 Processing AI (blue)
- 🟣 Pending Completion (purple)
- 🟢 Completed (green)
- 🔴 Failed (red)
- 🟠 Manual Edit (orange)

### Edit Modal

**Purpose**: Manually set job name and path

**Fields**:
- **New Name** (required): Desired filename
- **New Path** (optional): Full path including subdirectories

**Example**:
```
New Name: Movie Title (2020).mkv
New Path: Movies/Action/Movie Title (2020).mkv
```

**Actions**:
- **Cancel**: Close without saving
- **Save**: Submit changes to API

### Re-AI Modal

**Purpose**: Reprocess job with custom options

**Fields**:
- **Custom Prompt** (optional): Additional AI instructions
- **Include instructions.txt** (checkbox): Use default instructions
- **Include original filename** (checkbox): Show filename to AI
- **Enable web search** (checkbox): Allow AI to search web

**Actions**:
- **Cancel**: Close without submitting
- **Regen**: Queue for reprocessing

### Auto-Refresh

```javascript
setInterval(() => {
    loadJobs();
    loadStats();
}, 3000);
```

- **Interval**: 3 seconds
- **Updates**: Jobs table and statistics
- **Method**: Polls API endpoints

### Empty State

When no jobs exist:
```html
<div class="empty-state">
    <div class="empty-state-icon">📁</div>
    <p>No jobs yet. Add files to the downloading folder to get started.</p>
</div>
```

---

## Settings Page (settings.html)

**File**: `templates/settings.html`

### Overview
Comprehensive configuration interface for all application settings with dynamic model loading and real-time validation.

### Page Structure

```html
<body>
  <div class="container">
    <header>...</header>
    <div class="settings-container">
      <div class="settings-header">...</div>
      <div id="alert" class="alert"></div>
      <form id="settings-form">...</form>
    </div>
  </div>
</body>
```

### Settings Sections

#### 1. Folder Paths

**Downloading Path**
- Path to monitor for new files
- Default: `./test_folders/downloading`

**Completed Path**
- Path where completed downloads appear
- Default: `./test_folders/completed`

**Library Path**
- Path where organized files will be stored
- Default: `./test_folders/library`

**Instructions File Path**
- Path to AI prompt instructions file
- Default: `./instructions.md`

#### 2. Processing Settings

**Debounce Seconds**
- Wait time before processing batch
- Type: Number (1-60)
- Default: 5

**AI Batch Size**
- Number of files to process at once
- Type: Number (1-100)
- Default: 10

#### 3. AI Configuration

**AI Model**
- Dynamic dropdown populated from API
- Shows available Google AI models
- Loading indicator during fetch

**Model Loading Process**:
1. Page loads
2. Shows "Loading models..."
3. Calls `/api/models` endpoint
4. Populates dropdown with available models
5. Selects current model from config

#### 4. Advanced Options

**Dry Run Mode** (checkbox)
- When enabled, files won't actually be moved
- For testing purposes

**Enable Web Search** (checkbox)
- Allow AI to search the web for context
- Uses Google Search Retrieval

### Alert System

**Success Alert** (green):
```
Settings saved successfully!
```

**Error Alert** (red):
```
Error saving settings
```

**Auto-dismiss**: 5 seconds

### Form Submission

**Process**:
1. Prevent default form submission
2. Disable submit button
3. Change button text to "Saving..."
4. Collect all form values
5. Convert types (checkboxes to boolean, numbers to int)
6. Send POST to `/api/config`
7. Show success/error alert
8. Re-enable button
9. Restore button text

### Dynamic Model Loading

```javascript
async function loadModels() {
    // Show loading state
    modelSelect.disabled = true;
    loadingIndicator.style.display = 'inline-block';
    
    // Fetch models
    const response = await fetch('/api/models', {
        method: 'POST',
        body: JSON.stringify({ provider: 'google' })
    });
    
    // Populate dropdown
    const models = data.models;
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
    
    // Select current model
    modelSelect.value = currentConfig.AI_MODEL;
    
    // Hide loading state
    loadingIndicator.style.display = 'none';
    modelSelect.disabled = false;
}
```

---

## API Endpoints

### Job Management

#### `GET /api/jobs`

Get all jobs.

**Response**:
```json
[
    {
        "job_id": "abc-123-def-456",
        "original_path": "/downloads/movie.mkv",
        "relative_path": "movie.mkv",
        "status": "Pending Completion",
        "ai_determined_name": "Movie Title (2020).mkv",
        "new_path": null,
        "confidence": 95,
        "error_message": null,
        "created_at": "2025-11-09T10:30:00",
        "updated_at": "2025-11-09T10:30:15",
        "priority": false
    }
]
```

#### `GET /api/jobs/<job_id>`

Get specific job by ID.

**Parameters**:
- `job_id` (path): Job UUID

**Response** (200):
```json
{
    "job_id": "abc-123",
    "original_path": "/downloads/movie.mkv",
    ...
}
```

**Response** (404):
```json
{
    "error": "Job not found"
}
```

#### `POST /api/jobs/<job_id>/edit`

Manually edit a job.

**Parameters**:
- `job_id` (path): Job UUID

**Request Body**:
```json
{
    "new_name": "My Movie (2020).mkv",
    "new_path": "Movies/Action/My Movie (2020).mkv"
}
```

**Response** (200):
```json
{
    "success": true,
    "message": "Job updated successfully"
}
```

**Response** (400):
```json
{
    "error": "new_name is required"
}
```

**Response** (404):
```json
{
    "error": "Job not found"
}
```

**Response** (500):
```json
{
    "error": "Internal server error"
}
```

#### `POST /api/jobs/<job_id>/re-ai`

Queue job for AI reprocessing.

**Parameters**:
- `job_id` (path): Job UUID

**Request Body**:
```json
{
    "custom_prompt": "This is a documentary about nature",
    "include_instructions": true,
    "include_filename": true,
    "enable_web_search": true
}
```

**Fields**:
- `custom_prompt` (optional): Additional AI instructions
- `include_instructions` (default: true): Include default instructions
- `include_filename` (default: true): Include filename in prompt
- `enable_web_search` (default: false): Enable web search

**Response** (200):
```json
{
    "success": true,
    "message": "Job queued for re-processing"
}
```

**Response** (404):
```json
{
    "error": "Job not found"
}
```

### Configuration Management

#### `GET /api/config`

Get current configuration.

**Response**:
```json
{
    "DOWNLOADING_PATH": "./test_folders/downloading",
    "COMPLETED_PATH": "./test_folders/completed",
    "LIBRARY_PATH": "./test_folders/library",
    "INSTRUCTIONS_FILE_PATH": "./instructions.md",
    "DEBOUNCE_SECONDS": 5,
    "AI_BATCH_SIZE": 10,
    "AI_PROVIDER": "google",
    "AI_MODEL": "gemini-pro",
    "DRY_RUN_MODE": false,
    "ENABLE_WEB_SEARCH": false
}
```

#### `POST /api/config`

Update configuration.

**Request Body**:
```json
{
    "DOWNLOADING_PATH": "./new/downloading",
    "DEBOUNCE_SECONDS": 10,
    "AI_MODEL": "gemini-1.5-pro"
}
```

**Allowed Fields**:
- `DOWNLOADING_PATH`
- `COMPLETED_PATH`
- `LIBRARY_PATH`
- `INSTRUCTIONS_FILE_PATH`
- `DEBOUNCE_SECONDS`
- `AI_BATCH_SIZE`
- `AI_PROVIDER`
- `AI_MODEL`
- `DRY_RUN_MODE`
- `ENABLE_WEB_SEARCH`

**Response** (200):
```json
{
    "success": true,
    "message": "Configuration updated successfully"
}
```

**Response** (500):
```json
{
    "error": "Failed to update configuration"
}
```

### AI Model Discovery

#### `POST /api/models`

Get available AI models for provider.

**Request Body**:
```json
{
    "provider": "google"
}
```

**Response** (200):
```json
{
    "models": [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
}
```

**Response** (200 with warning):
```json
{
    "models": [],
    "warning": "GOOGLE_API_KEY not found in environment"
}
```

**Response** (400):
```json
{
    "error": "provider is required"
}
```

### Statistics

#### `GET /api/stats`

Get job statistics summary.

**Response**:
```json
{
    "total": 50,
    "queued": 5,
    "processing": 2,
    "pending": 10,
    "completed": 30,
    "failed": 3
}
```

**Fields**:
- `total`: Total number of jobs
- `queued`: Jobs waiting for AI (QUEUED_FOR_AI)
- `processing`: Jobs being processed (PROCESSING_AI)
- `pending`: Jobs waiting for completion (PENDING_COMPLETION)
- `completed`: Successfully completed jobs (COMPLETED)
- `failed`: Failed jobs (FAILED)

---

## JavaScript Functions

### Dashboard (index.html)

#### `loadStats()`

Fetches and updates statistics panel.

```javascript
async function loadStats() {
    const response = await fetch('/api/stats');
    const stats = await response.json();
    
    document.getElementById('stat-total').textContent = stats.total;
    document.getElementById('stat-queued').textContent = stats.queued;
    // ... update all stats
}
```

#### `loadJobs()`

Fetches and renders jobs table.

```javascript
async function loadJobs() {
    const response = await fetch('/api/jobs');
    const jobs = await response.json();
    
    // Handle empty state
    if (jobs.length === 0) {
        jobsList.innerHTML = emptyStateHTML;
        return;
    }
    
    // Build table
    let html = buildJobsTable(jobs);
    jobsList.innerHTML = html;
}
```

#### `getStatusClass(status)`

Maps job status to CSS class.

```javascript
function getStatusClass(status) {
    const statusMap = {
        'Queued for AI': 'status-queued',
        'Processing AI': 'status-processing',
        'Pending Completion': 'status-pending',
        'Completed': 'status-completed',
        'Failed': 'status-failed',
        'Manual Edit': 'status-manual'
    };
    return statusMap[status] || 'status-queued';
}
```

#### `openEditModal(jobId, currentName)`

Opens edit modal for job.

```javascript
function openEditModal(jobId, currentName) {
    currentJobId = jobId;
    document.getElementById('edit-name').value = currentName;
    document.getElementById('edit-path').value = '';
    document.getElementById('edit-modal').classList.add('active');
}
```

#### `saveEdit()`

Submits manual edit.

```javascript
async function saveEdit() {
    const newName = document.getElementById('edit-name').value;
    const newPath = document.getElementById('edit-path').value;
    
    const response = await fetch(`/api/jobs/${currentJobId}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_name: newName, new_path: newPath || null })
    });
    
    if (response.ok) {
        closeEditModal();
        loadJobs();
        loadStats();
    }
}
```

#### `openReAIModal(jobId)`

Opens Re-AI modal for job.

```javascript
function openReAIModal(jobId) {
    currentJobId = jobId;
    document.getElementById('reai-prompt').value = '';
    document.getElementById('reai-modal').classList.add('active');
}
```

#### `saveReAI()`

Submits Re-AI request.

```javascript
async function saveReAI() {
    const customPrompt = document.getElementById('reai-prompt').value;
    const includeInstructions = document.getElementById('reai-include-instructions').checked;
    const includeFilename = document.getElementById('reai-include-filename').checked;
    const enableWebSearch = document.getElementById('reai-web-search').checked;
    
    const response = await fetch(`/api/jobs/${currentJobId}/re-ai`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            custom_prompt: customPrompt || null,
            include_instructions: includeInstructions,
            include_filename: includeFilename,
            enable_web_search: enableWebSearch
        })
    });
    
    if (response.ok) {
        closeReAIModal();
        loadJobs();
        loadStats();
    }
}
```

### Settings Page (settings.html)

#### `loadConfig()`

Loads current configuration.

```javascript
async function loadConfig() {
    const response = await fetch('/api/config');
    currentConfig = await response.json();
    
    // Populate form fields
    document.getElementById('downloading-path').value = currentConfig.DOWNLOADING_PATH || '';
    document.getElementById('completed-path').value = currentConfig.COMPLETED_PATH || '';
    // ... populate all fields
    
    await loadModels();
}
```

#### `loadModels()`

Fetches and populates AI models dropdown.

```javascript
async function loadModels() {
    const modelSelect = document.getElementById('ai-model');
    const loadingIndicator = document.getElementById('model-loading');
    
    loadingIndicator.style.display = 'inline-block';
    modelSelect.disabled = true;
    
    const response = await fetch('/api/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'google' })
    });
    
    const data = await response.json();
    const models = data.models;
    
    modelSelect.innerHTML = '';
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
    
    modelSelect.value = currentConfig.AI_MODEL;
    
    loadingIndicator.style.display = 'none';
    modelSelect.disabled = false;
}
```

#### Form Submit Handler

Handles configuration save.

```javascript
document.getElementById('settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const saveBtn = document.getElementById('save-btn');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
    
    const formData = new FormData(e.target);
    const config = {};
    
    // Convert form data to config object
    for (const [key, value] of formData.entries()) {
        if (key === 'DRY_RUN_MODE' || key === 'ENABLE_WEB_SEARCH') {
            config[key] = document.getElementById(...).checked;
        } else if (key === 'DEBOUNCE_SECONDS' || key === 'AI_BATCH_SIZE') {
            config[key] = parseInt(value);
        } else {
            config[key] = value;
        }
    }
    
    const response = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    });
    
    if (response.ok) {
        showAlert('Settings saved successfully!', 'success');
    } else {
        showAlert('Error saving settings', 'error');
    }
    
    saveBtn.disabled = false;
    saveBtn.textContent = 'Save Settings';
});
```

#### `showAlert(message, type)`

Displays alert message.

```javascript
function showAlert(message, type) {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;
    
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}
```

---

## Responsive Design

### Breakpoints

| Device | Width | Layout Changes |
|--------|-------|----------------|
| Mobile Portrait | ≤768px | Single column, stacked elements |
| Mobile Landscape | ≤768px (landscape) | Optimized for horizontal space |
| Tablet | 769px-1024px | 2-3 column grids |
| Desktop | 1025px-1399px | Full layout |
| Large Desktop | ≥1400px | Expanded containers |

### Mobile Optimizations (≤768px)

**Dashboard**:
- Header stacks vertically
- Stats in 2-column grid
- Jobs table scrolls horizontally
- Action buttons stack vertically
- Modals take 95% width

**Settings**:
- Form rows become single column
- Save button full width
- Reduced padding and font sizes

### Tablet Optimizations (769px-1024px)

**Dashboard**:
- Stats in 3-column grid
- Jobs table full width
- Modals at 600px max width

**Settings**:
- Form rows stay 2-column
- Comfortable spacing

### Large Desktop (≥1400px)

**Dashboard**:
- Container expands to 1600px
- Stats in 6-column grid
- Increased padding

**Settings**:
- Container expands to 1200px
- Larger form spacing

### Landscape Mobile Optimizations

**Special handling** for landscape orientation on mobile:
- Horizontal layout maintained
- Stats in 3 columns
- Reduced vertical padding
- Modals at 85% height

---

## Summary

The frontend provides a modern, responsive interface for:

1. **Real-time Monitoring**: Auto-refreshing dashboard with live statistics
2. **Job Management**: Manual editing and Re-AI capabilities
3. **Configuration**: Comprehensive settings interface
4. **API Integration**: RESTful endpoints for all operations
5. **User Experience**: Modals, alerts, loading states
6. **Responsive Design**: Optimized for all device sizes

All JavaScript uses modern async/await patterns and the Fetch API for clean, readable code.
