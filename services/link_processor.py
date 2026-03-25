import requests

def clean_url(url):
    """
    Validate and clean URL safely
    Supports YouTube, Insta, Facebook
    """

    try:
        # 🔥 HEAD request (FASTER + LIGHTER)
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=15   # 🔥 increased timeout
        )

        final_url = response.url

        print("Original URL:", url)
        print("Final URL:", final_url)

        # ❌ Reject search pages
        if any(x in final_url for x in [
            "bing.com",
            "google.com/search",
            "google.com/url"
        ]):
            print("❌ Invalid redirect page")
            return None

        # ❌ Reject invalid protocol
        if not final_url.startswith("http"):
            print("❌ Invalid protocol")
            return None

        # ✅ Allowed platforms
        allowed_sites = [
            "youtube.com",
            "youtu.be",
            "instagram.com",
            "fb.watch",
            "facebook.com",
            "twitter.com",
            "x.com",
            "tiktok.com"
        ]

        if not any(site in final_url for site in allowed_sites):
            print("❌ Unsupported platform")
            return None

        print("✅ Clean URL ready")
        return final_url

    except requests.exceptions.Timeout:
        print("❌ URL Timeout — retrying with GET...")

        try:
            # 🔥 fallback if HEAD fails
            response = requests.get(
                url,
                allow_redirects=True,
                timeout=20
            )
            return response.url
        except Exception as e:
            print("❌ Retry failed:", e)
            return None

    except Exception as e:
        print("❌ URL cleaning error:", e)
        return None