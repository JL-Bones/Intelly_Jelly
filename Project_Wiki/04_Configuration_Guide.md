# Configuration Guide

## Table of Contents
1. [Configuration Files](#configuration-files)
2. [Public Configuration (config.json)](#public-configuration-configjson)
3. [Secret Configuration (.env)](#secret-configuration-env)
4. [Instructions File](#instructions-file)
5. [Configuration Management](#configuration-management)
6. [Default Values](#default-values)
7. [Configuration Best Practices](#configuration-best-practices)

---

## Configuration Files

Intelly Jelly uses a two-file configuration system to separate public settings from secret credentials:

| File | Purpose | Managed By | Contains |
|------|---------|------------|----------|
| `config.json` | Public settings | Web UI + Manual | Paths, timings, AI settings |
| `.env` | Secret credentials | Manual only | API keys |
| `instructions.md` | AI prompt | Manual only | Instructions for AI |

---

## Public Configuration (config.json)

### Overview

The `config.json` file contains all non-secret application settings. It can be edited through the web UI or manually.

**Location**: Project root directory

**Format**: JSON

**Reload**: Automatic (file watcher detects changes)

### Configuration Schema

```json
{
  "DOWNLOADING_PATH": "./test_folders/downloading",
  "COMPLETED_PATH": "./test_folders/completed",
  "LIBRARY_PATH": "./test_folders/library",
  "INSTRUCTIONS_FILE_PATH": "./instructions.md",
  "DEBOUNCE_SECONDS": 5,
  "AI_BATCH_SIZE": 10,
  "AI_PROVIDER": "google",
  "AI_MODEL": "gemini-2.0-flash-exp",
  "DRY_RUN_MODE": false,
  "ENABLE_WEB_SEARCH": true
}
```

### Configuration Fields

#### Folder Paths

**`DOWNLOADING_PATH`**
- **Type**: String (path)
- **Description**: Path to monitor for new files
- **Default**: `./test_folders/downloading`
- **Example**: `C:/Downloads/Processing` or `/home/user/downloads`
- **Notes**: 
  - Can be relative or absolute
  - Directory created automatically if missing
  - Watched recursively
  - Changes take effect immediately (watcher restarts)

**`COMPLETED_PATH`**
- **Type**: String (path)
- **Description**: Path where completed downloads appear
- **Default**: `./test_folders/completed`
- **Example**: `C:/Downloads/Completed` or `/home/user/completed`
- **Notes**:
  - Can be relative or absolute
  - Directory created automatically if missing
  - Watched recursively
  - Changes take effect immediately (watcher restarts)

**`LIBRARY_PATH`**
- **Type**: String (path)
- **Description**: Path where organized files will be stored
- **Default**: `./test_folders/library`
- **Example**: `D:/Media/Library` or `/mnt/nas/media`
- **Notes**:
  - Can be relative or absolute
  - Directory created automatically if missing
  - Final destination for all organized files
  - Should have sufficient storage space

**`INSTRUCTIONS_FILE_PATH`**
- **Type**: String (path)
- **Description**: Path to AI prompt instructions file
- **Default**: `./instructions.md`
- **Example**: `./custom_instructions.txt` or `/config/ai_prompt.md`
- **Notes**:
  - Can be relative or absolute
  - Read when AI processing starts
  - Falls back to default instructions if file not found
  - Changes take effect on next AI batch

#### Processing Settings

**`DEBOUNCE_SECONDS`**
- **Type**: Integer
- **Description**: Wait time before processing batch (in seconds)
- **Default**: 5
- **Range**: 1-60 (recommended)
- **Example**: `10` for 10-second wait
- **Notes**:
  - Timer resets with each new file
  - Allows multiple files to accumulate before processing
  - Lower values = faster processing, more API calls
  - Higher values = fewer API calls, longer wait times
  - Changes take effect on next trigger

**`AI_BATCH_SIZE`**
- **Type**: Integer
- **Description**: Number of files to process in single AI request
- **Default**: 10
- **Range**: 1-100 (recommended)
- **Example**: `20` for 20 files per batch
- **Notes**:
  - Larger batches = fewer API calls, longer processing time
  - Smaller batches = more API calls, faster per-batch results
  - Consider API rate limits and token limits
  - Changes take effect on next batch

#### AI Configuration

**`AI_PROVIDER`**
- **Type**: String
- **Description**: AI provider to use
- **Default**: `google`
- **Options**: Currently only `google` is supported
- **Future**: May support `openai`, `ollama`
- **Notes**:
  - Must have corresponding API key in .env
  - Changes take effect on next AI call

**`AI_MODEL`**
- **Type**: String
- **Description**: Specific AI model to use
- **Default**: `gemini-2.0-flash-exp` (or `gemini-pro` for older versions)
- **Options** (Google):
  - `gemini-2.0-flash-exp`: Latest experimental model, fast with web search support
  - `gemini-1.5-pro`: Highly capable, good for complex tasks
  - `gemini-1.5-flash`: Very fast, lighter weight
  - `gemini-pro`: General-purpose legacy model
  - Others available via API
- **Example**: `gemini-2.0-flash-exp`
- **Notes**:
  - Must be available for selected provider
  - Use `/api/models` endpoint to get valid options
  - Changes take effect on next AI call
  - Different models have different:
    - Speed
    - Accuracy
    - Cost
    - Context limits

#### Advanced Options

**`DRY_RUN_MODE`**
- **Type**: Boolean
- **Description**: Test mode without actually moving files
- **Default**: `false`
- **Options**: `true` or `false`
- **Example**: `true` for testing
- **Notes**:
  - When enabled:
    - AI processing still occurs
    - Jobs are created and tracked
    - Files are NOT moved
    - Logs show what WOULD happen
  - Useful for:
    - Testing AI results
    - Verifying file organization logic
    - Previewing changes
  - Changes take effect immediately

**`ENABLE_WEB_SEARCH`**
- **Type**: Boolean
- **Description**: Allow AI to search the web for additional context
- **Default**: `true`
- **Options**: `true` or `false`
- **Example**: `true` to enable
- **Notes**:
  - Uses Google Search tool (`google_search`)
  - Automatically activates when AI determines web search is needed
  - Provides AI with real-time web data
  - Useful for:
    - Obscure media
    - Recent releases
    - Missing metadata
    - Verifying movie/TV show titles and years
    - Finding episode names and season information
  - Applied globally to all batch processing
  - Can be overridden per-job via Re-AI dialog
  - May increase processing time slightly
  - May increase API costs
  - Changes take effect on next AI call
  - Requires compatible Gemini model (2.0+ recommended)

### Editing config.json

#### Via Web UI (Recommended)

1. Navigate to http://localhost:7000/settings
2. Modify desired fields
3. Click "Save Settings"
4. Changes applied automatically

**Advantages**:
- Validation
- Type checking
- Immediate feedback
- No syntax errors
- Dynamic model selection

#### Manual Editing

1. Open `config.json` in text editor
2. Modify values
3. Save file
4. Application detects change automatically

**Advantages**:
- Faster for experienced users
- Can edit offline
- Version control friendly

**Cautions**:
- Must maintain valid JSON syntax
- No validation until loaded
- Typos can cause errors
- Backup before editing

### Configuration Validation

The application validates configuration on load:

**Type Checking**:
- Paths must be strings
- Numbers must be integers
- Booleans must be true/false

**Fallback Behavior**:
- Missing fields use defaults
- Invalid JSON loads defaults
- File not found creates defaults

**Logging**:
- Config changes logged at INFO level
- Parse errors logged at ERROR level
- Validation failures logged at WARNING level

---

## Secret Configuration (.env)

### Overview

The `.env` file contains API keys and other sensitive credentials. This file should **NEVER** be committed to version control.

**Location**: Project root directory

**Format**: Key-value pairs

**Reload**: Only on application restart

**Security**: Listed in `.gitignore`

### Environment Variables

**`GOOGLE_API_KEY`**
- **Description**: Google AI (Gemini) API key
- **Required**: Yes (if using Google AI)
- **Format**: String
- **Example**: `GOOGLE_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuv`
- **Obtain From**: https://makersuite.google.com/app/apikey
- **Notes**:
  - Keep secret
  - Rotate periodically
  - Monitor usage in Google Cloud Console
  - Rate limits apply

**`OPENAI_API_KEY`**
- **Description**: OpenAI API key
- **Required**: No (reserved for future use)
- **Format**: String
- **Example**: `OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz`
- **Obtain From**: https://platform.openai.com/api-keys
- **Notes**:
  - Not currently used
  - Future provider support
  - Keep secret if added

### Setting Up .env

#### Initial Setup

1. Copy example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env`:
   ```bash
   # Windows
   notepad .env
   
   # Linux/Mac
   nano .env
   ```

3. Add your API keys:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   OPENAI_API_KEY=your_openai_key_if_needed
   ```

4. Save and close

5. Restart application to load new keys

#### Security Best Practices

**DO**:
- Keep .env out of version control
- Use different keys for dev/prod
- Rotate keys periodically
- Monitor API usage
- Use environment-specific keys
- Restrict key permissions in cloud console

**DON'T**:
- Commit .env to Git
- Share keys publicly
- Hard-code keys in source
- Use production keys in development
- Share .env file with others
- Post keys in issues/forums

### Verifying API Keys

**Google AI Key**:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
```

Expected response: List of available models

**From Web UI**:
1. Go to Settings page
2. AI Model dropdown should populate
3. If empty, check:
   - .env file exists
   - GOOGLE_API_KEY is set
   - Key is valid
   - No spaces around key
   - Application restarted after changes

---

## Instructions File

### Overview

The instructions file contains the AI prompt that guides file naming and organization. It defines the rules and formats the AI should follow.

**Location**: Configurable via `INSTRUCTIONS_FILE_PATH`

**Default**: `./instructions.md`

**Format**: Markdown (or plain text)

**Reload**: Read on each AI batch

### File Structure

The instructions file should contain:

1. **Core Task**: What the AI should do
2. **Output Format**: Expected JSON structure
3. **General Rules**: Processing guidelines
4. **Media Organization Rules**: Specific rules per media type
5. **Examples**: Sample inputs and outputs

### Current Instructions Overview

The default `instructions.md` contains comprehensive rules for:

**Movies**:
- Folder: `Movies/Movie Title (Year)/`
- File: `Movie Title (Year).ext`
- Versions: `Movie Title (Year) - 1080p.ext`
- Extras: Subfolders (trailers, behind the scenes, etc.)

**TV Shows**:
- Folder: `TV Shows/Series Name (Year)/Season XX/`
- File: `Series Name (Year) - SXXEYY.ext`
- Multi-part: `- SXXEYY - EZZ.ext`
- Optional: Episode name suffix

**Music**:
- Folder: `Music/Artist/Album/` or `Music/Album/`
- File: Tagged track title (e.g., `01 - Song Title.mp3`)
- Lyrics: Matching filename with `.lrc`/`.txt` extension

**Books**:
- Audiobooks: `Books/Audiobooks/[Author]/[Book Title]/`
- eBooks: `Books/Books/[Author]/[Book Title]/`
- Comics: `Books/Comics/[Series Name (Year)]/`

**Software**:
- Folder: `Software/[Software Name]/`
- File: Keep original structure

**Other**:
- Folder: `Other/`
- File: Keep original name

### Customizing Instructions

#### Adding Custom Rules

1. Open `instructions.md` (or your custom file)
2. Add your rules in the appropriate section
3. Provide examples
4. Save file
5. Changes apply to next AI batch

**Example Addition**:
```markdown
#### 📸 Photos

* **Folder Structure:** `Photos/[Year]/[Month]/`
* **File Naming:** `YYYY-MM-DD_HH-MM-SS_Description.ext`
* **Albums:** `Photos/Albums/[Album Name]/`
```

#### Testing Custom Instructions

1. Enable DRY_RUN_MODE in config
2. Add test file to downloading folder
3. Check AI result in dashboard
4. Verify naming matches expectations
5. Adjust instructions if needed
6. Disable DRY_RUN_MODE when satisfied

#### Using Multiple Instruction Files

You can maintain different instruction files for different scenarios:

**General media**:
```json
"INSTRUCTIONS_FILE_PATH": "./instructions_media.md"
```

**Documents only**:
```json
"INSTRUCTIONS_FILE_PATH": "./instructions_docs.md"
```

**Custom project**:
```json
"INSTRUCTIONS_FILE_PATH": "./instructions_custom.md"
```

Switch between them in the Settings page.

---

## Configuration Management

### Configuration Lifecycle

```
Application Start:
├─ Load .env (python-dotenv)
├─ Load config.json
├─ Apply defaults for missing values
├─ Start config file watcher
└─ Register change callbacks

Configuration Change:
├─ User edits via web UI
├─ POST to /api/config
├─ ConfigManager.update_config()
├─ Write to config.json
├─ File watcher detects change
├─ ConfigManager.reload_config()
├─ Compare old vs new
├─ Notify callbacks
└─ Components update

Backend Components Update:
├─ Orchestrator receives callback
├─ Check DOWNLOADING_PATH change
│  └─ Restart downloading watcher
├─ Check COMPLETED_PATH change
│  └─ Restart completed watcher
├─ Check DEBOUNCE_SECONDS change
│  └─ Update debounce processor
└─ Log changes
```

### Live Reload

The application supports **live configuration reload** without restart:

**What Updates Live**:
- Folder paths (watchers restart)
- Debounce timing (timer updates)
- AI model (next batch uses new model)
- AI batch size (next batch uses new size)
- Dry run mode (immediate effect)
- Web search flag (next batch uses new flag)

**What Requires Restart**:
- Environment variables (.env)
- Application port
- Logging configuration

### Configuration Backups

**Automatic**:
- Git tracks config.json changes
- Create backup before major changes

**Manual**:
```bash
# Backup current config
cp config.json config.json.backup

# Restore from backup
cp config.json.backup config.json
```

**Version Control**:
```bash
# Commit working configuration
git add config.json
git commit -m "Update configuration: increase batch size"
```

---

## Default Values

### Built-in Defaults

When config.json is missing or invalid, these defaults are used:

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
    "ENABLE_WEB_SEARCH": True  # Changed to True by default for better results
}
```

**Current Production Defaults** (as of latest version):
```json
{
    "DOWNLOADING_PATH": "./test_folders/downloading",
    "COMPLETED_PATH": "./test_folders/completed",
    "LIBRARY_PATH": "./test_folders/library",
    "INSTRUCTIONS_FILE_PATH": "./instructions.md",
    "DEBOUNCE_SECONDS": 5,
    "AI_BATCH_SIZE": 10,
    "AI_PROVIDER": "google",
    "AI_MODEL": "gemini-2.0-flash-exp",
    "DRY_RUN_MODE": false,
    "ENABLE_WEB_SEARCH": true
}
```

### Recommended Values

**For Fast Processing**:
```json
{
    "DEBOUNCE_SECONDS": 2,
    "AI_BATCH_SIZE": 5,
    "AI_MODEL": "gemini-1.5-flash"
}
```

**For Cost Optimization**:
```json
{
    "DEBOUNCE_SECONDS": 10,
    "AI_BATCH_SIZE": 20,
    "AI_MODEL": "gemini-pro"
}
```

**For Best Quality**:
```json
{
    "DEBOUNCE_SECONDS": 5,
    "AI_BATCH_SIZE": 10,
    "AI_MODEL": "gemini-2.0-flash-exp",
    "ENABLE_WEB_SEARCH": true
}
```

**For Latest Features** (Recommended):
```json
{
    "DEBOUNCE_SECONDS": 5,
    "AI_BATCH_SIZE": 10,
    "AI_MODEL": "gemini-2.0-flash-exp",
    "ENABLE_WEB_SEARCH": true,
    "DRY_RUN_MODE": false
}
```

**For Testing**:
```json
{
    "DEBOUNCE_SECONDS": 2,
    "AI_BATCH_SIZE": 3,
    "DRY_RUN_MODE": true
}
```

---

## Configuration Best Practices

### Path Configuration

**Use Absolute Paths for Production**:
```json
{
    "DOWNLOADING_PATH": "C:/Media/Downloads",
    "COMPLETED_PATH": "C:/Media/Completed",
    "LIBRARY_PATH": "D:/Library"
}
```

**Use Relative Paths for Development**:
```json
{
    "DOWNLOADING_PATH": "./test_folders/downloading",
    "COMPLETED_PATH": "./test_folders/completed",
    "LIBRARY_PATH": "./test_folders/library"
}
```

**Network Paths**:
```json
{
    "LIBRARY_PATH": "//NAS/Media/Library"
}
```
or
```json
{
    "LIBRARY_PATH": "/mnt/nas/media"
}
```

### Performance Tuning

**High-Volume Processing**:
- Increase `AI_BATCH_SIZE` (20-50)
- Increase `DEBOUNCE_SECONDS` (10-30)
- Use faster model (`gemini-1.5-flash`)

**Low-Volume Processing**:
- Decrease `DEBOUNCE_SECONDS` (2-3)
- Moderate `AI_BATCH_SIZE` (5-10)
- Use quality model (`gemini-1.5-pro`)

**API Rate Limits**:
- Monitor API usage in cloud console
- Adjust batch size to stay within limits
- Increase debounce to reduce request frequency

### Security

**API Keys**:
- Never commit .env file
- Use read-only keys if available
- Rotate keys quarterly
- Monitor for unauthorized usage

**File Permissions**:
```bash
# Linux/Mac
chmod 600 .env
chmod 644 config.json
```

**Access Control**:
- Restrict web UI access (firewall rules)
- Use reverse proxy with authentication
- Enable HTTPS in production

### Monitoring

**Log Levels**:
```python
# In code
logging.basicConfig(level=logging.DEBUG)  # Verbose
logging.basicConfig(level=logging.INFO)   # Normal
logging.basicConfig(level=logging.WARNING) # Quiet
```

**Configuration Checks**:
- Verify paths exist and are writable
- Test API keys before production
- Validate instructions file format
- Check disk space in library path

### Maintenance

**Regular Tasks**:
- Review and update instructions.md
- Rotate API keys
- Clean up completed jobs (future feature)
- Archive old log files
- Backup configuration

**Configuration Review**:
- Monthly: Review settings for optimization
- Quarterly: Update AI models if new ones available
- Yearly: Full configuration audit

---

## Summary

Intelly Jelly's configuration system provides:

1. **Flexibility**: Separate public and secret configuration
2. **Live Reload**: Changes take effect without restart
3. **Validation**: Type checking and defaults
4. **Security**: Secret credentials isolated
5. **Customization**: Comprehensive instruction system
6. **Management**: Web UI and manual editing options

Proper configuration ensures optimal performance, security, and organization quality.
