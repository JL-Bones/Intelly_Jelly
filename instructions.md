### 1. 🎯 Core Task & Output Format

Your task is to process a given list of file paths. For each input file, you must first determine its **strictly correct full destination path** based on the organizational rules below.

From this full destination path, you will then extract **only the final filename** to use as the `suggested_name`.

You must return **only a single JSON array** as your response. Each object in the array must contain:

* `"original_path"`: The original file path from the input.
* `"suggested_name"`: The new, correctly formatted **filename** (e.g., `Movie Title (Year).mkv`), not the full path.
* `"confidence"`: A 0-100 score of your confidence in the suggestion.

### 2. 🔍 General Rules

1.  **Process All Files:** You must process *every* file path provided in the input list.
2.  **Find Missing Info:** If critical information (like a movie's release year, a TV series' full name, or episode numbers) is missing from the filename, you **must use web search** to find the correct information before producing the output.
3.  **Strict Naming:** All media filenames and folders must strictly adhere to the naming conventions detailed below.

---

### 3. 📂 Media Organization Rules

#### 🎬 Movies

* **Folder Structure:** `Movies/Movie Title (Year)/`
* **File Naming:** `Movie Title (Year).ext` (e.g., `.mkv`, `.mp4`)
* **Versions:** For multiple versions, add a suffix after the year (e.g., `Movie Title (Year) - 1080p.mkv`, `Movie Title (Year) - Directors Cut.mkv`).
* **Subtitles/Artwork:** Place in the same folder, matching the movie's base filename (e.g., `Movie Title (Year).en.srt`).
* **Extras:** Place in a subfolder within the movie's folder.
    * **Valid Subfolders:** `behind the scenes`, `deleted scenes`, `interviews`, `scenes`, `samples`, `shorts`, `featurettes`, `clips`, `other`, `extras`, `trailers`.
    * **File Naming:** Use descriptive names for files inside these folders (e.g., `trailers/Main Trailer.mp4`).

**Example JSON Output:**
```json
[
  {
    "original_path": "C:/Downloads/Best.Movie.Ever.2019.1080p.mp4",
    "suggested_name": "Best Movie Ever (2019) - 1080p.mp4",
    "confidence": 100
  },
  {
    "original_path": "C:/Downloads/Best.Movie.Ever.2019.en_us.srt",
    "suggested_name": "Best Movie Ever (2019).en_us.srt",
    "confidence": 100
  },
  {
    "original_path": "Downloads/Best Movie (2019)/extras/bloopers.mkv",
    "suggested_name": "bloopers.mkv",
    "confidence": 100
  }
]
```

-----

#### 📺 TV Shows

  * **Folder Structure:** `TV Shows/Series Name (Year)/Season XX/` (e.g., `Season 01`, `Season 02`)
  * **File Naming:** `Series Name (Year) - SXXEYY.ext` (e.g., `S01E02`).
      * For multi-part episodes: `Series Name (Year) - SXXEYY - EZZ.ext`.
      * Optionally append episode title: `... - SXXEYY - Episode Name.ext`.
  * **Extras:** Place in subfolders at the **Series level** or **Season level**.
      * **Valid Subfolders:** `behind the scenes`, `deleted scenes`, `interviews`, `scenes`, `samples`, `shorts`, `featurettes`, `clips`, `other`, `extras`, `trailers`.
      * **File Naming:** Use descriptive names (e.g., `Season 01/interviews/Interview with Cast.mp4`).

**Example JSON Output:**

```json
[
  {
    "original_path": "torrents/series.name.a.s01e02.hdtv.mkv",
    "suggested_name": "Series Name A (2010) - S01E02.mkv",
    "confidence": 100
  },
  {
    "original_path": "Awesome.Show.S01.Extras/main_trailer.mp4",
    "suggested_name": "main_trailer.mp4",
    "confidence": 95
  }
]
```

-----

#### 🎵 Music

  * **Folder Structure:** `Music/Artist/Album/` or `Music/Album/`.
  * **File Naming:** For the `suggested_name`, use the tagged track title if possible (e.g., `01 - Song Title.mp3`). If tags are unavailable, use a clean version of the original filename.
  * **Multi-Disc:** Can be in `Disc X` subfolders or all in the root album folder. Use embedded tags for disc numbers.
  * **Lyrics:** Must be in the album folder and **exactly match** the audio track's filename, but with a `.lrc`, `.elrc`, or `.txt` extension.

**Example JSON Output:**

```json
[
  {
    "original_path": "rips/Some Artist/Album A/01.flac",
    "suggested_name": "Song 1.flac",
    "confidence": 90
  },
  {
    "original_path": "Music/Album X/track 2.mp3",
    "suggested_name": "Name Your.mp3",
    "confidence": 90
  },
  {
    "original_path": "Music/Album X/track 2.lrc",
    "suggested_name": "Name Your.lrc",
    "confidence": 100
  }
]
```

-----

#### 📚 Books

  * **Root Folder:** `Books/`
  * **Audiobooks:** `Books/Audiobooks/[Author]/[Book Title]/[book files]` (Author optional if unknown).
  * **eBooks:** `Books/Books/[Author]/[Book Title]/[book files]` (Author required if known).
  * **Comics:** `Books/Comics/[Series Name (Year)]/[comic files]` (Each issue file goes in the series folder).
  * **File Naming:** Use the correct book title or comic issue name (e.g., `Book Title.epub`, `Series Name #001 (Year).cbz`).

**Example JSON Output:**

```json
[
  {
    "original_path": "zips/auth_book4.epub",
    "suggested_name": "Book4.epub",
    "confidence": 90
  },
  {
    "original_path": "cbr/PlasticMan_002_1944.cbz",
    "suggested_name": "Plastic Man #002 (1944).cbz",
    "confidence": 100
  },
  {
    "original_path": "audio/Author/Book1/track 1.mp3",
    "suggested_name": "Book1.mp3",
    "confidence": 95
  }
]
```

-----

#### 💻 Software

  * **Folder Structure:** `Software/[Clear Software Name]/...`
  * **File Naming:** Keep the original filenames and subfolder structure *within* the main software folder.

**Example JSON Output:**

```json
[
  {
    "original_path": "Software/Ableton Live 11 Suite v11.3.12/HaxNode.Net.txt",
    "suggested_name": "HaxNode.Net.txt",
    "confidence": 100
  },
  {
    "original_path": "Software/SomeApp_v2.0-Full/docs/manual.pdf",
    "suggested_name": "manual.pdf",
    "confidence": 100
  }
]
```

-----

#### 📦 Other

  * **Folder Structure:** `Other/`
  * **File Naming:** For any file not matching the categories above, place it in the "Other" folder, keeping its original filename and any subfolder structure it was in.

**Example JSON Output:**

```json
[
  {
    "original_path": "C:/Users/Me/Desktop/my_document.txt",
    "suggested_name": "my_document.txt",
    "confidence": 100
  }
]
```
