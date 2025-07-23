from __future__ import annotations
import datetime
from typing import Any, Dict

def build_photo_info(
    photo_id: str,
    box_id: str,
    api_payload: Dict[str, Any],
    image_url: str,
    downloaded: bool,
    original_downloaded: bool,
) -> Dict[str, Any]:
    """Return a dict identical to the legacy `photo_info` structure."""
    p: Dict = api_payload["photo"]

    # graceful fall‑backs
    original_secret = p.get("originalsecret")
    original_format = p.get("originalformat", "jpg")

    # geography may be missing on some shots
    location = p.get("location", {})

    return {
        "id": photo_id,
        "text": p["title"]["_content"],
        "description": p["description"]["_content"],
        "created_at": datetime.datetime.fromtimestamp(
            int(p["dates"]["posted"])
        ).strftime("%Y-%m-%d %H:%M:%S+00:00"),
        "created_at_timestamp": p["dates"]["posted"],
        "taken_at": p["dates"]["taken"],
        "views_count": p["views"],
        "reply_count": p["comments"]["_content"],
        "box_id": box_id,
        "location_id": "NA",
        "original_secret": original_secret,
        "original_format": original_format if original_secret else None,
        "geo": {
            "coordinates": {
                "type": "Point",
                "coordinates": [location.get("longitude"), location.get("latitude")],
            },
            "accuracy": location.get("accuracy"),
            "context": location.get("context"),
            "locality": location.get("locality"),
            "county": location.get("county"),
            "region": location.get("region"),
            "country": location.get("country"),
            "neighbourhood": location.get("neighbourhood"),
        },
        "author_id": p["owner"]["nsid"],
        "username": p["owner"]["username"],
        "tags": [t["_content"] for t in p["tags"]["tag"]],
        "attachments": {"media_keys": {photo_id: image_url}},
        "image_url": image_url,
        "status": "ok",
        "image_downloaded": downloaded,
        "original_downloaded": original_downloaded,
    }
