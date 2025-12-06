"""
TMDB API integration for movie and TV show information lookup.
Provides functions to search for movies, TV shows, and retrieve detailed episode information.
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TMDBClient:
    """Client for interacting with The Movie Database (TMDB) API."""
    
    BASE_URL = 'https://api.themoviedb.org/3'
    
    def __init__(self, api_key: str):
        """
        Initialize TMDB client with API key.
        
        Args:
            api_key: TMDB API key (v3 API key)
        """
        self.api_key = api_key
        self.headers = {'accept': 'application/json'}
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a request to the TMDB API.
        
        Args:
            endpoint: API endpoint (e.g., '/search/movie')
            params: Query parameters
            
        Returns:
            JSON response data or None on error
        """
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API request failed for {endpoint}: {e}")
            return None
    
    def search_movie(self, movie_name: str) -> Optional[Dict]:
        """
        Search for a movie and return basic information including release year.
        
        Args:
            movie_name: Name of the movie to search for
            
        Returns:
            Dictionary with 'title', 'year', 'id', 'original_title' or None if not found
        """
        logger.info(f"Searching for movie: {movie_name}")
        
        params = {
            'query': movie_name,
            'include_adult': 'false'
        }
        
        data = self._make_request('/search/movie', params)
        
        if data and data.get('results'):
            movie = data['results'][0]  # Get first match
            release_date = movie.get('release_date', '')
            year = release_date[:4] if release_date else 'Unknown'
            
            result = {
                'title': movie.get('title'),
                'original_title': movie.get('original_title'),
                'year': year,
                'id': movie.get('id'),
                'overview': movie.get('overview', ''),
                'release_date': release_date
            }
            
            logger.info(f"Found movie: {result['title']} ({result['year']}) [ID: {result['id']}]")
            return result
        
        logger.warning(f"No movie found for: {movie_name}")
        return None
    
    def search_tv_show(self, tv_show_name: str) -> Optional[Dict]:
        """
        Search for a TV show and return basic information.
        
        Args:
            tv_show_name: Name of the TV show to search for
            
        Returns:
            Dictionary with 'name', 'year', 'id', 'original_name' or None if not found
        """
        logger.info(f"Searching for TV show: {tv_show_name}")
        
        params = {
            'query': tv_show_name
        }
        
        data = self._make_request('/search/tv', params)
        
        if data and data.get('results'):
            show = data['results'][0]  # Get first match
            first_air_date = show.get('first_air_date', '')
            year = first_air_date[:4] if first_air_date else 'Unknown'
            
            result = {
                'name': show.get('name'),
                'original_name': show.get('original_name'),
                'year': year,
                'id': show.get('id'),
                'overview': show.get('overview', ''),
                'first_air_date': first_air_date
            }
            
            logger.info(f"Found TV show: {result['name']} ({result['year']}) [ID: {result['id']}]")
            return result
        
        logger.warning(f"No TV show found for: {tv_show_name}")
        return None
    
    def get_tv_season_info(self, show_id: int, season_number: int) -> Optional[Dict]:
        """
        Get detailed information about a specific season including all episodes.
        
        Args:
            show_id: TMDB ID of the TV show
            season_number: Season number (e.g., 1, 2, 3)
            
        Returns:
            Dictionary with season info and list of episodes or None on error
        """
        logger.info(f"Fetching season {season_number} info for show ID: {show_id}")
        
        endpoint = f'/tv/{show_id}/season/{season_number}'
        data = self._make_request(endpoint)
        
        if data:
            episodes = []
            for ep in data.get('episodes', []):
                air_date = ep.get('air_date', '')
                episode_info = {
                    'episode_number': ep.get('episode_number'),
                    'name': ep.get('name'),
                    'air_date': air_date,
                    'year': air_date[:4] if air_date else 'Unknown',
                    'overview': ep.get('overview', ''),
                    'season_number': ep.get('season_number')
                }
                episodes.append(episode_info)
            
            result = {
                'season_number': data.get('season_number'),
                'name': data.get('name'),
                'air_date': data.get('air_date', ''),
                'episodes': episodes,
                'episode_count': len(episodes)
            }
            
            logger.info(f"Found {len(episodes)} episodes for season {season_number}")
            return result
        
        logger.warning(f"No season info found for show ID {show_id}, season {season_number}")
        return None
    
    def get_tv_episode_info(self, tv_show_name: str, season_number: int, episode_number: Optional[int] = None) -> Optional[Dict]:
        """
        Get episode information for a TV show. First searches for the show, then fetches episode details.
        
        Args:
            tv_show_name: Name of the TV show
            season_number: Season number
            episode_number: Optional specific episode number. If None, returns all episodes in season.
            
        Returns:
            Dictionary with show info and episode(s) information or None on error
        """
        # First, search for the show
        show_info = self.search_tv_show(tv_show_name)
        if not show_info:
            return None
        
        # Then get season details
        season_info = self.get_tv_season_info(show_info['id'], season_number)
        if not season_info:
            return None
        
        # If specific episode requested, filter to that episode
        if episode_number is not None:
            episodes = [ep for ep in season_info['episodes'] if ep['episode_number'] == episode_number]
            if not episodes:
                logger.warning(f"Episode {episode_number} not found in season {season_number}")
                return None
            season_info['episodes'] = episodes
        
        # Combine show and season info
        result = {
            'show_name': show_info['name'],
            'show_year': show_info['year'],
            'show_id': show_info['id'],
            'season_number': season_info['season_number'],
            'episodes': season_info['episodes']
        }
        
        return result
    
    def batch_search(self, queries: List[Dict[str, str]]) -> List[Dict]:
        """
        Perform multiple searches in batch.
        
        Args:
            queries: List of query dictionaries with 'type' (movie/tv) and 'name' keys
            
        Returns:
            List of results matching the query order
        """
        results = []
        
        for query in queries:
            query_type = query.get('type', 'movie').lower()
            name = query.get('name', '')
            
            if not name:
                results.append(None)
                continue
            
            if query_type == 'tv' or query_type == 'tv_show':
                result = self.search_tv_show(name)
            else:
                result = self.search_movie(name)
            
            results.append(result)
        
        return results


