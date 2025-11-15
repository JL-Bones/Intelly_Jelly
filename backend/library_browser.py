import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import math

logger = logging.getLogger(__name__)


class LibraryBrowser:
    """Browse and manage files in the library path."""
    
    def __init__(self, library_path: str):
        self.library_path = library_path
        self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
        self.subtitle_extensions = {'.srt', '.sub', '.vtt', '.ass', '.ssa'}
        self.supported_extensions = self.video_extensions | self.subtitle_extensions | {'.mp3', '.flac', '.wav', '.aac', '.m4a', '.pdf', '.epub', '.mobi'}
    
    def update_library_path(self, new_path: str):
        """Update the library path."""
        self.library_path = new_path
        logger.info(f"Library path updated to: {new_path}")
    
    def _get_all_files(self) -> List[Dict]:
        """Recursively get all files in the library path."""
        files = []
        
        if not os.path.exists(self.library_path):
            logger.warning(f"Library path does not exist: {self.library_path}")
            return files
        
        try:
            for root, dirs, filenames in os.walk(self.library_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    # Only include supported file types
                    if file_ext in self.supported_extensions:
                        relative_path = os.path.relpath(file_path, self.library_path)
                        file_size = os.path.getsize(file_path)
                        modified_time = os.path.getmtime(file_path)
                        
                        files.append({
                            'filename': filename,
                            'full_path': file_path,
                            'relative_path': relative_path,
                            'directory': os.path.dirname(relative_path),
                            'extension': file_ext,
                            'size': file_size,
                            'modified': modified_time,
                            'is_video': file_ext in self.video_extensions,
                            'is_subtitle': file_ext in self.subtitle_extensions
                        })
        
        except Exception as e:
            logger.error(f"Error scanning library path: {type(e).__name__}: {e}", exc_info=True)
        
        return files
    
    def get_files_paginated(self, page: int = 1, per_page: int = 50, search: Optional[str] = None, 
                           sort_by: str = 'modified', sort_order: str = 'desc') -> Dict:
        """
        Get files with pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            search: Optional search filter
            sort_by: Field to sort by (filename, modified, size)
            sort_order: Sort order (asc, desc)
            
        Returns:
            Dictionary with files, pagination info, and stats
        """
        all_files = self._get_all_files()
        
        # Filter by search if provided
        if search:
            search_lower = search.lower()
            all_files = [f for f in all_files if search_lower in f['filename'].lower() 
                        or search_lower in f['relative_path'].lower()]
        
        # Sort files
        reverse = (sort_order == 'desc')
        if sort_by == 'filename':
            all_files.sort(key=lambda x: x['filename'].lower(), reverse=reverse)
        elif sort_by == 'size':
            all_files.sort(key=lambda x: x['size'], reverse=reverse)
        else:  # modified
            all_files.sort(key=lambda x: x['modified'], reverse=reverse)
        
        # Calculate pagination
        total_files = len(all_files)
        total_pages = math.ceil(total_files / per_page) if total_files > 0 else 1
        page = max(1, min(page, total_pages))  # Clamp page to valid range
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_files = all_files[start_idx:end_idx]
        
        return {
            'files': page_files,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_files': total_files,
                'total_pages': total_pages,
                'has_previous': page > 1,
                'has_next': page < total_pages
            },
            'stats': {
                'total_files': total_files,
                'video_files': len([f for f in all_files if f['is_video']]),
                'subtitle_files': len([f for f in all_files if f['is_subtitle']]),
                'total_size': sum(f['size'] for f in all_files)
            }
        }
    
    def find_related_subtitle(self, video_path: str) -> Optional[str]:
        """Find subtitle file with matching base name."""
        video_dir = os.path.dirname(video_path)
        video_base = os.path.splitext(os.path.basename(video_path))[0]
        
        for ext in self.subtitle_extensions:
            subtitle_path = os.path.join(video_dir, video_base + ext)
            if os.path.exists(subtitle_path):
                return subtitle_path
        
        return None
    
    def rename_file(self, old_path: str, new_name: str, rename_subtitle: bool = True) -> Dict:
        """
        Rename a file and optionally its related subtitle.
        
        Args:
            old_path: Full path to the file to rename
            new_name: New filename (without path)
            rename_subtitle: If True and file is video, rename matching subtitle too
            
        Returns:
            Dictionary with success status and messages
        """
        result = {
            'success': False,
            'message': '',
            'renamed_files': []
        }
        
        try:
            if not os.path.exists(old_path):
                result['message'] = f"File not found: {old_path}"
                return result
            
            old_dir = os.path.dirname(old_path)
            old_filename = os.path.basename(old_path)
            old_ext = os.path.splitext(old_filename)[1]
            
            # Ensure new name has the same extension
            new_base = os.path.splitext(new_name)[0]
            new_filename = new_base + old_ext
            new_path = os.path.join(old_dir, new_filename)
            
            # Check if destination already exists
            if os.path.exists(new_path) and new_path != old_path:
                result['message'] = f"Destination file already exists: {new_filename}"
                return result
            
            # Rename the main file
            os.rename(old_path, new_path)
            result['renamed_files'].append({
                'old': old_path,
                'new': new_path,
                'type': 'main'
            })
            logger.info(f"Renamed file: {old_path} -> {new_path}")
            
            # If it's a video and rename_subtitle is True, try to rename subtitle
            if rename_subtitle and old_ext.lower() in self.video_extensions:
                subtitle_path = self.find_related_subtitle(old_path)
                if subtitle_path:
                    subtitle_ext = os.path.splitext(subtitle_path)[1]
                    new_subtitle_path = os.path.join(old_dir, new_base + subtitle_ext)
                    
                    try:
                        os.rename(subtitle_path, new_subtitle_path)
                        result['renamed_files'].append({
                            'old': subtitle_path,
                            'new': new_subtitle_path,
                            'type': 'subtitle'
                        })
                        logger.info(f"Renamed subtitle: {subtitle_path} -> {new_subtitle_path}")
                    except Exception as e:
                        logger.warning(f"Failed to rename subtitle: {e}")
            
            result['success'] = True
            result['message'] = f"Successfully renamed {len(result['renamed_files'])} file(s)"
            
        except Exception as e:
            logger.error(f"Error renaming file: {type(e).__name__}: {e}", exc_info=True)
            result['message'] = f"Error: {str(e)}"
        
        return result
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get detailed information about a specific file."""
        if not os.path.exists(file_path):
            return None
        
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        relative_path = os.path.relpath(file_path, self.library_path)
        
        info = {
            'filename': filename,
            'full_path': file_path,
            'relative_path': relative_path,
            'directory': os.path.dirname(relative_path),
            'extension': file_ext,
            'size': os.path.getsize(file_path),
            'modified': os.path.getmtime(file_path),
            'is_video': file_ext in self.video_extensions,
            'is_subtitle': file_ext in self.subtitle_extensions
        }
        
        # Check for related subtitle if it's a video
        if info['is_video']:
            subtitle_path = self.find_related_subtitle(file_path)
            info['has_subtitle'] = subtitle_path is not None
            info['subtitle_path'] = subtitle_path
        
        return info
