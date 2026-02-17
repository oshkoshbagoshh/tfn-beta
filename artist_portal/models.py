from django.db import models
from django.utils import timezone
from music_beta.models import User, Track
import uuid
import os

def artist_profile_image_path(instance, filename):
    """
    Generate a unique file path for artist profile images.

    Args:
        instance (Model instance): The ArtistProfile model instance.
        filename (str): The original filename of the uploaded image.

    Returns:
        str: The file path with a UUID as filename inside 'artist_profiles' directory.
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('artist_profiles', filename)

class ArtistProfile(models.Model):
    """
    Represents an artist's profile with additional information.

    Fields:
        user (ForeignKey): The user associated with this profile.
        profile_picture (FileField): The artist's profile picture.
        bio (TextField): A detailed biography of the artist.
        contact_email (EmailField): Contact email for the artist.
        phone (CharField): Contact phone number for the artist.
        website (URLField): Artist's website URL.
        facebook (URLField): Artist's Facebook profile URL.
        twitter (URLField): Artist's Twitter profile URL.
        instagram (URLField): Artist's Instagram profile URL.
        spotify (URLField): Artist's Spotify profile URL.
        apple_music (URLField): Artist's Apple Music profile URL.
        soundcloud (URLField): Artist's SoundCloud profile URL.
        youtube (URLField): Artist's YouTube channel URL.
        featured_track (ForeignKey): A track featured on the artist's profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    profile_picture = models.FileField(upload_to=artist_profile_image_path, blank=True, null=True)
    bio = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    # Social media links
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    spotify = models.URLField(blank=True)
    apple_music = models.URLField(blank=True)
    soundcloud = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    # Featured track
    featured_track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_on_profiles')

    def __str__(self):
        return f"{self.user.username}'s Artist Profile"

    @property
    def profile_picture_url(self):
        """
        Returns the URL for the artist's profile picture.
        If no image is set or accessible, returns a fallback placeholder image URL.

        Returns:
            str: URL to the artist's profile picture or a fallback image.
        """
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            try:
                # Access URL to ensure file exists
                _ = self.profile_picture.url
                return self.profile_picture.url
            except Exception:
                # Fall back to placeholder if image access fails
                pass
        # Fallback placeholder URL with random image keyed by user id
        return f'https://picsum.photos/300?random={self.user.id}'


class ArtistStreamingData(models.Model):
    """
    Cached Spotify and Apple Music data for an artist profile.
    Fetched when artist saves profile with Spotify/Apple Music URLs or via "Refresh" button.
    """
    profile = models.OneToOneField(
        ArtistProfile, on_delete=models.CASCADE, related_name='streaming_data'
    )
    # Spotify: stored as JSON from API (followers, popularity, genres, image_url, etc.)
    spotify_data = models.JSONField(blank=True, null=True)
    spotify_updated_at = models.DateTimeField(blank=True, null=True)
    # Apple Music: stored as JSON (artist_id, name, link, etc.)
    apple_music_data = models.JSONField(blank=True, null=True)
    apple_music_updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Streaming data for {self.profile.user.username}"

    @property
    def spotify_followers(self):
        """Convenience: follower count from cached Spotify data."""
        if self.spotify_data and isinstance(self.spotify_data.get('followers'), dict):
            return self.spotify_data['followers'].get('total')
        return None

    @property
    def spotify_popularity(self):
        """Convenience: 0-100 popularity from cached Spotify data."""
        if self.spotify_data is not None:
            return self.spotify_data.get('popularity')
        return None

    @property
    def spotify_genres(self):
        """Convenience: list of genre strings from cached Spotify data."""
        if self.spotify_data and isinstance(self.spotify_data.get('genres'), list):
            return self.spotify_data['genres']
        return []

    @property
    def spotify_image_url(self):
        """First image URL from cached Spotify data."""
        if self.spotify_data and self.spotify_data.get('images'):
            return self.spotify_data['images'][0].get('url')
        return None

    @property
    def apple_music_url(self):
        """Apple Music artist link from cached data."""
        if self.apple_music_data:
            return self.apple_music_data.get('artistLinkUrl') or self.apple_music_data.get('url')
        return None
