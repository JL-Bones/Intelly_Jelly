# Intelly Jelly DeepWiki

> Comprehensive technical documentation for the Intelly Jelly automated media organizer

## 🆕 Recent Improvements

**Latest Updates**:
- ✅ **Comprehensive API Logging**: Full request/response logging for Google AI API calls
- ✅ **Web Search Enhancement**: Fixed and improved Google Search grounding functionality
- ✅ **Dynamic Retrieval**: Configured dynamic threshold-based web search activation
- ✅ **Updated Documentation**: All wiki docs updated to reflect current implementation
- ✅ **Main README**: Added comprehensive project README with installation and usage guide

These improvements enhance debugging capabilities and ensure web search works correctly for accurate media information retrieval.

---

## 📚 Documentation Index

This DeepWiki provides complete, in-depth documentation of every aspect of the Intelly Jelly application. Whether you're a developer, system administrator, or power user, you'll find detailed information about how the system works.

### Quick Navigation

| Document | Description | Best For |
|----------|-------------|----------|
| [01. Architecture Overview](01_Architecture_Overview.md) | System design, components, and threading model | Understanding the big picture |
| [02. Backend Components](02_Backend_Components.md) | Detailed documentation of all backend modules | Developers and contributors |
| [03. Frontend Interface](03_Frontend_Interface.md) | Web UI, API endpoints, and JavaScript | Frontend development |
| [04. Configuration Guide](04_Configuration_Guide.md) | All configuration options and best practices | System administrators |
| [05. Processing Workflows](05_Processing_Workflows.md) | Complete data flow and state transitions | Understanding operations |
| [06. File Organization Rules](06_File_Organization_Rules.md) | AI instructions and naming conventions | Customizing organization |
| [07. Development Guide](07_Development_Guide.md) | Setup, coding standards, and deployment | New developers |

---

## 📖 Document Summaries

### 01. Architecture Overview

**What's Inside**:
- System overview and key features
- Core design principles
- Architecture diagrams
- Component relationships
- Technology stack
- Threading model details
- Complete data flow
- Google Search grounding integration

**Read This If**:
- You want to understand how everything fits together
- You're new to the project
- You need to explain the system to others
- You're planning architectural changes

**Key Sections**:
- Component overview with ASCII diagrams
- Threading model with 6 concurrent threads
- Data flow through 4 processing stages
- Integration points between components
- Web search and AI grounding capabilities

---

### 02. Backend Components

**What's Inside**:
- Job Store: Thread-safe state management with web search support
- Configuration Manager: Live config reload
- AI Processor: Google AI integration with comprehensive logging
- Backend Orchestrator: Central coordination with web search
- File Watchers: File system monitoring

**Read This If**:
- You're developing backend features
- You need to understand thread safety
- You're debugging backend issues
- You want to add new capabilities
- You're troubleshooting API interactions

**Key Sections**:
- Complete API documentation for each class
- Thread safety mechanisms explained
- Usage examples for every component
- Integration patterns
- Comprehensive API request/response logging
- Web search grounding configuration

**Code Coverage**:
- 5 backend modules fully documented
- Every class, method, and attribute
- Thread safety patterns
- Error handling approaches
- API logging and debugging features

---

### 03. Frontend Interface & API Reference

**What's Inside**:
- Flask application structure
- Dashboard (index.html) breakdown
- Settings page (settings.html) details
- Complete API endpoint reference
- JavaScript function documentation
- Responsive design guide

**Read This If**:
- You're working on the web interface
- You need to call API endpoints
- You're adding new UI features
- You want to understand the frontend

**Key Sections**:
- All 10 API endpoints documented
- Request/response formats
- JavaScript function explanations
- CSS responsive breakpoints

**API Coverage**:
- Job management (GET, POST)
- Configuration (GET, POST)
- Model discovery
- Statistics

---

### 04. Configuration Guide

**What's Inside**:
- Configuration file formats
- All configuration fields explained
- Secret management (.env)
- Instructions file guide
- Live reload mechanism
- Best practices

**Read This If**:
- You're setting up the application
- You need to customize behavior
- You're troubleshooting configuration
- You want to understand settings

**Key Sections**:
- Complete field reference
- Default values
- Validation rules
- Security best practices
- Performance tuning

**Configuration Types**:
- Public (config.json): 10 fields
- Secret (.env): API keys
- Instructions: AI prompt template

---

### 05. Processing Workflows & Data Flow

**What's Inside**:
- Complete workflow overview
- Automated processing flow (3 stages)
- Manual intervention workflows
- Priority queue processing
- Configuration change flow
- Error handling & recovery
- State transitions
- Timing & performance

**Read This If**:
- You want to understand how files are processed
- You're debugging workflow issues
- You need to optimize performance
- You're tracing execution flow

**Key Sections**:
- Stage 1: File Detection → AI Processing
- Stage 2: File Completion → Organization  
- Stage 3: Manual Re-AI Request
- Stage 4: Manual Edit
- Job status state machine

**Workflow Diagrams**:
- ASCII flow charts for each workflow
- Timing information
- Error paths
- Recovery procedures

---

### 06. File Organization Rules & AI Instructions

**What's Inside**:
- Instructions file format
- Media organization rules
- JSON response format
- Examples by media type
- Custom rule creation

**Read This If**:
- You want to customize file organization
- You need to understand AI behavior
- You're adding new media types
- You want to modify naming conventions

**Key Sections**:
- Movies, TV Shows, Music, Books, Software
- Folder structures
- Naming conventions
- JSON examples
- Custom rule guide

