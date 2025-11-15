# 🍇 Intelly Jelly

**An intelligent, automated media organizer powered by AI**

Intelly Jelly is a multi-threaded Python application that watches your download folders and uses Google's Gemini AI to intelligently organize, rename, and categorize your media files. With a beautiful web interface, powerful automation, and secure authentication, it takes the hassle out of managing your media library.

---

## ✨ Features

### Core Features
- **🤖 AI-Powered Organization**: Uses Google Gemini AI to intelligently determine proper file names and folder structures
- **👀 Real-Time Monitoring**: Automatically watches folders for new files and processes them in batches
- **🌐 Web Search Integration**: Optional Google Search grounding for accurate information about movies, TV shows, music, and more
- **🎨 Beautiful Web UI**: Clean, responsive interface with dark/light theme support
- **⚡ Priority Queue System**: Manually re-process files with custom prompts and immediate priority
- **🔧 Dynamic Configuration**: Update all settings through the web interface - no file editing required
- **🧵 Multi-Threaded**: Efficient concurrent processing with thread-safe operations
- **📊 Real-Time Stats**: Live job status updates and processing statistics
- **🎯 Flexible Rules**: Customizable organization rules for Movies, TV Shows, Music, Books, and more

### Security & Authentication
- **🔐 Password Protection**: Optional app-wide and admin password protection
- **� Remember Me**: Secure token-based authentication with 30-day sessions
- **🍪 Browser Cookies**: Theme and authentication preferences persist across sessions

### Additional Features
- **�📝 Comprehensive Logging**: Detailed logging of all operations and file movements
- **🍇 Jellyfin Integration**: Optional automatic library refresh when files are organized
- **🔑 Web-Based API Management**: Configure Google and Jellyfin API keys directly in settings
- **🌙 Theme Persistence**: Dark/light mode preference saved in browser cookies

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))
- (Optional) Jellyfin server for library refresh integration

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/JL-Bones/Intelly_Jelly.git
   cd Intelly_Jelly
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Configure through web interface**
   
   Open your browser to `http://localhost:5000` and:
   - Navigate to **Settings** to configure:
     - **API Keys**: Add your Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
     - **Folder Paths**: Set your downloading, completed, and library paths
     - **AI Settings**: Choose your preferred AI model and settings
     - **Security**: Optionally set application and admin passwords
     - **Jellyfin**: Configure Jellyfin integration if desired

That's it! All configuration is done through the user-friendly web interface.

6. **Open your browser**
   
   Navigate to: `http://localhost:7000`

---

## 📖 How It Works

### The Workflow

1. **Detection**: Files are detected in the `DOWNLOADING_PATH` folder
2. **Queuing**: Jobs are created and queued for AI processing
3. **AI Processing**: Gemini AI analyzes filenames and determines proper organization
4. **Pending**: Jobs wait for files to appear in `COMPLETED_PATH` folder
5. **Organization**: Files are automatically moved and renamed in `LIBRARY_PATH`

### Example

**Before:**
```
downloading/
  ├── The.Best.Movie.2024.1080p.WEB-DL.mkv
  └── awesome.show.s01e01.720p.mp4
```

**After Processing:**
```
library/
  ├── Movies/
  │   └── The Best Movie (2024)/
  │       └── The Best Movie (2024).mkv
  └── TV Shows/
      └── Awesome Show/
          └── Season 01/
              └── Awesome Show - S01E01 - Episode Title.mp4
```

---

## 🎮 Using the Web Interface

Access the application at `http://localhost:5000`

### 🏠 Downloads (`/`)

- **Job Queue**: View all active jobs and their status
- **Statistics**: Real-time counts of queued, processing, pending, completed, and failed jobs
- **Job Actions**:
  - ✏️ **Edit**: Manually edit the AI-determined name and path
  - 🔄 **Re-AI**: Re-process with custom prompts and options
  - 🗑️ **Delete**: Remove completed jobs from the list
