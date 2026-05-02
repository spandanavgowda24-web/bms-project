# services/link_processor.py - Multi-platform support
import re
from urllib.parse import urlparse

# Supported platforms
SUPPORTED_PLATFORMS = {
    'youtube': {
        'domains': ['youtube.com', 'youtu.be'],
        'patterns': [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})'
        ]
    },
    'instagram': {
        'domains': ['instagram.com', 'instagr.am'],
        'patterns': [
            r'instagram\.com/p/([a-zA-Z0-9_-]+)',
            r'instagram\.com/reel/([a-zA-Z0-9_-]+)',
            r'instagram\.com/tv/([a-zA-Z0-9_-]+)'
        ]
    },
    'facebook': {
        'domains': ['facebook.com', 'fb.com', 'fb.watch'],
        'patterns': [
            r'facebook\.com/watch/\?v=(\d+)',
            r'facebook\.com/.*?/videos/(\d+)',
            r'fb\.watch/([a-zA-Z0-9]+)'
        ]
    },
    'twitter': {
        'domains': ['twitter.com', 'x.com'],
        'patterns': [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)'
        ]
    },
    'tiktok': {
        'domains': ['tiktok.com'],
        'patterns': [
            r'tiktok\.com/@\w+/video/(\d+)',
            r'tiktok\.com/t/([a-zA-Z0-9]+)'
        ]
    },
    'vimeo': {
        'domains': ['vimeo.com'],
        'patterns': [
            r'vimeo\.com/(\d+)'
        ]
    },
    'dailymotion': {
        'domains': ['dailymotion.com'],
        'patterns': [
            r'dailymotion\.com/video/([a-zA-Z0-9]+)'
        ]
    }
}


def clean_url(url: str) -> str:
    """Validate and clean video URLs from multiple platforms"""
    if not url:
        return None

    url = url.strip()

    # Add https if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')

        # Check if domain is supported
        is_supported = False
        platform = None

        for plat_name, plat_info in SUPPORTED_PLATFORMS.items():
            if any(d in domain for d in plat_info['domains']):
                is_supported = True
                platform = plat_name
                break

        if not is_supported:
            print(f"⚠️ Unsupported platform: {domain}")
            return None

        print(f"✅ Supported platform detected: {platform}")
        return url

    except Exception as e:
        print(f"URL parsing error: {e}")
        return None


def extract_video_id(url: str) -> dict:
    """Extract video ID and platform from URL"""
    url = clean_url(url)
    if not url:
        return None

    for platform, info in SUPPORTED_PLATFORMS.items():
        for pattern in info['patterns']:
            match = re.search(pattern, url)
            if match:
                return {
                    'platform': platform,
                    'video_id': match.group(1),
                    'full_url': url
                }

    return {'platform': 'unknown', 'video_id': None, 'full_url': url}


def get_platform_icon(platform: str) -> str:
    """Get emoji icon for platform"""
    icons = {
        'youtube': '▶️',
        'instagram': '📸',
        'facebook': '📘',
        'twitter': '🐦',
        'tiktok': '🎵',
        'vimeo': '🎬',
        'dailymotion': '🎥',
        'unknown': '🔗'
    }
    return icons.get(platform, '🔗')