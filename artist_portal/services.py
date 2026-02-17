"""
Fetch and normalize Spotify and Apple Music data for artist profiles.

- Spotify: requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in settings/env.
  Uses Client Credentials flow; extracts artist ID from profile Spotify URL.
- Apple Music: uses iTunes Search API (no auth). Search by artist name or parse
  Apple Music URL when provided.
"""

import re
import logging
import requests

logger = logging.getLogger(__name__)


def _spotify_token(client_id: str, client_secret: str) -> str | None:
    """Get Spotify API access token via Client Credentials flow."""
    try:
        r = requests.post(
            'https://accounts.spotify.com/api/token',
            data={'grant_type': 'client_credentials'},
            auth=(client_id, client_secret),
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get('access_token')
    except Exception as e:
        logger.warning("Spotify token request failed: %s", e)
        return None


def _spotify_artist_id_from_url(url: str) -> str | None:
    """Extract Spotify artist ID from URL like https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm."""
    if not url or not url.strip():
        return None
    # Match /artist/ID where ID is alphanumeric
    m = re.search(r'open\.spotify\.com/artist/([A-Za-z0-9]+)', url)
    if m:
        return m.group(1)
    # If they pasted just the ID
    if re.match(r'^[A-Za-z0-9]{22}$', url.strip()):
        return url.strip()
    return None


def fetch_spotify_artist(spotify_url: str, client_id: str, client_secret: str) -> dict | None:
    """
    Fetch artist data from Spotify Web API.
    Returns dict with keys: followers, popularity, genres, images, (or None on failure).
    """
    artist_id = _spotify_artist_id_from_url(spotify_url)
    if not artist_id:
        logger.warning("Could not parse Spotify artist ID from url=%s", spotify_url)
        return None

    token = _spotify_token(client_id, client_secret)
    if not token:
        return None

    try:
        r = requests.get(
            f'https://api.spotify.com/v1/artists/{artist_id}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'followers': data.get('followers'),
            'popularity': data.get('popularity'),
            'genres': data.get('genres') or [],
            'images': data.get('images') or [],
            'external_urls': data.get('external_urls'),
        }
    except Exception as e:
        logger.warning("Spotify artist fetch failed for id=%s: %s", artist_id, e)
        return None


def _apple_music_artist_id_from_url(url: str) -> str | None:
    """Extract Apple Music artist ID from URL if present."""
    if not url or not url.strip():
        return None
    # music.apple.com/.../artist/.../id123456789
    m = re.search(r'music\.apple\.com/[^/]+/artist/[^/]+/(?:id)?(\d+)', url)
    if m:
        return m.group(1)
    return None


def fetch_apple_music_artist(apple_music_url: str | None, artist_name: str) -> dict | None:
    """
    Fetch artist data from iTunes Search API (Apple Music).
    Either pass apple_music_url (we use artist name from our side for display) or
    artist_name to search. Returns dict with artistId, artistName, artistLinkUrl, etc.
    """
    # If we have a URL with an ID we could in theory look up by ID, but iTunes Search
    # doesn't support lookup by ID easily; we use search by name and take first result.
    name_to_search = artist_name or ''
    if not name_to_search.strip():
        return None

    try:
        r = requests.get(
            'https://itunes.apple.com/search',
            params={'term': name_to_search, 'entity': 'musicArtist', 'limit': 1},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get('results')
        if not results:
            return None
        first = results[0]
        return {
            'artistId': first.get('artistId'),
            'artistName': first.get('artistName'),
            'artistLinkUrl': first.get('artistLinkUrl'),
            'primaryGenreName': first.get('primaryGenreName'),
        }
    except Exception as e:
        logger.warning("Apple Music (iTunes) search failed for name=%s: %s", name_to_search, e)
        return None


def refresh_streaming_data_for_profile(profile, spotify_client_id: str | None, spotify_client_secret: str | None) -> None:
    """
    Fetch Spotify and Apple Music data for the given ArtistProfile and save
    into ArtistStreamingData (create if needed). Uses profile.spotify and
    profile.apple_music URLs, and profile.user.username as fallback artist name.
    """
    from django.utils import timezone
    from .models import ArtistStreamingData

    streaming, _ = ArtistStreamingData.objects.get_or_create(profile=profile)
    artist_name = profile.user.get_full_name() or profile.user.username or ''
    updated = False

    if profile.spotify and spotify_client_id and spotify_client_secret:
        data = fetch_spotify_artist(profile.spotify, spotify_client_id, spotify_client_secret)
        if data:
            streaming.spotify_data = data
            streaming.spotify_updated_at = timezone.now()
            updated = True

    if profile.apple_music or artist_name:
        data = fetch_apple_music_artist(profile.apple_music, artist_name)
        if data:
            streaming.apple_music_data = data
            streaming.apple_music_updated_at = timezone.now()
            updated = True

    if updated:
        streaming.save()
