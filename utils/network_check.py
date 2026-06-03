"""Lightweight network connectivity checker."""


def is_online() -> bool:
    """Check if the system has internet connectivity.

    Uses a lightweight HEAD request to Google's generate_204 endpoint.
    Falls back to checking if we can resolve DNS.

    Returns:
        True if online, False otherwise.
    """
    try:
        import requests
        # Try the lightweight 204 endpoint (returns no body, just status)
        resp = requests.head(
            "https://www.google.com/generate_204",
            timeout=3,
            allow_redirects=True,
        )
        return resp.status_code in (200, 204)
    except Exception:
        pass

    # Fallback: try a DNS resolve
    try:
        import socket
        socket.setdefaulttimeout(3)
        socket.getaddrinfo("www.google.com", 443)
        return True
    except Exception:
        return False
