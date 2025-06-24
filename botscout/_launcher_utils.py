def _prepare_url(url: str) -> str:
    """
    Ensures the URL starts with 'http://' or 'https://'
    and ends with a trailing slash '/'.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if not url.endswith("/"):
        url += "/"

    return url
