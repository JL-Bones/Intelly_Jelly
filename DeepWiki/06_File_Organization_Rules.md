# File Organization Rules & AI Instructions

## Table of Contents
1. [Overview](#overview)
2. [Instructions File Format](#instructions-file-format)
3. [Media Organization Rules](#media-organization-rules)
4. [JSON Response Format](#json-response-format)
5. [Examples by Media Type](#examples-by-media-type)
6. [Custom Rule Creation](#custom-rule-creation)

---

## Overview

The `instructions.md` file contains comprehensive rules that guide the AI in determining proper file names and organization structure. This file is critical to the quality of the AI's suggestions.

**Location**: Configurable via `INSTRUCTIONS_FILE_PATH` (default: `./instructions.md`)

**Purpose**: 
- Define naming conventions for all media types
- Specify folder structures
- Provide examples for the AI
- Ensure consistent organization

**When Used**: Read before each AI batch processing request

---

## Instructions File Format

### Structure

The instructions file uses a hierarchical structure:

1. **Core Task & Output Format**: What the AI should do and return
2. **General Rules**: Universal processing guidelines
3. **Media Organization Rules**: Specific rules per media type
4. **Examples**: JSON samples for each media type

### Key Sections

#### 1. Core Task

Tells the AI its primary objective:
- Process all input files
- Find missing information via web search if needed
- Return structured JSON with suggestions

#### 2. Output Format

Defines the expected JSON structure:
```json
[
  {
    "original_path": "input file path",
    "suggested_name": "output filename only",
    "confidence": 0-100
  }
]
```

**Important**: `suggested_name` should be **filename only**, not full path

#### 3. General Rules

- Process every file in the list
- Use web search for missing information
- Follow strict naming conventions
- Handle special cases (versions, extras, etc.)

---

## Media Organization Rules

### Movies

#### Folder Structure
```
Movies/
└── Movie Title (Year)/
    ├── Movie Title (Year).mkv
    ├── Movie Title (Year).en.srt
    ├── Movie Title (Year) - 1080p.mkv
    └── extras/
        ├── trailers/
        ├── behind the scenes/
        └── deleted scenes/
```

#### Naming Convention

**Main File**: `Movie Title (Year).ext`

**Examples**:
- `The Matrix (1999).mkv`
- `Inception (2010).mp4`
- `Blade Runner 2049 (2017).mkv`

**With Version Suffix**: `Movie Title (Year) - Version.ext`

**Examples**:
- `The Matrix (1999) - 1080p.mkv`
- `Blade Runner (1982) - Directors Cut.mkv`
- `The Lord of the Rings (2001) - Extended Edition.mkv`

**Subtitles**: `Movie Title (Year).language.srt`

**Examples**:
- `The Matrix (1999).en.srt`
- `The Matrix (1999).es.srt`

#### Extras Subfolders

Valid subfolder names:
- `behind the scenes`
- `deleted scenes`
- `interviews`
- `scenes`
- `samples`
- `shorts`
- `featurettes`
- `clips`
- `other`
- `extras`
- `trailers`

Files in extras folders use descriptive names:
- `trailers/Main Trailer.mp4`
- `behind the scenes/Making Of.mkv`

### TV Shows

#### Folder Structure
```
TV Shows/
└── Series Name (Year)/
    ├── Season 01/
    │   ├── Series Name (Year) - S01E01.mkv
    │   ├── Series Name (Year) - S01E02.mkv
    │   └── ...
    ├── Season 02/
    │   └── ...
    └── extras/
        └── interviews/
```

#### Naming Convention

**Standard Episode**: `Series Name (Year) - SXXEYY.ext`

**Examples**:
- `Breaking Bad (2008) - S01E01.mkv`
- `Game of Thrones (2011) - S05E09.mkv`
- `The Office (2005) - S02E03.mp4`

**Multi-Part Episode**: `Series Name (Year) - SXXEYY - EZZ.ext`

**Examples**:
- `Doctor Who (2005) - S04E12 - E13.mkv`
- `Battlestar Galactica (2004) - S01E01 - E02.mkv`

**With Episode Title**: `Series Name (Year) - SXXEYY - Episode Name.ext`

**Examples**:
- `Breaking Bad (2008) - S01E01 - Pilot.mkv`
- `Game of Thrones (2011) - S01E01 - Winter Is Coming.mkv`

#### Season Numbering

Always use two digits:
- `Season 01` (not `Season 1`)
- `S01E01` (not `S1E1`)

#### Extras

Can be at series level or season level:
- `Series Name (Year)/extras/`
- `Series Name (Year)/Season 01/extras/`

### Music

#### Folder Structure
```
Music/
├── Artist Name/
│   └── Album Name/
│       ├── 01 - Track Title.mp3
│       ├── 02 - Another Track.mp3
│       └── 01 - Track Title.lrc
└── Album Name/
    └── (same structure)
```

#### Naming Convention

**With Track Numbers**: `01 - Song Title.ext`

**Examples**:
- `01 - Bohemian Rhapsody.mp3`
- `02 - We Are the Champions.flac`
- `03 - Somebody to Love.m4a`

**Multi-Disc Albums**:

Option 1: Subfolders
```
Album Name/
├── Disc 1/
│   ├── 01 - Track.mp3
│   └── 02 - Track.mp3
└── Disc 2/
    ├── 01 - Track.mp3
    └── 02 - Track.mp3
```

Option 2: Tags (preferred)
```
Album Name/
├── 01 - Track.mp3  (disc=1 in tags)
├── 02 - Track.mp3  (disc=1 in tags)
├── 03 - Track.mp3  (disc=2 in tags)
└── 04 - Track.mp3  (disc=2 in tags)
```

#### Lyrics

**Must match audio filename exactly**:
- Audio: `01 - Song Title.mp3`
- Lyrics: `01 - Song Title.lrc` (or `.txt`, `.elrc`)

### Books

#### Audiobooks

```
Books/
└── Audiobooks/
    └── [Author Name]/
        └── [Book Title]/
            ├── Chapter 01.mp3
            ├── Chapter 02.mp3
            └── ...
```

**Examples**:
- `Books/Audiobooks/J.K. Rowling/Harry Potter and the Philosophers Stone/Chapter 01.mp3`
- `Books/Audiobooks/Stephen King/The Shining/Part 1.m4b`

Author folder optional if unknown:
- `Books/Audiobooks/Unknown Book/file.mp3`

#### eBooks

```
Books/
└── Books/
    └── [Author Name]/
        └── [Book Title]/
            └── Book Title.epub
```

**Examples**:
- `Books/Books/George Orwell/1984/1984.epub`
- `Books/Books/Isaac Asimov/Foundation/Foundation.pdf`

#### Comics

```
Books/
└── Comics/
    └── [Series Name (Year)]/
        ├── Series Name #001 (Year).cbz
        ├── Series Name #002 (Year).cbz
        └── ...
```

**Examples**:
- `Books/Comics/The Amazing Spider-Man (1963)/The Amazing Spider-Man #001 (1963).cbz`
- `Books/Comics/Batman (1940)/Batman #001 (1940).cbr`

### Software

#### Folder Structure
```
Software/
└── [Software Name]/
    ├── setup.exe
    ├── readme.txt
    └── subfolders...
```

**Keep original structure within software folder**

**Examples**:
- `Software/Adobe Photoshop 2024/`
- `Software/Microsoft Office 365/`
- `Software/Ableton Live 11 Suite v11.3.12/`

#### Naming

Keep original filenames and folder structure intact.

### Other

#### Folder Structure
```
Other/
└── [original name and structure]
```

**Purpose**: Catch-all for unclassified files

**Examples**:
- `Other/document.pdf`
- `Other/random_file.zip`
- `Other/subfolder/file.txt`

---

## JSON Response Format

### Required Structure

The AI must return a JSON array:

```json
[
  {
    "original_path": "string",
    "suggested_name": "string",
    "confidence": number
  }
]
```

### Field Specifications

**`original_path`** (string, required):
- Exact match of input file path
- Used to correlate result with job
- Must match one of the input paths

**`suggested_name`** (string, required):
- **Filename only**, not full path
- Includes extension
- Follows naming conventions
- Ready to use as final filename

**`confidence`** (number, required):
- Integer from 0 to 100
- Represents AI's certainty
- Higher = more confident
- Typical ranges:
  - 90-100: High confidence, clear metadata
  - 70-89: Good confidence, some assumptions
  - 50-69: Moderate confidence, missing data
  - Below 50: Low confidence, guesswork

### Alternative Format

The AI may also return:

```json
{
  "files": [
    {
      "original_path": "...",
      "suggested_name": "...",
      "confidence": ...
    }
  ]
}
```

The application handles both formats.

---

## Examples by Media Type

### Movie Examples

**Input**:
```
C:/Downloads/best.movie.2019.1080p.BluRay.mp4
```

**Output**:
```json
{
  "original_path": "C:/Downloads/best.movie.2019.1080p.BluRay.mp4",
  "suggested_name": "Best Movie (2019) - 1080p.mp4",
  "confidence": 100
}
```

**Input**:
```
movie_directors_cut_2020.mkv
```

**Output**:
```json
{
  "original_path": "movie_directors_cut_2020.mkv",
  "suggested_name": "Movie Title (2020) - Directors Cut.mkv",
  "confidence": 95
}
```

### TV Show Examples

**Input**:
```
series.name.s02e05.hdtv.x264.mkv
```

**Output**:
```json
{
  "original_path": "series.name.s02e05.hdtv.x264.mkv",
  "suggested_name": "Series Name (2015) - S02E05.mkv",
  "confidence": 100
}
```

**Input**:
```
show.2x03.The.Episode.Name.mp4
```

**Output**:
```json
{
  "original_path": "show.2x03.The.Episode.Name.mp4",
  "suggested_name": "Show Title (2020) - S02E03 - The Episode Name.mp4",
  "confidence": 98
}
```

### Music Examples

**Input**:
```
01-artist-song_title.mp3
```

**Output**:
```json
{
  "original_path": "01-artist-song_title.mp3",
  "suggested_name": "01 - Song Title.mp3",
  "confidence": 95
}
```

**Input**:
```
Album/track2.flac
```

**Output**:
```json
{
  "original_path": "Album/track2.flac",
  "suggested_name": "02 - Track Name.flac",
  "confidence": 85
}
```

### Book Examples

**Input**:
```
author_book1_2023.epub
```

**Output**:
```json
{
  "original_path": "author_book1_2023.epub",
  "suggested_name": "Book Title.epub",
  "confidence": 90
}
```

**Input**:
```
comic_series_001_1995.cbz
```

**Output**:
```json
{
  "original_path": "comic_series_001_1995.cbz",
  "suggested_name": "Comic Series #001 (1995).cbz",
  "confidence": 100
}
```

### Software Examples

**Input**:
```
Software/app_v2.0_cracked/setup.exe
```

**Output**:
```json
{
  "original_path": "Software/app_v2.0_cracked/setup.exe",
  "suggested_name": "setup.exe",
  "confidence": 100
}
```

### Other Examples

**Input**:
```
random_document.pdf
```

**Output**:
```json
{
  "original_path": "random_document.pdf",
  "suggested_name": "random_document.pdf",
  "confidence": 100
}
```

---

## Custom Rule Creation

### Adding New Media Types

To add a new media type:

1. **Define Folder Structure**:
```markdown
#### 📷 Photos

* **Folder Structure:** `Photos/[Year]/[Month]/`
* **File Naming:** `YYYY-MM-DD_Description.ext`
```

2. **Specify Naming Rules**:
```markdown
**Standard Photo**: `YYYY-MM-DD_HH-MM-SS.ext`
**With Description**: `YYYY-MM-DD_Description.ext`
```

3. **Provide Examples**:
```markdown
**Example JSON Output:**
```json
[
  {
    "original_path": "IMG_1234.jpg",
    "suggested_name": "2024-03-15_Birthday_Party.jpg",
    "confidence": 90
  }
]
```
```

4. **Test with Dry Run**:
```json
{
  "DRY_RUN_MODE": true
}
```

5. **Add to instructions.md**

### Modifying Existing Rules

To modify existing rules:

1. **Open instructions.md**

2. **Find the relevant section**

3. **Modify the rules**:
```markdown
**Old**:
`Movie Title (Year).ext`

**New**:
`[Year] Movie Title.ext`
```

4. **Update examples**

5. **Save and test**

### Best Practices

**Be Specific**:
- Provide exact formatting
- Include all variations
- Show special character handling

**Provide Context**:
- Explain why rules exist
- Document edge cases
- Include real-world examples

**Use Examples**:
- Show input → output clearly
- Cover common scenarios
- Include edge cases

**Test Thoroughly**:
- Use dry run mode
- Test with various file types
- Verify edge cases

**Document Exceptions**:
- Note special handling
- Explain unusual rules
- Provide reasoning

---

## Summary

The instructions file is the brain of Intelly Jelly's organization system:

1. **Comprehensive**: Covers all common media types
2. **Structured**: Clear hierarchy and sections
3. **Example-Driven**: JSON examples for clarity
4. **Customizable**: Easy to modify and extend
5. **AI-Friendly**: Formatted for LLM understanding

Proper instruction design ensures high-quality, consistent file organization.