def format_tool_response(tmdb_result: Optional[Dict], query_type: str = 'movie') -> str:
    """
    Format TMDB API result as a natural language response for AI tool use.
    
    Args:
        tmdb_result: Result from TMDB search
        query_type: Type of query ('movie', 'tv', or 'episode')
        
    Returns:
        Formatted string response
    """
    if not tmdb_result:
        return "No results found in TMDB."
    
    if query_type == 'movie':
        return (f"Movie: {tmdb_result['title']} ({tmdb_result['year']})\n"
                f"Original Title: {tmdb_result.get('original_title', 'N/A')}\n"
                f"Release Date: {tmdb_result.get('release_date', 'Unknown')}\n"
                f"TMDB ID: {tmdb_result['id']}")
    
    elif query_type == 'tv':
        return (f"TV Show: {tmdb_result['name']} ({tmdb_result['year']})\n"
                f"Original Name: {tmdb_result.get('original_name', 'N/A')}\n"
                f"First Air Date: {tmdb_result.get('first_air_date', 'Unknown')}\n"
                f"TMDB ID: {tmdb_result['id']}")
    
    elif query_type == 'episode':
        show_info = f"Show: {tmdb_result['show_name']} ({tmdb_result['show_year']})\n"
        show_info += f"Season {tmdb_result['season_number']} Episodes:\n"
        
        for ep in tmdb_result['episodes']:
            show_info += (f"  E{ep['episode_number']:02d}: {ep['name']} "
                         f"(Aired: {ep['air_date'] or 'Unknown'})\n")
        
        return show_info
    
    return str(tmdb_result)