- **Auto-Refresh**: Live updates every 2 seconds

### 📚 Library (`/library`)

- Browse organized files in your library
- Search and filter functionality
- Sort by name, date, or size
- Delete files directly from the interface
- Pagination for large libraries

### 📋 Logs (`/logs`)

- View file movement history
- See source and destination paths
- Track success/failure status
- Filter and search logs
- Clear log history

### ⚙️ Settings (`/settings`)

Configure everything through the web interface:

- **API Keys**: Securely add Google and Jellyfin API keys (masked display)
- **Folder Paths**: Set downloading, completed, and library directories
- **AI Configuration**: Select model, adjust processing delay
- **Advanced Options**: Toggle web search
- **Jellyfin Integration**: Enable automatic library refresh
- **Security**: Set optional app and admin passwords

---

## ⚙️ Configuration

All configuration is managed through the **Settings** page in the web interface at `http://localhost:5000/settings`.

### Configuration Options

| Category | Setting | Description | Default |
|----------|---------|-------------|---------|
| **API Keys** | Google API Key | Your Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey)) | None |
| | Jellyfin API Key | Your Jellyfin API key (optional) | None |
| **Folder Paths** | Downloading Path | Folder to monitor for new files | `./test_folders/downloading` |
| | Completed Path | Folder where completed downloads appear | `./test_folders/completed` |
| | Library Path | Destination for organized files | `./test_folders/library` |
| **AI Settings** | AI Model | Google Gemini model to use | `gemini-2.0-flash-exp` |
| | API Call Delay | Delay between AI API calls (seconds) | `2` |
| **Advanced** | Web Search | Enable Google Search grounding | Enabled |
| **Jellyfin** | Refresh Enabled | Auto-refresh Jellyfin library | Disabled |
| **Security** | App Password | Password for entire application (optional) | None |
| | Admin Password | Password for settings access (optional) | None |

### Security Features

- **API Key Masking**: Saved API keys display only the last 4 digits for security
- **Password Protection**: 
  - App Password: Protects access to the entire application
  - Admin Password: Protects access to settings page
  - Both optional - leave blank to disable
- **Remember Me**: Secure 30-day authentication tokens stored in browser cookies

**Notes**: 
- All settings are stored in `config.json` and update in real-time
- AI instructions are stored in `instruction_prompt.md` (not configurable through UI)
- Jellyfin server address is `http://localhost:8096`
- Configuration changes apply immediately without restart

---

## 📚 Media Organization Rules

Intelly Jelly follows strict naming conventions for different media types:

### 🎬 Movies
```
Movies/Movie Title (Year)/Movie Title (Year).ext
```

### 📺 TV Shows
```
TV Shows/Show Name/Season ##/Show Name - S##E## - Episode Title.ext
```

### 🎵 Music
```
Music/Artist Name/Album Name (Year)/## - Track Name.ext
```

### 📖 Books
```
Books/Author Name/Book Title (Year)/Book Title.ext
```

### 🎮 Games
```
Games/Platform/Game Title (Year)/Game Title.ext
```

For complete details, see [`instruction_prompt.md`](instruction_prompt.md) or the [File Organization Rules](Project_Wiki/06_File_Organization_Rules.md) documentation.

---

## 🔍 Web Search Feature

When enabled, Intelly Jelly uses Google's Search grounding feature to find accurate information about your media:

- **Movie Details**: Correct titles, release years, proper formatting
- **TV Show Info**: Episode names, air dates, season numbers
- **Music Metadata**: Artist names, album titles, track listings
- **Book Information**: Author names, publication years, editions

Enable web search in:
1. Global settings (`config.json` → `ENABLE_WEB_SEARCH: true`)
2. Per-job basis (Re-AI dialog → "Enable web search" checkbox)

---

## 🛠️ Advanced Usage

### Custom Prompts

Use the Re-AI feature to process files with custom instructions:

```
This is a Japanese anime movie from Studio Ghibli.
Use the original Japanese title with English subtitle in parentheses.
```

