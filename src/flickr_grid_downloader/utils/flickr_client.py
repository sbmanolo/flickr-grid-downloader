import json
from typing import Any
import certifi
import requests

from flickr_grid_downloader.constants import API_METHODS, API_BASE_TEMPLATE


class FlickrClient:
    def __init__(self, *, api_key: str, api_secret: str, timeout: int = 30):
        self.api_key    = api_key
        self.api_secret = api_secret
        self.base = API_BASE_TEMPLATE.format(api_key=api_key)
        self.session = requests.Session()
        self.session.params = {"format": "json"}   # siempre JSON
        self.session.verify = certifi.where()      #  ✅ bundle actualizado
        self.timeout = timeout

    # ---------------- HTTP helpers -----------------
    def _get(self, method: str, **params: Any) -> dict[str, Any]:
        """
        Make a GET request to the Flickr API.
        :param method: The API method to call.
        :param params: Additional parameters for the API request.
        :return: Parsed JSON response from the API.
        """
        url = f"{self.base}{API_METHODS[method]}"
        r = self.session.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        # Flickr API retunrns JSONP like: jsonFlickrApi({...}), so we need to strip the callback function: 
        payload = r.text[14:-1]
        return json.loads(payload)

    # ---------------- high‑level API ---------------
    def search_photos(self, **params):
        """
        Search for photos using the Flickr API.
        :param params: Parameters for the photo search.
        :return: Parsed JSON response containing photo search results.
        """
        return self._get("photo_search", **params)

    def get_info(self, photo_id: str):
        """
        Get detailed information about a specific photo.
        :param photo_id: The ID of the photo to retrieve information for.
        :return: Parsed JSON response containing photo information.
        """
        return self._get("photo_info", photo_id=photo_id)