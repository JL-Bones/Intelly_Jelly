# Processing Workflows & Data Flow

## Table of Contents
1. [Complete Workflow Overview](#complete-workflow-overview)
2. [Automated Processing Flow](#automated-processing-flow)
3. [Manual Intervention Workflows](#manual-intervention-workflows)
4. [Priority Queue Processing](#priority-queue-processing)
5. [Configuration Change Flow](#configuration-change-flow)
6. [Error Handling & Recovery](#error-handling--recovery)
7. [State Transitions](#state-transitions)
8. [Timing & Performance](#timing--performance)

---

## Complete Workflow Overview

### System Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION START                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ├─► Load .env (API keys)
                        ├─► Load config.json
                        ├─► Initialize components
                        ├─► Start backend thread
                        │   ├─► Start file watchers
                        │   ├─► Start debounced processor
                        │   └─► Start priority queue worker
                        └─► Start Flask web server (port 7000)
                        
┌─────────────────────────────────────────────────────────────┐
│                    NORMAL OPERATION                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ├─► Monitor downloading folder
                        ├─► Monitor completed folder
                        ├─► Process AI batches
                        ├─► Process priority requests
                        ├─► Handle web UI requests
                        └─► Watch for config changes
                        
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION SHUTDOWN                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ├─► Stop file watchers
                        ├─► Stop debounced processor
                        ├─► Stop priority queue worker
                        ├─► Stop config watcher
                        └─► Flask server terminates
```

---

## Automated Processing Flow

### Stage 1: File Detection & Queuing

```
User Action: Add file to DOWNLOADING_PATH
         │
         ▼
┌─────────────────────────────────────────┐
│  Watchdog Observer detects file event   │
│  (on_created or on_moved)                │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  DownloadingFolderHandler triggered     │
│  • Calculate relative path               │
│  • Call orchestrator callback            │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  BackendOrchestrator._on_file_detected()│
│  • Check if job already exists           │
│  • If exists, log warning and return     │
│  • If new, continue...                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  JobStore.add_job()                     │
│  • Generate UUID                         │
│  • Set status: QUEUED_FOR_AI            │
│  • Set timestamps                        │
│  • Store in job dictionary               │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  DebouncedProcessor.trigger()           │
│  • Cancel existing timer (if any)        │
│  • Start new timer (DEBOUNCE_SECONDS)   │
└─────────────────────────────────────────┘

Result: Job created and waiting for batch processing
```

**Timing**: Instant (milliseconds)

**Logging**:
```
INFO: File detected in downloading folder: movie.mkv
INFO: Created job abc-123 for movie.mkv
DEBUG: Triggered debounced processor
```

### Stage 2: Batch Processing & AI Analysis

```
Timer Completes (No new files for DEBOUNCE_SECONDS)
         │
         ▼
┌─────────────────────────────────────────┐
│  DebouncedProcessor._execute()          │
│  • Call process_callback                 │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  BackendOrchestrator._process_ai_batch()│
│  • Get all QUEUED_FOR_AI jobs            │
│  • Filter out priority jobs              │
│  • If none, return                       │
│  • Divide into batches (AI_BATCH_SIZE)  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        For each batch:
┌─────────────────────────────────────────┐
│  BackendOrchestrator._process_batch()   │
│  • Update all jobs: PROCESSING_AI        │
│  • Extract relative paths                │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  AIProcessor.process_batch()            │
│  • Get Google API key                    │
│  • Load instructions from file           │
│  • Prepare prompt                        │
│  • Construct API request                 │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  POST to Google AI API                  │
│  • URL: /v1beta/models/{model}:generate │
│  • Body: prompt + config                 │
│  • Wait for response...                  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Parse AI Response                      │
│  • Extract JSON from response            │
│  • Strip markdown code blocks            │
│  • Parse as array or object              │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Match Results to Jobs                  │
│  For each job:                           │
│    • Find matching result by path        │
│    • If found:                           │
│      - Update: PENDING_COMPLETION        │
│      - Set ai_determined_name            │
│      - Set confidence                    │
│    • If not found:                       │
│      - Update: FAILED                    │
│      - Set error_message                 │
└─────────────────────────────────────────┘

Result: Jobs updated with AI suggestions
```

**Timing**: 
- Debounce wait: 5 seconds (default)
- AI API call: 2-10 seconds (depends on batch size)
- Total: ~7-15 seconds from last file

**Logging**:
```
INFO: Processing AI batch...
INFO: Found 3 jobs to process with batch size 10
INFO: Processing batch of 3 jobs
DEBUG: Job IDs in batch: [abc-123, def-456, ghi-789]
INFO: Sending 3 files to AI processor
INFO: Using AI model: gemini-pro
INFO: Received 3 results from AI processor
INFO: Job abc-123 completed: movie.mkv -> Movie Title (2020).mkv (confidence: 95%)
```

### Stage 3: File Completion & Organization

```
User Action: File appears in COMPLETED_PATH
         │
         ▼
┌─────────────────────────────────────────┐
│  Watchdog Observer detects file event   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  CompletedFolderHandler triggered       │
│  • Calculate relative path               │
│  • Call orchestrator callback            │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  BackendOrchestrator._on_file_completed()│
│  • Search for matching job               │
│    Strategy 1: By relative_path          │
│    Strategy 2: By filename only          │
│    Strategy 3: Iterate all jobs          │
│    Strategy 4: Match by basename         │
└──────────────────┬──────────────────────┘
                   │
                   ├─► Job found? ──No──► Log warning & return
                   │
                   Yes
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Validate Job Status                    │
│  • Check: PENDING_COMPLETION or          │
│           MANUAL_EDIT                    │
│  • If wrong status, log warning & return │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  BackendOrchestrator._organize_file()   │
│  • Get LIBRARY_PATH from config          │
│  • Get DRY_RUN_MODE flag                 │
│  • Determine new filename                │
│    - Use ai_determined_name if available │
│    - Or use original name                │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Construct Destination Path             │
│  • If job.new_path exists:               │
│    destination = LIBRARY_PATH + new_path │
│  • Else:                                 │
│    destination = LIBRARY_PATH + new_name │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Create Directory & Handle Conflicts    │
│  • Create destination directory          │
│  • If file exists, append _1, _2, etc.  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Move File                              │
│  • If DRY_RUN_MODE:                      │
│    - Log what would happen               │
│    - Don't actually move                 │
│  • Else:                                 │
│    - shutil.move(source, destination)    │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Update Job                             │
│  • Status: COMPLETED                     │
│  • new_path: final destination           │
│  • updated_at: current timestamp         │
└─────────────────────────────────────────┘

Result: File organized in library
```

**Timing**: Instant (< 1 second)

**Logging**:
```
INFO: File appeared in completed folder: movie.mkv
DEBUG: Full path: C:/completed/movie.mkv
INFO: Found matching job abc-123 for movie.mkv
INFO: Organizing file for job abc-123: C:/completed/movie.mkv
DEBUG: Library path: C:/library, Dry run: False
DEBUG: Target name: Movie Title (2020).mkv
DEBUG: Destination file: C:/library/Movies/Movie Title (2020).mkv
INFO: Successfully moved file: C:/completed/movie.mkv -> C:/library/Movies/Movie Title (2020).mkv
INFO: Job abc-123 marked as COMPLETED
```

---

## Manual Intervention Workflows

### Manual Edit Workflow

```
User clicks "Edit" button in web UI
         │
         ▼
┌─────────────────────────────────────────┐
│  Frontend: openEditModal(jobId, name)  │
│  • Display modal with current values     │
│  • User enters new name                  │
│  • User optionally enters new path       │
│  • User clicks "Save"                    │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Frontend: saveEdit()                   │
│  • Validate new_name is not empty        │
│  • Collect form values                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  POST /api/jobs/{job_id}/edit           │
│  Body: {                                 │
│    "new_name": "My Movie (2020).mkv",   │
│    "new_path": "Movies/Action/..."      │
│  }                                       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Flask: edit_job()                      │
│  • Validate request data                 │
│  • Extract new_name and new_path         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  BackendOrchestrator.manual_edit_job()  │
│  • Get job from store                    │
│  • Update job:                           │
│    - status: MANUAL_EDIT (temporary)     │
│    - ai_determined_name: user's input    │
│    - new_path: user's input              │
│  • Immediately update to:                │
│    - status: PENDING_COMPLETION          │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Return success response                │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Frontend: Close modal & refresh        │
│  • Close edit modal                      │
│  • Reload jobs table                     │
│  • Reload statistics                     │
└─────────────────────────────────────────┘
         │
         ▼
File organization continues normally when file appears in completed folder

Result: Job updated with manual values
```

**Use Cases**:
- AI suggestion incorrect
- User prefers different naming
- Custom subfolder needed
- Special characters required

**Timing**: Instant (< 1 second)

### Re-AI Workflow

```
User clicks "Re-AI" button in web UI
         │
         ▼
┌─────────────────────────────────────────┐
│  Frontend: openReAIModal(jobId)        │
│  • Display modal with options            │
│  • User enters custom prompt (optional)  │
│  • User sets checkboxes:                 │
│    - Include instructions.txt            │
│    - Include original filename           │
│    - Enable web search                   │
│  • User clicks "Regen"                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Frontend: saveReAI()                   │
│  • Collect all form values               │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  POST /api/jobs/{job_id}/re-ai          │
│  Body: {                                 │
│    "custom_prompt": "...",               │
│    "include_instructions": true,         │
│    "include_filename": true,             │
│    "enable_web_search": false            │
│  }                                       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Flask: re_ai_job()                     │
│  • Extract request data                  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  BackendOrchestrator.re_ai_job()        │
│  • Get job from store                    │
│  • Update job:                           │
│    - status: QUEUED_FOR_AI               │
│    - priority: True                      │
│    - custom_prompt: user's input         │
│    - include_instructions: flag          │
│    - include_filename: flag              │
│    - enable_web_search: flag             │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Priority Queue Worker detects job     │
│  (within 1 second)                       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        See Priority Queue Processing section below

Result: Job reprocessed with custom options
```

**Use Cases**:
- AI suggestion not specific enough
- Need web search for obscure media
- Want to test different prompts
- Original processing failed

**Timing**: 
- Queue detection: < 1 second
- AI processing: 2-10 seconds
- Total: ~3-11 seconds

---

## Priority Queue Processing

### Priority Queue Worker Thread

**Continuous Loop**:

```python
while priority_running:
    try:
        # Get priority jobs
        priority_jobs = job_store.get_priority_jobs()
        
        if priority_jobs:
            job = priority_jobs[0]  # Take first
            
            # Process immediately
            ...
        
        # Sleep before next check
        time.sleep(1)
    except Exception as e:
        log error
        continue
```

### Priority Job Processing Flow

```
Priority Queue Worker (polls every 1 second)
         │
         ▼
┌─────────────────────────────────────────┐
│  JobStore.get_priority_jobs()           │
│  • Query: priority=True AND              │
│           status=QUEUED_FOR_AI           │
└──────────────────┬──────────────────────┘
                   │
                   ├─► No jobs? ──► Sleep 1s ──► Loop
                   │
                   Job found!
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Take First Priority Job                │
│  • Update status: PROCESSING_AI          │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Extract Job Settings                   │
│  • custom_prompt (if provided)           │
│  • include_instructions flag             │
│  • include_filename flag                 │
│  • enable_web_search flag                │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  AIProcessor.process_batch()            │
│  • Single file only                      │
│  • With custom settings                  │
│  • Bypasses normal batch queue           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Update Job with Result                 │
│  • If success:                           │
│    - status: PENDING_COMPLETION          │
│    - ai_determined_name: new result      │
│    - confidence: new score               │
│  • If failure:                           │
│    - status: FAILED                      │
│    - error_message: error details        │
│  • Always:                               │
│    - priority: False (clear flag)        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
         Sleep 1s & Loop

Result: High-priority job processed immediately
```

**Key Features**:
- **Immediate Processing**: Bypasses batch queue
- **One at a Time**: Sequential processing
- **Custom Options**: Respects all user settings
- **Error Isolation**: Errors don't stop queue
- **Priority Clearing**: Flag removed after processing

**Timing**:
- Detection latency: < 1 second
- Processing: 2-10 seconds
- Total: ~3-11 seconds

---

## Configuration Change Flow

### Configuration Update via Web UI

```
User modifies settings in web UI
         │
         ▼
┌─────────────────────────────────────────┐
│  User clicks "Save Settings"            │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Frontend: Form submit handler          │
│  • Collect all form values               │
│  • Convert types (int, bool, string)     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  POST /api/config                       │
│  Body: { ...all config values... }      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Flask: update_config()                 │
│  • Validate allowed fields               │
│  • Filter to allowed fields only         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  ConfigManager.update_config()          │
│  • Update in-memory config               │
│  • Write to config.json                  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  File System: config.json modified      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Config Watcher detects change          │
│  (Watchdog Observer)                     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  ConfigChangeHandler.on_modified()      │
│  • Check: is config.json?                │
│  • If yes, continue...                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  ConfigManager.reload_config()          │
│  • Read config.json                      │
│  • Parse JSON                            │
│  • Compare old vs new                    │
└──────────────────┬──────────────────────┘
                   │
                   ├─► Same? ──► No callbacks ──► Done
                   │
                   Different!
                   │
                   ▼
┌─────────────────────────────────────────┐
│  ConfigManager._notify_changes()        │
│  • Call all registered callbacks         │
│  • Pass old_config and new_config        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  BackendOrchestrator._on_config_change()│
└──────────────────┬──────────────────────┘
                   │
                   ├─► DOWNLOADING_PATH changed?
                   │   ├─► Update handler base_path
                   │   └─► Restart watcher with new path
                   │
                   ├─► COMPLETED_PATH changed?
                   │   ├─► Update handler base_path
                   │   └─► Restart watcher with new path
                   │
                   └─► DEBOUNCE_SECONDS changed?
                       └─► Update debounced processor timing
                       
Result: Configuration live-reloaded
```

**What Updates Live**:
✅ Folder paths (watchers restart)
✅ Debounce timing (processor updates)
✅ AI model (next batch uses new model)
✅ Batch size (next batch uses new size)
✅ Dry run mode (immediate effect)
✅ Web search flag (next batch uses flag)

**What Requires Restart**:
❌ Environment variables (.env)
❌ Logging configuration
❌ Flask port/host

---

## Error Handling & Recovery

### Common Errors & Responses

#### File Not Found During Organization

```
Scenario: Job is PENDING_COMPLETION but file doesn't exist
         │
         ▼
System detects file missing
         │
         ├─► Log error message
         ├─► Update job:
         │   - status: FAILED
         │   - error_message: "File not found"
         └─► User sees in dashboard
         
Recovery:
1. Check file actually completed download
2. Verify file in completed folder
3. Re-add file to completed folder
4. Job auto-retries if file reappears
```

#### AI API Error

```
Scenario: Google AI API returns error
         │
         ▼
API call fails (HTTP error, timeout, etc.)
         │
         ├─► Exception caught in process_batch()
         ├─► Log full error details
         ├─► Mark all jobs in batch as FAILED
         │   - error_message: API error details
         └─► Batch processing stops
         
Recovery:
1. Check API key validity
2. Verify API quota not exceeded
3. Check network connectivity
4. Use Re-AI for failed jobs
```

#### Invalid JSON Response from AI

```
Scenario: AI returns malformed JSON
         │
         ▼
JSON parse fails
         │
         ├─► JSONDecodeError caught
         ├─► Log raw response text
         ├─► Mark all jobs as FAILED
         │   - error_message: "Invalid JSON response"
         └─► Processing stops
         
Recovery:
1. Check instructions.md format
2. Verify AI model compatibility
3. Use Re-AI with clearer prompt
4. Check AI response in logs
```

#### Destination Directory Permission Error

```
Scenario: Cannot create directory in library path
         │
         ▼
os.makedirs() fails
         │
         ├─► Exception caught in _organize_file()
         ├─► Log error details
         ├─► Update job:
         │   - status: FAILED
         │   - error_message: "Permission denied"
         └─► File not moved
         
Recovery:
1. Check library path permissions
2. Verify path is writable
3. Check disk space
4. Fix permissions and re-add file
```

#### Configuration File Corruption

```
Scenario: config.json has invalid JSON
         │
         ▼
JSON parse fails
         │
         ├─► JSONDecodeError caught
         ├─► Log error
         ├─► Load default configuration
         └─► Application continues with defaults
         
Recovery:
1. Restore config.json from backup
2. Or edit and fix JSON syntax
3. Or delete and recreate via web UI
```

### Error Logging

All errors are logged with:
- **Timestamp**: When error occurred
- **Logger Name**: Which component failed
- **Level**: ERROR for failures
- **Message**: Human-readable description
- **Exception Info**: Full traceback (if applicable)

**Example Error Log**:
```
2025-11-09 10:45:23 - backend.backend_orchestrator - ERROR - Error organizing file for job abc-123: PermissionError: [Errno 13] Permission denied: '/library/Movies'
Traceback (most recent call last):
  File "backend/backend_orchestrator.py", line 312, in _organize_file
    os.makedirs(destination_dir, exist_ok=True)
PermissionError: [Errno 13] Permission denied: '/library/Movies'
```

---

## State Transitions

### Job Status State Machine

```
         ┌─────────────────┐
         │  QUEUED_FOR_AI  │ ◄──────────────┐
         └────────┬────────┘                 │
                  │                           │
                  │ Batch timer fires         │ Re-AI
                  ▼                           │ requested
         ┌─────────────────┐                 │
         │ PROCESSING_AI   │                 │
         └────────┬────────┘                 │
                  │                           │
                  │ AI success                │
                  ▼                           │
         ┌─────────────────┐                 │
    ┌───►│PENDING_COMPLETION│                │
    │    └────────┬────────┘                 │
    │             │                           │
    │             │ File appears              │
    │             │ in completed              │
    │             ▼                           │
    │    ┌─────────────────┐                 │
    │    │   COMPLETED     │                 │
    │    └─────────────────┘                 │
    │                                         │
    │    ┌─────────────────┐                 │
    └────┤  MANUAL_EDIT    │ ────────────────┘
         └─────────────────┘
         (temporary state)
         
         ┌─────────────────┐
         │     FAILED      │ ────────────────┐
         └─────────────────┘                  │
                  ▲                           │
                  │                           │
                  └───────────────────────────┘
                   AI error / File error
```

### Valid State Transitions

| From | To | Trigger |
|------|---|---------|
| QUEUED_FOR_AI | PROCESSING_AI | Batch timer or priority queue |
| PROCESSING_AI | PENDING_COMPLETION | AI success |
| PROCESSING_AI | FAILED | AI error |
| PENDING_COMPLETION | COMPLETED | File appears + organization success |
| PENDING_COMPLETION | FAILED | Organization error |
| MANUAL_EDIT | PENDING_COMPLETION | Manual edit saved |
| Any | QUEUED_FOR_AI | Re-AI requested |
| FAILED | QUEUED_FOR_AI | Re-AI requested (recovery) |

### Invalid Transitions

These transitions should never occur:
- COMPLETED → Any (final state)
- FAILED → COMPLETED (must reprocess)
- PROCESSING_AI → MANUAL_EDIT (should go through PENDING first)

---

## Timing & Performance

### Typical Timings

**File Detection to AI Processing**:
```
File added to downloading
    → Detection: ~50ms (watchdog latency)
    → Job creation: ~5ms
    → Debounce wait: 5000ms (default)
    → Total: ~5055ms
```

**AI Processing Duration**:
```
Single file: 2-3 seconds
Batch of 10: 5-8 seconds
Batch of 50: 15-30 seconds
With web search: +2-5 seconds
```

**File Organization Duration**:
```
Detection: ~50ms
Job matching: ~5ms
Directory creation: ~10ms
File move: 50-500ms (depends on file size)
Total: ~100-600ms
```

**End-to-End (File Added → File Organized)**:
```
Best case (single file, no queue):
  5s (debounce) + 3s (AI) + 0.5s (move) = ~8.5 seconds

Typical case (batch of 10):
  5s (debounce) + 7s (AI) + 0.5s (move) = ~12.5 seconds

Worst case (large batch, web search, slow AI):
  10s (debounce) + 30s (AI) + 1s (move) = ~41 seconds
```

### Performance Optimization Tips

**For Speed**:
- Reduce `DEBOUNCE_SECONDS` to 2-3
- Reduce `AI_BATCH_SIZE` to 5-10
- Use `gemini-1.5-flash` model
- Disable `ENABLE_WEB_SEARCH`

**For Efficiency**:
- Increase `DEBOUNCE_SECONDS` to 10-15
- Increase `AI_BATCH_SIZE` to 20-50
- Use `gemini-pro` model
- Batch files manually before adding

**For Quality**:
- Moderate `DEBOUNCE_SECONDS` (5-7)
- Moderate `AI_BATCH_SIZE` (10-15)
- Use `gemini-1.5-pro` model
- Enable `ENABLE_WEB_SEARCH` for unknowns

### Bottlenecks

1. **AI API Response Time**: 
   - Main bottleneck
   - 2-30 seconds depending on batch size
   - Solution: Optimize batch size and model selection

2. **File I/O**:
   - Moving large files takes time
   - Network paths slower than local
   - Solution: Use fast local storage for library

3. **Debounce Wait**:
   - Intentional delay for batching
   - Can feel slow for single files
   - Solution: Reduce for interactive use

4. **Priority Queue Polling**:
   - 1-second polling interval
   - Max 1 second latency for re-AI
   - Solution: Acceptable tradeoff for simplicity

---

## Summary

The Intelly Jelly workflow system provides:

1. **Automated Processing**: Detect → Batch → AI → Organize
2. **Manual Control**: Edit and Re-AI capabilities
3. **Priority Handling**: Immediate processing for user requests
4. **Live Configuration**: Changes apply without restart
5. **Error Recovery**: Comprehensive error handling and logging
6. **State Management**: Clear state transitions and tracking
7. **Performance**: Tunable timing and batch sizes

All workflows are logged extensively for debugging and monitoring.
