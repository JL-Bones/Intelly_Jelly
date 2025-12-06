#!/usr/bin/env python3
"""
Test script for TMDB API integration.
Verifies that TMDB client can successfully query movie and TV show information.
"""

from backend.tmdb_api import TMDBClient, format_tool_response
from backend.config_manager import ConfigManager

def test_tmdb_integration():
    """Test TMDB API integration with real queries."""
    
    print("=" * 80)
    print("TMDB API Integration Test")
    print("=" * 80)
    
    # Load config
    config = ConfigManager()
    tmdb_api_key = config.get('TMDB_API_KEY', '')
    
    if not tmdb_api_key:
        print("\n❌ TMDB_API_KEY not found in config.json")
        print("Please add your TMDB API key to config.json or configure it in Settings")
        return False
    
    print(f"\n✅ Found TMDB API Key: {tmdb_api_key[:10]}...")
    
    # Initialize client
    client = TMDBClient(tmdb_api_key)
    
    # Test 1: Search for a movie
    print("\n" + "=" * 80)
    print("Test 1: Search for Movie - 'Inception'")
    print("=" * 80)
    
    movie_result = client.search_movie("Inception")
    if movie_result:
        print("\n✅ Movie search successful!")
        print(format_tool_response(movie_result, "movie"))
    else:
        print("\n❌ Movie search failed")
        return False
    
    # Test 2: Search for a TV show
    print("\n" + "=" * 80)
    print("Test 2: Search for TV Show - 'Breaking Bad'")
    print("=" * 80)
    
    tv_result = client.search_tv_show("Breaking Bad")
    if tv_result:
        print("\n✅ TV show search successful!")
        print(format_tool_response(tv_result, "tv"))
    else:
        print("\n❌ TV show search failed")
        return False
    
    # Test 3: Get episode information
    print("\n" + "=" * 80)
    print("Test 3: Get Episode Info - 'Breaking Bad' Season 1")
    print("=" * 80)
    
    episode_result = client.get_tv_episode_info("Breaking Bad", 1)
    if episode_result:
        print("\n✅ Episode info retrieval successful!")
        print(format_tool_response(episode_result, "episode"))
    else:
        print("\n❌ Episode info retrieval failed")
        return False
    
    # Test 4: Batch search
    print("\n" + "=" * 80)
    print("Test 4: Batch Search - Multiple Queries")
    print("=" * 80)
    
    queries = [
        {"type": "movie", "name": "The Matrix"},
        {"type": "tv", "name": "Game of Thrones"},
        {"type": "movie", "name": "Interstellar"}
    ]
    
    batch_results = client.batch_search(queries)
    print(f"\n✅ Batch search completed - {len(batch_results)} results")
    for i, result in enumerate(batch_results):
        if result:
            query_type = queries[i]["type"]
            print(f"\nResult {i+1} ({query_type}):")
            print(f"  Title: {result.get('title') or result.get('name')}")
            print(f"  Year: {result.get('year')}")
        else:
            print(f"\nResult {i+1}: No data found")
    
    print("\n" + "=" * 80)
    print("✅ All TMDB tests passed successfully!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = test_tmdb_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
