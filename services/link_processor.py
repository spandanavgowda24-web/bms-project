import requests


def clean_url(url):
    """
    Validate and clean URL
    Only allow real video links
    """

    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        final_url = response.url

        print("Original URL:", url)
        print("Final URL:", final_url)

        # ❌ Reject search/redirect pages
        if any(x in final_url for x in [
            "bing.com",
            "google.com/search",
            "google.com/url"
        ]):
            return None

        # ❌ Reject non-http
        if not final_url.startswith("http"):
            return None

        # ✅ Allow only trusted platforms (you can add more)
        allowed_sites = [
            "youtube.com",
            "youtu.be",
            "instagram.com",
            "fb.watch",
            "facebook.com"
        ]

        if not any(site in final_url for site in allowed_sites):
            return None

        return final_url

    except Exception as e:
        print("URL cleaning error:", e)
        return None