from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_BASE="https://www.flickr.com/services/rest/?method="

API_METHODS = {
    "photo_search": "flickr.photos.search",
    "photo_info":  "flickr.photos.getInfo",
}

API_BASE_TEMPLATE = (
    "https://www.flickr.com/services/rest/?format=json"
    "&api_key={api_key}&method="
)

C_XX, C_YX, C_XY, C_YY = 1, 2, 5, 6

# Flickr API pagination limit
# The flickr.photos.search endpoint caps retrievable results to ~4,000 items per query
# due to pagination constraints (independent of rate limits). This is a known limitation
# documented in various studies. To avoid truncation, refine spatial grids to ensure
# no single cell exceeds this threshold.
FLICKR_PAGINATION_LIMIT = 4000
FLICKR_WARNING_THRESHOLD = 3500  # Warn when approaching the limit