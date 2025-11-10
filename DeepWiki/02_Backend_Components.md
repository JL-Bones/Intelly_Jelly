# Backend Components

## Table of Contents
1. [Job Store](#job-store)
2. [Configuration Manager](#configuration-manager)
3. [AI Processor](#ai-processor)
4. [Backend Orchestrator](#backend-orchestrator)
5. [File Watchers](#file-watchers)

---

## Job Store

**File**: `backend/job_store.py`

### Overview
The Job Store is a thread-safe, in-memory data structure that acts as the central repository for all job state in the application. It provides a simple, dictionary-based storage with proper locking mechanisms to ensure thread safety across multiple concurrent operations.

### Class: `JobStatus`

An enumeration defining all possible job states:

```python
class JobStatus(Enum):
    QUEUED_FOR_AI = "Queued for AI"
    PROCESSING_AI = "Processing AI"
    PENDING_COMPLETION = "Pending Completion"
    COMPLETED = "Completed"
    FAILED = "Failed"
    MANUAL_EDIT = "Manual Edit"
```

**Status Meanings**:
- **QUEUED_FOR_AI**: Job created, waiting for AI processing
- **PROCESSING_AI**: Currently being processed by AI
- **PENDING_COMPLETION**: AI processing complete, waiting for file to appear in completed folder
- **COMPLETED**: File successfully organized and moved to library
- **FAILED**: Error occurred during processing
- **MANUAL_EDIT**: User manually edited the job (temporary state)

### Class: `Job`

Represents a single file processing job.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `job_id` | str | Unique UUID for the job |
| `original_path` | str | Absolute path to the original file |
| `relative_path` | str | Relative path from base directory |
| `status` | JobStatus | Current job status |
| `ai_determined_name` | Optional[str] | Name suggested by AI |
| `new_path` | Optional[str] | Full path after organization |
| `confidence` | Optional[int] | AI confidence score (0-100) |
| `error_message` | Optional[str] | Error description if failed |
| `created_at` | datetime | Job creation timestamp |
| `updated_at` | datetime | Last update timestamp |
| `custom_prompt` | Optional[str] | Custom prompt for re-AI |
| `priority` | bool | Whether job is high-priority |
| `include_instructions` | bool | Include default instructions |
| `include_filename` | bool | Include filename in prompt |

#### Methods

**`__init__(original_path: str, relative_path: str)`**
- Creates a new job with default values
- Generates unique UUID
- Sets initial status to QUEUED_FOR_AI
- Records creation timestamp

**`to_dict() -> dict`**
- Converts job to JSON-serializable dictionary
- Used for API responses
- Formats datetime as ISO format strings

**`update_status(status: JobStatus, **kwargs)`**
- Updates job status
- Updates `updated_at` timestamp
- Applies any additional keyword arguments as attributes

### Class: `JobStore`

Thread-safe storage and management of all jobs.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_jobs` | Dict[str, Job] | Dictionary mapping job_id to Job |
| `_lock` | threading.RLock | Reentrant lock for thread safety |

#### Methods

**`add_job(original_path: str, relative_path: str) -> Job`**
- Creates a new job
- Adds it to the store
- Returns the created job
- Thread-safe

**`get_job(job_id: str) -> Optional[Job]`**
- Retrieves a job by ID
- Returns None if not found
- Thread-safe

**`get_job_by_path(path: str) -> Optional[Job]`**
- Finds a job matching either original_path or relative_path
- Returns first match or None
- Thread-safe

**`get_jobs_by_status(status: JobStatus) -> List[Job]`**
- Returns all jobs with the specified status
- Returns a new list (snapshot)
- Thread-safe

**`get_all_jobs() -> List[Job]`**
- Returns all jobs in the store
- Returns a new list (snapshot)
- Thread-safe

**`update_job(job_id: str, status: JobStatus, **kwargs) -> bool`**
- Updates a job's status and attributes
- Returns True if job found and updated
- Returns False if job not found
- Thread-safe

**`delete_job(job_id: str) -> bool`**
- Removes a job from the store
- Returns True if deleted
- Returns False if not found
- Thread-safe

**`get_priority_jobs() -> List[Job]`**
- Returns all jobs with priority=True and status=QUEUED_FOR_AI
- Used by priority queue worker
- Thread-safe

**`clear_completed_jobs(days: int = 7) -> int`**
- Removes completed jobs older than specified days
- Returns count of deleted jobs
- Thread-safe
- Currently not called (future feature)

### Thread Safety

The JobStore uses `threading.RLock()` (reentrant lock) to ensure thread safety:

- **All methods** acquire the lock before accessing `_jobs`
- **RLock** allows the same thread to acquire the lock multiple times
- **Context manager** (`with self._lock:`) ensures lock is always released

### Usage Examples

```python
# Initialize
job_store = JobStore()

# Add a new job
job = job_store.add_job(
    original_path="/downloads/movie.mkv",
    relative_path="movie.mkv"
)

# Update job status
job_store.update_job(
    job.job_id,
    JobStatus.PROCESSING_AI
)

# Update with additional attributes
job_store.update_job(
    job.job_id,
    JobStatus.PENDING_COMPLETION,
    ai_determined_name="Movie Title (2020).mkv",
    confidence=95
)

# Query jobs
queued_jobs = job_store.get_jobs_by_status(JobStatus.QUEUED_FOR_AI)
priority_jobs = job_store.get_priority_jobs()

# Get specific job
job = job_store.get_job(job_id)
```

---

## Configuration Manager

**File**: `backend/config_manager.py`

### Overview
The Configuration Manager handles all configuration operations, including loading from files, watching for changes, and notifying subscribers of updates. It separates public configuration (config.json) from secret configuration (.env).

### Class: `ConfigChangeHandler`

File system event handler for config.json changes.

#### Methods

**`on_modified(event)`**
- Triggered when config.json is modified
- Calls `config_manager.reload_config()`

### Class: `ConfigManager`

Main configuration management class.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `config_path` | str | Path to config.json |
| `env_path` | str | Path to .env file |
| `_config` | Dict[str, Any] | In-memory configuration |
| `_lock` | threading.RLock | Thread safety lock |
| `_observers` | List[Observer] | File watchers |
| `_change_callbacks` | List[Callable] | Change notification callbacks |

#### Methods

**`__init__(config_path: str = 'config.json', env_path: str = '.env')`**
- Initializes configuration manager
- Loads environment variables from .env
- Loads initial configuration
- Starts file watcher

**`reload_config()`**
- Reloads config.json from disk
- Compares old vs new configuration
- Notifies callbacks if changes detected
- Falls back to defaults if file not found
- Thread-safe

**`_get_default_config() -> Dict[str, Any]`**
Returns default configuration:
```python
{
    "DOWNLOADING_PATH": "./test_folders/downloading",
    "COMPLETED_PATH": "./test_folders/completed",
    "LIBRARY_PATH": "./test_folders/library",
    "INSTRUCTIONS_FILE_PATH": "./instructions.md",
    "DEBOUNCE_SECONDS": 5,
    "AI_BATCH_SIZE": 10,
    "AI_PROVIDER": "google",
    "AI_MODEL": "gemini-pro",
    "DRY_RUN_MODE": False,
    "ENABLE_WEB_SEARCH": False
}
```

**`_start_watching()`**
- Creates file watcher for config.json
- Uses Watchdog Observer
- Monitors parent directory for changes

**`get(key: str, default: Any = None) -> Any`**
- Retrieves a configuration value
- Returns default if key not found
- Thread-safe

**`get_all() -> Dict[str, Any]`**
- Returns copy of entire configuration
- Thread-safe

**`set(key: str, value: Any)`**
- Sets a configuration value in memory
- Does not persist to disk
- Thread-safe

**`save() -> bool`**
- Writes current configuration to config.json
- Returns True on success
- Returns False on error
- Thread-safe

**`update_config(updates: Dict[str, Any]) -> bool`**
- Updates multiple configuration values
- Automatically saves to disk
- Returns success status
- Thread-safe

**`get_env(key: str, default: Optional[str] = None) -> Optional[str]`**
- Retrieves environment variable from .env
- Used for API keys and secrets
- Not thread-locked (os.getenv is thread-safe)

**`register_change_callback(callback: Callable)`**
- Registers a function to be called on config changes
- Callback signature: `callback(old_config: Dict, new_config: Dict)`

**`_notify_changes(old_config: Dict, new_config: Dict)`**
- Calls all registered callbacks
- Catches and logs callback exceptions
- Doesn't stop on individual callback failures

**`stop()`**
- Stops all file watchers
- Cleanup method

### Configuration Flow

```
1. ConfigManager initialized
   ↓
2. .env loaded via python-dotenv
   ↓
3. config.json loaded
   ↓
4. File watcher started
   ↓
5. Application runs
   ↓
6. User changes config via web UI
   ↓
7. Flask calls update_config()
   ↓
8. Config saved to config.json
   ↓
9. File watcher detects change
   ↓
10. reload_config() called
   ↓
11. Old vs new compared
   ↓
12. Callbacks notified
   ↓
13. Backend components update
```

### Usage Examples

```python
# Initialize
config = ConfigManager()

# Get value
downloading_path = config.get('DOWNLOADING_PATH')

# Get with default
batch_size = config.get('AI_BATCH_SIZE', 10)

# Get all config
all_config = config.get_all()

# Update config
config.update_config({
    'DEBOUNCE_SECONDS': 10,
    'AI_BATCH_SIZE': 20
})

# Get secret from .env
api_key = config.get_env('GOOGLE_API_KEY')

# Register for changes
def on_change(old, new):
    print(f"Config changed: {old} -> {new}")

config.register_change_callback(on_change)
```

---

## AI Processor

**File**: `backend/ai_processor.py`

### Overview
The AI Processor handles all interactions with AI providers. Currently supports Google AI (Gemini) with optional web search capability.

### Class: `AIProcessor`

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `config_manager` | ConfigManager | Reference to config manager |

#### Methods

**`__init__(config_manager: ConfigManager)`**
- Initializes AI processor
- Stores reference to config manager

**`_get_instructions() -> str`**
- Reads instructions from file specified in config
- Falls back to default instructions if file not found
- Returns instruction text

Default instructions if file missing:
```
"Suggest improved file names for the following files. 
Return JSON array with original_path, suggested_name, and confidence (0-100)."
```

**`_prepare_batch_prompt(file_paths: List[str], custom_prompt: Optional[str], include_default: bool, include_filename: bool) -> str`**

Constructs the full prompt for AI processing.

Parameters:
- `file_paths`: List of file paths to process
- `custom_prompt`: Optional user-provided prompt
- `include_default`: Whether to include default instructions
- `include_filename`: Whether to include filenames in prompt

Prompt structure:
```
[Default Instructions (if include_default)]

[Additional instructions: {custom_prompt} (if provided)]

[Files to process: (if include_filename)]
[- file1]
[- file2]
[OR]
[Number of files to process: N (if not include_filename)]
```

**`process_batch(file_paths: List[str], custom_prompt: Optional[str] = None, include_default: bool = True, include_filename: bool = True, enable_web_search: bool = False) -> List[Dict]`**

Main method for AI processing.

**Parameters**:
- `file_paths`: List of file paths to process
- `custom_prompt`: Optional custom instructions
- `include_default`: Include default instructions from file
- `include_filename`: Include actual filenames in prompt
- `enable_web_search`: Enable Google search retrieval

**Returns**: List of dictionaries with structure:
```python
[
    {
        "original_path": "file1.mkv",
        "suggested_name": "Movie Title (2020).mkv",
        "confidence": 95
    },
    ...
]
```

**Process**:
1. Validates Google API key exists
2. Gets AI model from config
3. Prepares prompt
4. Constructs API request
5. Sends POST to Google AI API
6. Parses JSON response
7. Returns results

**API Request Structure** (without web search):
```json
{
    "contents": [{
        "parts": [{"text": "{prompt}"}]
    }],
    "generationConfig": {
        "temperature": 0.7,
        "topK": 1,
        "topP": 1,
        "maxOutputTokens": 2048
    }
}
```

**API Request Structure** (with web search):
```json
{
    "contents": [...],
    "generationConfig": {...},
    "tools": [{
        "googleSearchRetrieval": {}
    }]
}
```

**Response Parsing**:
- Extracts text from `candidates[0].content.parts[0].text`
- Strips markdown code blocks (```json and ```)
- Parses as JSON
- Handles both array and object formats
- Returns empty list on errors

**Error Handling**:
- `requests.exceptions.HTTPError`: API errors
- `json.JSONDecodeError`: Invalid JSON response
- `KeyError`: Unexpected response structure
- All errors logged with full details

**`get_available_models(provider: Optional[str] = None) -> List[str]`**

Fetches list of available models from Google AI.

**Returns**: Sorted list of model names

**Process**:
1. Gets Google API key
2. Calls `/v1beta/models` endpoint
3. Extracts model names
4. Removes "models/" prefix
5. Sorts alphabetically
6. Returns list

**`_get_google_models() -> List[str]`**

Internal method for fetching Google models.

### AI Integration Details

**Google AI API Endpoints**:
- Content Generation: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}`
- Model List: `https://generativelanguage.googleapis.com/v1beta/models?key={api_key}`

**Supported Models**:
- `gemini-pro`
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- And others returned by API

**Generation Parameters**:
- **temperature**: 0.7 (balance creativity/consistency)
- **topK**: 1 (most likely token)
- **topP**: 1 (consider all tokens)
- **maxOutputTokens**: 2048 (max response length)

### Usage Examples

```python
# Initialize
ai_processor = AIProcessor(config_manager)

# Basic batch processing
results = ai_processor.process_batch([
    "movie.2020.1080p.mkv",
    "show.s01e01.hdtv.mp4"
])

# With custom prompt
results = ai_processor.process_batch(
    file_paths=["album.zip"],
    custom_prompt="This is a music album",
    include_default=True,
    include_filename=True
)

# With web search enabled
results = ai_processor.process_batch(
    file_paths=["obscure_movie_2023.mkv"],
    enable_web_search=True
)

# Get available models
models = ai_processor.get_available_models()
# Returns: ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', ...]
```

---

## Backend Orchestrator

**File**: `backend/backend_orchestrator.py`

### Overview
The Backend Orchestrator is the central coordinator that manages all backend operations. It ties together the Job Store, Configuration Manager, AI Processor, and File Watchers, orchestrating the complete workflow from file detection to organization.

### Class: `BackendOrchestrator`

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `config_manager` | ConfigManager | Configuration management |
| `job_store` | JobStore | Job state storage |
| `ai_processor` | AIProcessor | AI integration |
| `downloading_watcher` | Optional[FileWatcher] | Downloading folder watcher |
| `completed_watcher` | Optional[FileWatcher] | Completed folder watcher |
| `debounced_processor` | Optional[DebouncedProcessor] | Batch timer |
| `priority_thread` | Optional[threading.Thread] | Priority queue thread |
| `priority_running` | bool | Priority thread running flag |
| `_running` | bool | Orchestrator running flag |

#### Methods

**`__init__(config_manager: ConfigManager, job_store: JobStore)`**
- Initializes orchestrator
- Creates AI processor
- Initializes watcher references as None
- Registers configuration change callback
- Sets running flags to False

**`start()`**

Starts all backend operations.

**Process**:
1. Checks if already running (prevents double-start)
2. Sets running flag
3. Gets configuration values
4. Creates downloading folder handler and watcher
5. Creates completed folder handler and watcher
6. Starts both watchers
7. Creates debounced processor with callback
8. Starts priority queue worker thread
9. Logs startup completion

**`stop()`**

Stops all backend operations.

**Process**:
1. Checks if running
2. Sets running flags to False
3. Stops downloading watcher
4. Stops completed watcher
5. Stops debounced processor
6. Joins priority thread (5 second timeout)
7. Logs shutdown completion

**`_on_file_detected(file_path: str, relative_path: str)`**

Callback when file detected in downloading folder.

**Process**:
1. Logs file detection
2. Checks if job already exists for this path
3. If exists, logs warning and returns
4. Creates new job in job store
5. Triggers debounced processor

**`_process_ai_batch()`**

Callback when debounce timer completes.

**Process**:
1. Gets all QUEUED_FOR_AI jobs
2. Filters out priority jobs (handled separately)
3. If no jobs, returns
4. Divides jobs into batches (AI_BATCH_SIZE)
5. Processes each batch via `_process_batch()`

**`_process_batch(jobs: List[Job])`**

Processes a batch of jobs through AI.

**Process**:
1. Validates batch not empty
2. Updates all jobs to PROCESSING_AI
3. Extracts relative paths
4. Calls `ai_processor.process_batch()`
5. Matches results to jobs
6. Updates jobs with AI results:
   - Success: PENDING_COMPLETION with suggested_name and confidence
   - No result: FAILED with error message
7. Catches exceptions and marks all jobs as FAILED on error

**`_priority_queue_worker()`**

Background thread for processing priority jobs.

**Infinite Loop** (while priority_running):
1. Get all priority jobs from store
2. If priority job found:
   a. Take first job
   b. Update to PROCESSING_AI
   c. Extract custom options (prompt, flags, web search)
   d. Call AI processor with single file
   e. Update job with result or mark as FAILED
   f. Clear priority flag
3. Sleep 1 second
4. Repeat

**Handles exceptions**: Logs errors and continues running

**`_on_file_completed(file_path: str, relative_path: str)`**

Callback when file appears in completed folder.

**Process**:
1. Logs file detection
2. Searches for matching job (multiple strategies):
   a. By relative_path
   b. By filename only
   c. Iterate all jobs matching relative_path
   d. Iterate all jobs matching basename
3. If no job found, logs warning and returns
4. Validates job status (PENDING_COMPLETION or MANUAL_EDIT)
5. Calls `_organize_file()` to move/rename

**`_organize_file(job: Job, file_path: str)`**

Organizes and moves file to library.

**Process**:
1. Gets library path and dry run mode from config
2. Determines new filename from job
3. Constructs destination path:
   - If job has custom new_path, use it
   - Otherwise use library_path + ai_determined_name
4. Creates destination directory
5. Handles filename conflicts (appends _1, _2, etc.)
6. Moves file (or logs in dry run mode)
7. Updates job to COMPLETED with new_path
8. On error, marks job as FAILED

**`_on_config_change(old_config: Dict, new_config: Dict)`**

Callback when configuration changes.

**Process**:
1. Compares old vs new DOWNLOADING_PATH
2. If changed, restarts downloading watcher with new path
3. Compares old vs new COMPLETED_PATH
4. If changed, restarts completed watcher with new path
5. Compares old vs new DEBOUNCE_SECONDS
6. If changed, updates debounced processor timing

**`manual_edit_job(job_id: str, new_name: str, new_path: Optional[str] = None) -> bool`**

Handles manual job editing from web UI.

**Process**:
1. Gets job by ID
2. If not found, returns False
3. Updates job:
   - Status: MANUAL_EDIT (temporary)
   - ai_determined_name: user's input
   - new_path: user's input (optional)
4. Immediately updates status to PENDING_COMPLETION
5. Returns True

**`re_ai_job(job_id: str, custom_prompt: Optional[str] = None, include_instructions: bool = True, include_filename: bool = True, enable_web_search: bool = False) -> bool`**

Handles re-AI request from web UI.

**Process**:
1. Gets job by ID
2. If not found, returns False
3. Updates job:
   - Status: QUEUED_FOR_AI
   - priority: True
   - custom_prompt: user's input
   - include_instructions: flag
   - include_filename: flag
   - enable_web_search: flag
4. Priority queue worker will process immediately
5. Returns True

### Orchestration Flow

```
Backend Start:
├─ Create file watchers
├─ Start watching folders
├─ Create debounced processor
├─ Start priority thread
└─ Register config callback

File Detection:
├─ File appears in downloading
├─ Watcher triggers callback
├─ Create job (QUEUED_FOR_AI)
├─ Trigger debounce timer
└─ Wait for timer

Batch Processing:
├─ Timer completes
├─ Get all queued jobs
├─ Filter non-priority
├─ Divide into batches
├─ Process each batch
│  ├─ Mark as PROCESSING_AI
│  ├─ Call AI API
│  ├─ Parse results
│  └─ Update to PENDING_COMPLETION
└─ Wait for file completion

File Completion:
├─ File appears in completed
├─ Watcher triggers callback
├─ Find matching job
├─ Validate status
├─ Organize file
│  ├─ Determine destination
│  ├─ Create directories
│  ├─ Move and rename
│  └─ Update to COMPLETED
└─ Job complete

Priority Processing:
├─ User clicks Re-AI
├─ Job marked priority=True
├─ Priority thread detects
├─ Process immediately
│  ├─ Mark as PROCESSING_AI
│  ├─ Call AI with custom options
│  ├─ Update result
│  └─ Clear priority flag
└─ Back to normal flow
```

### Usage Examples

```python
# Initialize
config_manager = ConfigManager()
job_store = JobStore()
orchestrator = BackendOrchestrator(config_manager, job_store)

# Start backend
orchestrator.start()

# Manual edit (called by Flask)
success = orchestrator.manual_edit_job(
    job_id="abc-123",
    new_name="My Movie (2020).mkv",
    new_path="Movies/Action/My Movie (2020).mkv"
)

# Re-AI with custom prompt
success = orchestrator.re_ai_job(
    job_id="abc-123",
    custom_prompt="This is a documentary",
    include_instructions=True,
    include_filename=True,
    enable_web_search=True
)

# Stop backend
orchestrator.stop()
```

---

## File Watchers

**File**: `backend/file_watcher.py`

### Overview
The File Watchers module provides classes for monitoring file system changes using the Watchdog library. It includes handlers for downloading and completed folders, a generic watcher wrapper, and a debounced processor for batch timing.

### Class: `DownloadingFolderHandler`

Handles file events in the downloading folder.

**Extends**: `FileSystemEventHandler` (from Watchdog)

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `callback` | Callable | Function to call on file events |
| `base_path` | str | Base path being monitored |

#### Methods

**`__init__(callback: Callable[[str, str], None], base_path: str)`**
- Stores callback and base path
- Callback signature: `callback(file_path, relative_path)`

**`update_base_path(new_base_path: str)`**
- Updates base path for relative path calculation
- Used when configuration changes

**`on_created(event)`**
- Triggered when file created
- Ignores directories
- Calculates relative path
- Calls callback with paths

**`on_moved(event)`**
- Triggered when file moved into folder
- Ignores directories
- Uses destination path
- Calculates relative path
- Calls callback with paths

### Class: `CompletedFolderHandler`

Handles file events in the completed folder.

**Extends**: `FileSystemEventHandler`

Identical to `DownloadingFolderHandler` - separated for clarity and future extensibility.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `callback` | Callable | Function to call on file events |
| `base_path` | str | Base path being monitored |

#### Methods

Same as `DownloadingFolderHandler`:
- `__init__(callback, base_path)`
- `update_base_path(new_base_path)`
- `on_created(event)`
- `on_moved(event)`

### Class: `FileWatcher`

Generic wrapper for Watchdog Observer.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `path` | str | Path to watch |
| `handler` | FileSystemEventHandler | Event handler |
| `observer` | Optional[Observer] | Watchdog observer |
| `_running` | bool | Running status flag |

#### Methods

**`__init__(path: str, handler: FileSystemEventHandler)`**
- Stores path and handler
- Observer created on start, not in constructor

**`start()`**
- Creates watched directory if it doesn't exist
- Creates Observer instance
- Schedules handler for recursive watching
- Starts observer thread
- Sets running flag

**`stop()`**
- Stops observer
- Waits for observer thread to finish
- Sets running flag to False

**`restart(new_path: str)`**
- Stops current observer
- Updates path
- Starts new observer
- Used when configuration changes

### Class: `DebouncedProcessor`

Implements debounce logic for batch processing.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `debounce_seconds` | int | Wait time before processing |
| `process_callback` | Callable | Function to call when timer fires |
| `_timer` | Optional[threading.Timer] | Current timer |
| `_lock` | threading.Lock | Thread safety lock |

#### Methods

**`__init__(debounce_seconds: int, process_callback: Callable)`**
- Stores timing and callback
- Initializes lock
- Timer created on first trigger

**`trigger()`**

Starts or resets the debounce timer.

**Process**:
1. Acquire lock
2. Cancel existing timer if running
3. Create new Timer with debounce_seconds
4. Start timer
5. Release lock

**`_execute()`**

Internal callback when timer completes.

**Process**:
1. Try to call process_callback
2. Catch and log any exceptions
3. Timer is not recreated (one-shot)

**`stop()`**
- Cancels current timer
- Clears timer reference

**`update_debounce_time(new_seconds: int)`**
- Updates debounce_seconds
- Affects next trigger
- Does not affect currently running timer

### Debounce Logic

```
File 1 arrives → Trigger (start 5s timer)
  ↓
File 2 arrives (2s later) → Trigger (cancel old timer, start new 5s timer)
  ↓
File 3 arrives (3s later) → Trigger (cancel old timer, start new 5s timer)
  ↓
No more files for 5s → Timer completes → Process batch
```

### Usage Examples

```python
# Create handlers
downloading_handler = DownloadingFolderHandler(
    callback=on_file_detected,
    base_path="/downloads"
)

completed_handler = CompletedFolderHandler(
    callback=on_file_completed,
    base_path="/completed"
)

# Create watchers
downloading_watcher = FileWatcher(
    path="/downloads",
    handler=downloading_handler
)

completed_watcher = FileWatcher(
    path="/completed",
    handler=completed_handler
)

# Start watching
downloading_watcher.start()
completed_watcher.start()

# Create debounced processor
debouncer = DebouncedProcessor(
    debounce_seconds=5,
    process_callback=process_batch
)

# Trigger on file detection
def on_file_detected(file_path, relative_path):
    create_job(file_path, relative_path)
    debouncer.trigger()

# Update paths
downloading_handler.update_base_path("/new/downloads")
downloading_watcher.restart("/new/downloads")

# Update timing
debouncer.update_debounce_time(10)

# Stop watchers
downloading_watcher.stop()
completed_watcher.stop()
debouncer.stop()
```

### Event Types Handled

**File Events**:
- `on_created`: New file appears in folder
- `on_moved`: File moved into folder

**Not Handled**:
- `on_modified`: File content changed (ignored)
- `on_deleted`: File removed (ignored)
- Directory events (filtered out)

### Thread Safety

**FileWatcher**:
- Observer runs in separate thread
- Callbacks executed in observer thread
- Handler methods must be thread-safe

**DebouncedProcessor**:
- Uses `threading.Lock()` for timer management
- Timer executes callback in separate thread
- Callback must be thread-safe

---

## Summary

The backend components work together to provide a robust, thread-safe system for automated file processing:

1. **Job Store**: Central state management with thread-safe operations
2. **Configuration Manager**: Dynamic configuration with live reload
3. **AI Processor**: Clean interface to Google AI API
4. **Backend Orchestrator**: Coordinates all operations and workflow
5. **File Watchers**: Real-time file system monitoring with debouncing

All components use proper logging, error handling, and thread synchronization to ensure reliable operation in a multi-threaded environment.
