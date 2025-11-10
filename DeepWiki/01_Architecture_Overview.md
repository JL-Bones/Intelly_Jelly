# Architecture Overview

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Design Principles](#core-design-principles)
3. [Architecture Diagram](#architecture-diagram)
4. [Component Relationships](#component-relationships)
5. [Technology Stack](#technology-stack)
6. [Threading Model](#threading-model)
7. [Data Flow](#data-flow)

---

## System Overview

**Intelly Jelly** is an advanced, automated media organizing application that combines a multi-threaded Python backend with a Flask-based web interface. The system intelligently processes files from a "downloading" folder, uses AI to determine appropriate file names and organization, and executes the organization when files arrive in a "completed" folder.

### Key Features

- **Automated File Monitoring**: Real-time detection of new files using file system watchers
- **AI-Powered File Naming**: Integration with Google AI (Gemini) for intelligent file renaming
- **Batch Processing**: Efficient processing of multiple files with configurable debounce timing
- **Priority Queue System**: Immediate processing of manual re-AI requests
- **Web Interface**: Beautiful, responsive UI for monitoring and configuration
- **Dynamic Configuration**: Live reload of configuration without application restart
- **Thread-Safe Operations**: Multi-threaded architecture with proper synchronization

---

## Core Design Principles

### 1. Separation of Concerns
The application is divided into distinct, loosely-coupled components:
- **Backend Orchestrator**: Coordinates all backend operations
- **Job Store**: Centralized state management
- **Configuration Manager**: Handles all configuration operations
- **AI Processor**: Isolated AI provider interactions
- **File Watchers**: Independent file system monitoring
- **Web Server**: Separate Flask application for UI

### 2. Thread Safety
All shared resources use appropriate locking mechanisms:
- `threading.RLock()` for Job Store operations
- `threading.Lock()` for debounced processor
- Thread-safe configuration reloading

### 3. Modularity
Each module has a single, well-defined responsibility and can be tested independently.

### 4. Observability
Comprehensive logging at multiple levels (INFO, DEBUG, ERROR) throughout the application.

### 5. Dynamic Configuration
Configuration changes take effect immediately without requiring application restart.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Web Server                          │
│                         (Port 7000)                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Routes:                                                  │  │
│  │  • /                    (Dashboard)                       │  │
│  │  • /settings            (Configuration UI)                │  │
│  │  • /api/jobs            (Job Management)                  │  │
│  │  • /api/config          (Config Management)               │  │
│  │  • /api/models          (AI Model Discovery)              │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Orchestrator                          │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  • Coordinates all backend operations                      ││
│  │  • Manages file watchers                                   ││
│  │  • Controls processing threads                             ││
│  │  • Handles configuration changes                           ││
│  └────────────────────────────────────────────────────────────┘│
└─────┬───────────────────────────────────────────────────────────┘
      │
      ├─────────────────┬──────────────────┬────────────────────┐
      ▼                 ▼                  ▼                    ▼
┌───────────┐  ┌────────────────┐  ┌─────────────┐  ┌──────────────┐
│  Job      │  │  Config        │  │  AI         │  │  File        │
│  Store    │  │  Manager       │  │  Processor  │  │  Watchers    │
└───────────┘  └────────────────┘  └─────────────┘  └──────────────┘
     │               │                    │                 │
     │               │                    │                 │
     │          ┌────┴────┐          ┌───┴────┐      ┌─────┴─────┐
     │          │ config  │          │ Google │      │Downloading│
     │          │  .json  │          │   AI   │      │  Watcher  │
     │          └─────────┘          │  API   │      └───────────┘
     │                               └────────┘      ┌───────────┐
     │                                               │ Completed │
     │                                               │  Watcher  │
     └───────────────────────────────────────────────└───────────┘
                Thread-Safe Job State Management

┌─────────────────────────────────────────────────────────────────┐
│                      Processing Threads                          │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  1. Downloading Watcher Thread                             ││
│  │     • Monitors DOWNLOADING_PATH for new files              ││
│  │     • Adds jobs to queue                                   ││
│  │                                                            ││
│  │  2. Completed Watcher Thread                               ││
│  │     • Monitors COMPLETED_PATH for finished downloads       ││
│  │     • Triggers file organization                           ││
│  │                                                            ││
│  │  3. Debounce Timer Thread                                  ││
│  │     • Waits for DEBOUNCE_SECONDS                           ││
│  │     • Triggers batch AI processing                         ││
│  │                                                            ││
│  │  4. Priority Queue Worker Thread                           ││
│  │     • Processes high-priority re-AI requests               ││
│  │     • Bypasses normal batch processing                     ││
│  │                                                            ││
│  │  5. Config Watcher Thread                                  ││
│  │     • Monitors config.json for changes                     ││
│  │     • Triggers live configuration reload                   ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Relationships

### Backend Components

#### 1. Backend Orchestrator
- **Purpose**: Central coordinator for all backend operations
- **Dependencies**: Job Store, Config Manager, AI Processor, File Watchers
- **Key Responsibilities**:
  - Starting/stopping all watchers and processors
  - Routing file events to appropriate handlers
  - Managing the priority queue worker
  - Responding to configuration changes

#### 2. Job Store
- **Purpose**: Thread-safe storage for all job state
- **Dependencies**: None (core data structure)
- **Key Responsibilities**:
  - Creating and tracking jobs
  - Updating job status
  - Querying jobs by status or attributes
  - Managing priority flags

#### 3. Configuration Manager
- **Purpose**: Centralized configuration management
- **Dependencies**: Watchdog library, python-dotenv
- **Key Responsibilities**:
  - Loading configuration from config.json
  - Loading secrets from .env file
  - Watching for configuration changes
  - Notifying callbacks of changes
  - Persisting configuration updates

#### 4. AI Processor
- **Purpose**: Interface to AI providers
- **Dependencies**: Config Manager, requests library
- **Key Responsibilities**:
  - Loading AI instructions
  - Formatting prompts
  - Calling Google AI API
  - Parsing AI responses
  - Discovering available models

#### 5. File Watchers
- **Purpose**: Monitor file system for changes
- **Dependencies**: Watchdog library
- **Key Responsibilities**:
  - Watching downloading folder
  - Watching completed folder
  - Triggering callbacks on file events
  - Supporting dynamic path changes

#### 6. Debounced Processor
- **Purpose**: Batch multiple file events together
- **Dependencies**: threading module
- **Key Responsibilities**:
  - Implementing debounce logic
  - Triggering batch processing
  - Supporting dynamic timing changes

### Frontend Components

#### 1. Flask Application (app.py)
- **Purpose**: Web server and API gateway
- **Dependencies**: Flask, backend modules
- **Key Responsibilities**:
  - Serving HTML pages
  - Providing REST API endpoints
  - Bridging web UI and backend
  - Managing API responses

#### 2. Dashboard (index.html)
- **Purpose**: Job monitoring interface
- **Dependencies**: Browser, Fetch API
- **Key Responsibilities**:
  - Displaying all jobs
  - Showing real-time statistics
  - Providing job editing interface
  - Enabling re-AI requests

#### 3. Settings Page (settings.html)
- **Purpose**: Configuration interface
- **Dependencies**: Browser, Fetch API
- **Key Responsibilities**:
  - Loading current configuration
  - Displaying configuration forms
  - Fetching available AI models
  - Saving configuration changes

---

## Technology Stack

### Backend
- **Python 3.x**: Core programming language
- **Flask 3.0.0**: Web framework
- **Watchdog 3.0.0**: File system monitoring
- **Requests 2.31.0**: HTTP client for AI APIs
- **python-dotenv 1.0.0**: Environment variable management

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling (modern, responsive design)
- **Vanilla JavaScript**: Interactivity (no frameworks)
- **Fetch API**: AJAX requests

### AI Integration
- **Google AI (Gemini)**: Primary AI provider
- **Google Search Retrieval**: Optional web search capability

### Development Tools
- **Git**: Version control
- **Logging**: Python's built-in logging module
- **Threading**: Python's threading module

---

## Threading Model

### Thread Overview

The application uses **6 concurrent threads**:

1. **Main Thread** (Flask Web Server)
   - Runs the Flask application
   - Serves HTTP requests
   - Blocks on `app.run()`

2. **Backend Thread** (daemon)
   - Runs the Backend Orchestrator
   - Coordinates all backend operations
   - Started by main thread before Flask

3. **Downloading Watcher Thread** (daemon)
   - Monitors DOWNLOADING_PATH
   - Created by Watchdog Observer
   - Triggers file detection callbacks

4. **Completed Watcher Thread** (daemon)
   - Monitors COMPLETED_PATH
   - Created by Watchdog Observer
   - Triggers file completion callbacks

5. **Debounce Timer Thread** (dynamic)
   - Created on-demand by DebouncedProcessor
   - Waits for DEBOUNCE_SECONDS
   - Triggers batch AI processing
   - Recreated each time debounce is triggered

6. **Priority Queue Worker Thread** (daemon)
   - Continuously polls for priority jobs
   - Processes re-AI requests immediately
   - 1-second polling interval

7. **Config Watcher Thread** (daemon)
   - Monitors config.json for changes
   - Created by Watchdog Observer
   - Triggers configuration reload

### Thread Safety Mechanisms

#### Job Store
- Uses `threading.RLock()` (reentrant lock)
- Locks all operations that read or modify job data
- Allows same thread to acquire lock multiple times

#### Configuration Manager
- Uses `threading.RLock()` for config access
- Atomic read/write operations

#### Debounced Processor
- Uses `threading.Lock()` for timer management
- Cancels existing timer before creating new one

### Thread Communication

- **Callback Pattern**: File watchers use callbacks to notify orchestrator
- **Polling Pattern**: Priority queue worker polls job store
- **Event-Driven**: Configuration changes trigger callbacks
- **Shared State**: Job Store acts as central state repository

---

## Data Flow

### Stage 1: File Detection → AI Processing

```
1. User adds file to DOWNLOADING_PATH
   ↓
2. Downloading Watcher detects file
   ↓
3. DownloadingFolderHandler.on_created() called
   ↓
4. BackendOrchestrator._on_file_detected() called
   ↓
5. JobStore.add_job() creates new job (status: QUEUED_FOR_AI)
   ↓
6. DebouncedProcessor.trigger() starts/resets timer
   ↓
7. After DEBOUNCE_SECONDS, timer fires
   ↓
8. BackendOrchestrator._process_ai_batch() called
   ↓
9. Jobs retrieved by status (QUEUED_FOR_AI)
   ↓
10. Jobs divided into batches (size: AI_BATCH_SIZE)
   ↓
11. For each batch:
    a. Jobs marked as PROCESSING_AI
    b. AIProcessor.process_batch() called
    c. Prompt constructed from instructions + file paths
    d. Request sent to Google AI API
    e. Response parsed into suggested names
    f. Jobs updated with results (status: PENDING_COMPLETION)
```

### Stage 2: File Completion → Organization

```
1. File appears in COMPLETED_PATH
   ↓
2. Completed Watcher detects file
   ↓
3. CompletedFolderHandler.on_created() called
   ↓
4. BackendOrchestrator._on_file_completed() called
   ↓
5. JobStore searched for matching job
   ↓
6. If job found with PENDING_COMPLETION status:
   a. BackendOrchestrator._organize_file() called
   b. Destination path constructed
   c. Directory created if needed
   d. File moved to LIBRARY_PATH
   e. File renamed using AI-determined name
   f. Job updated (status: COMPLETED)
```

### Stage 3: Manual Re-AI Request

```
1. User clicks "Re-AI" button in web UI
   ↓
2. JavaScript sends POST to /api/jobs/{id}/re-ai
   ↓
3. Flask route calls BackendOrchestrator.re_ai_job()
   ↓
4. Job updated:
   - status: QUEUED_FOR_AI
   - priority: True
   - custom_prompt: (user's input)
   ↓
5. Priority Queue Worker detects high-priority job
   ↓
6. Job processed immediately (bypasses batch queue)
   ↓
7. AIProcessor.process_batch() called with custom options
   ↓
8. Job updated with new AI result (status: PENDING_COMPLETION)
```

### Stage 4: Manual Edit

```
1. User clicks "Edit" button in web UI
   ↓
2. Modal opens with current values
   ↓
3. User enters new name/path and saves
   ↓
4. JavaScript sends POST to /api/jobs/{id}/edit
   ↓
5. Flask route calls BackendOrchestrator.manual_edit_job()
   ↓
6. Job updated:
   - status: MANUAL_EDIT (temporarily)
   - ai_determined_name: (user's input)
   - new_path: (user's input, optional)
   ↓
7. Job immediately updated to PENDING_COMPLETION
   ↓
8. File organization occurs when file appears in COMPLETED_PATH
```

### Configuration Update Flow

```
1. User modifies settings in web UI
   ↓
2. User clicks "Save Settings"
   ↓
3. JavaScript sends POST to /api/config
   ↓
4. Flask route calls ConfigManager.update_config()
   ↓
5. ConfigManager updates in-memory config
   ↓
6. ConfigManager writes to config.json
   ↓
7. Config Watcher detects file change
   ↓
8. ConfigManager.reload_config() called
   ↓
9. ConfigManager._notify_changes() triggers callbacks
   ↓
10. BackendOrchestrator._on_config_change() called
   ↓
11. Watchers restarted with new paths if changed
   ↓
12. Debounced processor updated with new timing if changed
```

---

## Next Steps

For detailed information about specific components:
- [Backend Components](02_Backend_Components.md)
- [Frontend Interface](03_Frontend_Interface.md)
- [API Reference](04_API_Reference.md)
- [Configuration Guide](05_Configuration_Guide.md)
- [Data Models](06_Data_Models.md)
- [Processing Workflows](07_Processing_Workflows.md)
- [AI Integration](08_AI_Integration.md)
- [File Organization Rules](09_File_Organization_Rules.md)
- [Development Guide](10_Development_Guide.md)
