# Intelly Jelly - Automated Media Organizer

An advanced, automated media-organizing application with a multi-threaded Python backend for file monitoring and processing, and a local Flask web interface for monitoring, manual intervention, and full application configuration.

## Features

- **Automated File Monitoring**: Watches downloading and completed folders for new files
- **AI-Powered File Naming**: Uses OpenAI, Google, or Ollama to intelligently rename files
- **Batch Processing**: Processes files in configurable batches with debounce timer
- **Priority Queue**: Manual re-AI requests are processed immediately
- **Web Interface**: Beautiful Flask-based UI for monitoring and configuration
- **Dynamic Configuration**: Live reload of configuration without restarting
- **Multi-threaded Architecture**: Efficient processing with separate threads for different tasks

## Architecture

### Backend Components

1. **Job Store**: Thread-safe data structure tracking all file processing jobs
2. **Configuration Manager**: Manages config.json with live reload capability
3. **AI Processor**: Supports multiple AI providers (OpenAI, Google, Ollama)
4. **File Watchers**: Monitor downloading and completed folders
5. **Batch Processor**: Debounced batch processing with configurable timing
6. **Priority Queue**: Dedicated thread for high-priority re-AI requests

### Frontend

- **Dashboard** (`/`): Real-time view of all jobs with auto-refresh
- **Settings** (`/settings`): Full configuration management with dynamic AI model loading

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JL-Bones/Intelly_Jelly.git
cd Intelly_Jelly
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. Configure the application by editing `config.json` or use the web interface

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:7000
```

3. Configure your settings in the Settings page

4. Add files to the downloading folder to start processing

## Configuration

### config.json (Managed via Web UI)

- `DOWNLOADING_PATH`: Path to monitor for new files
- `COMPLETED_PATH`: Path where completed downloads appear
- `LIBRARY_PATH`: Path where organized files will be stored
- `INSTRUCTIONS_FILE_PATH`: Path to AI prompt instructions
- `DEBOUNCE_SECONDS`: Wait time before processing batch
- `AI_BATCH_SIZE`: Number of files to process at once
- `AI_PROVIDER`: AI provider (openai, google, ollama)
- `AI_MODEL`: AI model to use
- `OLLAMA_API_URL`: Ollama API URL (default: http://localhost:11434)
- `DRY_RUN_MODE`: Test mode without actually moving files
- `ENABLE_WEB_SEARCH`: Allow AI to search the web

### .env (Manual Configuration)

- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_API_KEY`: Your Google API key

## Workflow

### Stage 1: Monitor & Batch Process

1. Files detected in downloading folder are added to the job queue
2. Debounce timer starts/resets with each new file
3. When timer completes, files are batched and sent to AI
4. AI returns suggested names and confidence scores
5. Jobs are marked as "Pending Completion"

### Stage 2: Execute & Organize

1. Files appearing in completed folder are matched to pending jobs
2. Files are renamed and moved to library folder
3. Jobs are marked as "Completed"

### Manual Intervention

- **Edit Job**: Manually set the new name and path
- **Re-AI**: Reprocess with optional custom prompt (priority queue)

## API Endpoints

- `GET /api/jobs` - Get all jobs
- `GET /api/jobs/<job_id>` - Get specific job
- `POST /api/jobs/<job_id>/edit` - Manually edit job
- `POST /api/jobs/<job_id>/re-ai` - Queue job for re-processing
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `POST /api/models` - Get available AI models for provider
- `GET /api/stats` - Get job statistics

## Development

The application uses a multi-threaded architecture:

- Main thread: Flask web server
- Background thread: Backend orchestrator
- File watcher threads: Monitor downloading and completed folders
- Debounce thread: Batch processing timer
- Priority queue thread: Process re-AI requests

## License

MIT License

## Author

Created by @JL-Bones