**Media Types Covered**:
- 🎬 Movies
- 📺 TV Shows
- 🎵 Music
- 📚 Books (Audiobooks, eBooks, Comics)
- 💻 Software
- 📦 Other

---

### 07. Development Guide

**What's Inside**:
- Getting started
- Project structure
- Development setup
- Code style & standards
- Testing approaches
- Debugging techniques
- Contributing guidelines
- Deployment instructions

**Read This If**:
- You're a new developer
- You want to contribute
- You need to deploy to production
- You're setting up a dev environment

**Key Sections**:
- Quick start guide
- IDE setup (VS Code, PyCharm)
- Code style standards
- Manual testing procedures
- Production deployment
- Monitoring and maintenance

**Tools Covered**:
- Virtual environments
- Git workflow
- Systemd service
- Nginx reverse proxy
- SSL with Let's Encrypt

---

## 🎯 Use Case Navigation

### "I want to understand how it works"
Start with: [01. Architecture Overview](01_Architecture_Overview.md)
Then read: [05. Processing Workflows](05_Processing_Workflows.md)

### "I want to develop new features"
Start with: [07. Development Guide](07_Development_Guide.md)
Then read: [02. Backend Components](02_Backend_Components.md)

### "I want to customize file organization"
Start with: [06. File Organization Rules](06_File_Organization_Rules.md)
Then read: [04. Configuration Guide](04_Configuration_Guide.md)

### "I want to deploy to production"
Start with: [07. Development Guide](07_Development_Guide.md) (Deployment section)
Then read: [04. Configuration Guide](04_Configuration_Guide.md)

### "I want to add a web UI feature"
Start with: [03. Frontend Interface](03_Frontend_Interface.md)
Then read: [02. Backend Components](02_Backend_Components.md) (for API changes)

### "I'm debugging an issue"
Start with: [05. Processing Workflows](05_Processing_Workflows.md)
Then read: [07. Development Guide](07_Development_Guide.md) (Debugging section)

---

## 📊 Documentation Statistics

- **Total Pages**: 7 comprehensive documents
- **Total Words**: ~50,000 words
- **Code Examples**: 100+ examples
- **Diagrams**: 15+ ASCII diagrams
- **API Endpoints**: 10 fully documented
- **Configuration Fields**: 10 detailed
- **Media Types**: 6 with examples
- **Workflows**: 4 complete flows

---

## 🔍 Quick Reference

### Key Concepts

**Job**: A file processing task with state tracking
**Status**: Current stage of job (Queued, Processing, Pending, Completed, Failed)
**Priority**: Flag for immediate processing (bypasses batch queue)
**Debounce**: Wait period before processing batch
**Batch**: Group of files processed together by AI

### Key Components

**Job Store**: Thread-safe job state storage
**Config Manager**: Configuration with live reload
**AI Processor**: Google AI (Gemini) integration
**Backend Orchestrator**: Central coordinator
**File Watchers**: Watchdog-based file monitoring
**Debounced Processor**: Batch timing manager

### Key Files

- `app.py`: Flask web server
- `config.json`: Public configuration
- `.env`: Secret API keys
- `instructions.md`: AI prompt
- `backend_orchestrator.py`: Main coordinator
- `job_store.py`: State management

### Key Endpoints

- `GET /api/jobs`: List all jobs
- `POST /api/jobs/{id}/edit`: Manual edit
- `POST /api/jobs/{id}/re-ai`: Re-process with AI
- `GET /api/config`: Get configuration
- `POST /api/config`: Update configuration
- `GET /api/stats`: Job statistics

---

## 🛠 Maintenance

This DeepWiki is maintained alongside the codebase. When making changes to the application:

1. **Update relevant documentation** immediately
2. **Add examples** for new features
3. **Update diagrams** if architecture changes
4. **Keep code and docs in sync**

### Contributing to Documentation

- Follow existing format and style
- Include code examples
- Add ASCII diagrams where helpful
- Test all code examples
- Proofread for clarity

---

## 📝 Document Format

Each document follows this structure:

1. **Table of Contents**: Quick navigation
2. **Overview**: Brief introduction
3. **Detailed Sections**: In-depth coverage
4. **Examples**: Code and usage examples
5. **Summary**: Key takeaways

### Formatting Conventions

- **Bold**: Important terms, field names
- *Italic*: Emphasis, file paths
- `Code`: Code, commands, values
- ```blocks```: Multi-line code examples
- 📊 Emojis: Section markers
- ASCII: Diagrams and flows

---

## 🚀 Getting Started

If you're new to Intelly Jelly:

1. **Read**: [01. Architecture Overview](01_Architecture_Overview.md)
2. **Setup**: Follow [07. Development Guide](07_Development_Guide.md)
3. **Configure**: Use [04. Configuration Guide](04_Configuration_Guide.md)
4. **Understand Workflows**: Read [05. Processing Workflows](05_Processing_Workflows.md)
5. **Customize**: Modify [06. File Organization Rules](06_File_Organization_Rules.md)

---

## 📞 Support

For questions or issues:

1. Search this DeepWiki
2. Check application logs (`intelly_jelly.log`)
3. Review [07. Development Guide](07_Development_Guide.md) debugging section
4. Create issue on GitHub

---

## 📄 License

This documentation is part of the Intelly Jelly project.

**License**: MIT License

---

## ✨ Acknowledgments

Created to provide comprehensive technical documentation for developers, administrators, and power users of Intelly Jelly.

**Author**: @JL-Bones

**Last Updated**: November 2025

---

*Happy organizing! 🍇*