### Manual Editing

Override AI suggestions by clicking "Edit" on any job:
- Change the destination filename
- Specify a custom folder path
- Correct any mistakes

### Priority Processing

Re-AI requests are processed immediately, bypassing the batch queue for instant results.

---

## 📊 API Endpoints

Intelly Jelly provides a RESTful API for integration:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/jobs` | Get all jobs |
| `GET` | `/api/jobs/<id>` | Get specific job |
| `POST` | `/api/jobs/<id>/edit` | Edit job name/path |
| `POST` | `/api/jobs/<id>/re-ai` | Re-process with AI |
| `DELETE` | `/api/jobs/<id>` | Delete completed job |
| `GET` | `/api/config` | Get configuration |
| `POST` | `/api/config` | Update configuration |
| `POST` | `/api/models` | Get available AI models |
| `GET` | `/api/stats` | Get processing statistics |

---

## 📖 Documentation

For in-depth technical documentation, see the [Project Wiki](Project_Wiki/):

- [Architecture Overview](Project_Wiki/01_Architecture_Overview.md)
- [Backend Components](Project_Wiki/02_Backend_Components.md)
- [Frontend Interface](Project_Wiki/03_Frontend_Interface.md)
- [Configuration Guide](Project_Wiki/04_Configuration_Guide.md)
- [Processing Workflows](Project_Wiki/05_Processing_Workflows.md)
- [File Organization Rules](Project_Wiki/06_File_Organization_Rules.md)
- [Development Guide](Project_Wiki/07_Development_Guide.md)

---

## 🐛 Troubleshooting

### Jobs Stuck in "Processing"

- Check `intelly_jelly.log` for error messages
- Verify your Google API key is configured correctly in Settings
- Ensure the AI model supports your request
- Check API key has not expired

### Files Not Moving

- Confirm files are in the `COMPLETED_PATH` folder
- Check file permissions
- Verify `LIBRARY_PATH` is accessible and writable

### API Key Issues

- Ensure Google API key is entered in Settings → API Keys
- Keys are masked after saving - only last 4 digits shown
- Delete and re-add key if having issues
- Verify key has Gemini API access enabled

### Authentication Problems

- Clear browser cookies if having login issues
- Check password is set correctly in Settings
- Remember Me tokens expire after 30 days
- Tokens invalidate when password changes

### Web Search Not Working

- Ensure `ENABLE_WEB_SEARCH` is enabled in Settings → Advanced Options
- Verify you're using a compatible Gemini model (2.0+ recommended)
- Check API logs for any grounding errors

### API Rate Limits

- Reduce `AI_BATCH_SIZE` in settings
- Increase `DEBOUNCE_SECONDS` to process less frequently
- Monitor the logs for 429 errors

---

## 🧪 Development

### Running Tests

```bash
python test_functionality.py
```

### Logging

Logs are written to:
- Console (stdout)
- `intelly_jelly.log` file

Detailed API request/response logging is included for debugging.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

This project is provided as-is for personal use. See repository for license details.

---

## 🙏 Acknowledgments

- **Google Gemini AI**: For powerful language understanding and generation
- **Flask**: For the lightweight web framework
- **Watchdog**: For reliable file system monitoring
- **Contributors**: Thanks to everyone who has contributed to this project

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/JL-Bones/Intelly_Jelly/issues)
- **Documentation**: [Project Wiki](Project_Wiki/)
- **Logs**: Check `intelly_jelly.log` for detailed information

---

## 🗺️ Roadmap

- [x] Integration with Jellyfin media server
- [ ] Support for additional AI providers (OpenAI, Anthropic Claude)
- [ ] Integration with Plex media server
- [ ] Automatic metadata fetching and tagging
- [ ] Mobile app for remote monitoring
- [ ] Advanced filtering and search
- [ ] Scheduled processing windows
- [ ] Webhook notifications

---

**Made with ❤️ and AI**
