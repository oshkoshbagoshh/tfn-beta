"""
Shared helpers for music_beta views (session user, redirects).
"""
from django.shortcuts import redirect
from django.contrib import messages

from .models import User


def get_session_user(request, require_client=False):
    """
    Return the current user from session or a redirect response if not logged in.

    Returns:
        tuple: (user, None) if valid; (None, HttpResponse) if redirect (e.g. login required).
    """
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to access this page.')
        return None, redirect('login')

    try:
        user = User.objects.get(id=request.session['user_id'])
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return None, redirect('login')

    if require_client and user.user_type != 'client':
        messages.error(request, 'You must be a client to access this page.')
        return None, redirect('home')

    return user, None
