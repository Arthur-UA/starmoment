from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

APOD_ROOT = "https://apod.nasa.gov/apod/"


def get_photo_metadata(content: bytes) -> tuple[str | None, str]:
    """Extract the primary image and explanation from an APOD page.
    Args:
        content: The HTML content of the APOD page.
    Returns:
        A tuple containing the image URL (or None if not found) and the explanation text.
    """

    soup = BeautifulSoup(content, "lxml")
    image = soup.find("img")
    label = soup.find("b", string=lambda value: value and "Explanation:" in value)
    if label is None:
        return None, ""

    text = []
    for element in label.next_siblings:
        if getattr(element, "name", None) == "center":
            break
        value = (element.get_text(" ", strip=True)
                 if hasattr(element, "get_text") else str(element).strip())
        if value:
            text.append(value)

    image_url = (urljoin(APOD_ROOT, image.get("src"))
                 if image and image.get("src") else None)
    return image_url, " ".join(text)


def get_photo(moment_date: date) -> tuple[str, str, str]:
    """Fetch the Astronomy Picture of the Day for a given date.
    Args:
        moment_date: The date for which to fetch the APOD.
    Returns:
        A tuple containing the page URL, image URL, and explanation text.
    """

    page_url = f"{APOD_ROOT}ap{moment_date:%y%m%d}.html"
    response = requests.get(page_url, timeout=15)
    response.raise_for_status()
    image_url, explanation = get_photo_metadata(response.content)
    if not image_url:
        raise ValueError("NASA does not have a still image for this date. Try another day.")
    return page_url, image_url, explanation
