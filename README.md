# Flickr‑Grid‑Downloader

Fetch public Flickr metadata and photos for geo‑referenced grids in a **reproducible**, **modular** way. The pipeline has two stages:

1. **download‑grid** – query Flickr and save photo IDs to a CSV file.
2. **download‑images** – (re)deduplicate results when necessary and download the images **plus** full metadata to disk.

This tool was tested with 1 km² grids, but it can be adapted to any grid size or shape as long as you provide the correct bounding box coordinates in the input CSV files.

---

## Installation

```bash
python -m pip install https://github.com/sbmanolo/flickr-grid-downloader
```

For development:

```bash
git clone https://github.com/sbmanolo/flickr-grid-downloader
cd flickr-grid-downloader
python -m pip install -e .[dev]
```

> Requires **Python ≥ 3.9**.

---

## Environment variables

| Variable     | Purpose                |
| ------------ | ---------------------- |
| `API_KEY`    | Your Flickr app key    |
| `API_SECRET` | Your Flickr app secret |

Every CLI flag can also be provided via an env‑var with the same name.

---

## Preparing the input

Place one CSV per **zone** in the `input/` folder, e.g. `input/<zone_name>_coordinates.csv`.

The CSVs used for the project use-cases had the following format:

```
"id","X.x","Y.x","vertex_index.x","vertex_part.x","X.y","Y.y","vertex_index.y","vertex_part.y"
1,-3.92974,37.44253,3,0,-3.91854,37.45163,1,0
```

But you can use any format as long as you specify the column indices correctly with the `--xx`, `--yx`, `--xy`, and `--yy` flags.

The only requirement is that the first column contains a unique ID for each grid cell, and the next four columns contain the coordinates of the bounding box corners.

---

## Quick start

```bash
# 1) download metadata for a 1‑km grid
fgd download-grid \
    --zone <zone_name> \
    --start-year 2015 --end-year 2024

# 2) download images (automatic dedup)
fgd download-images --zone <zone_name>
```

---

### `download-grid` – key options

| Flag                        | Default                        | Env Var            | Description                           |
| --------------------------- | ------------------------------ | ------------------ | ------------------------------------- |
| `--zone`                    | _(required)_                   | `ZONE`             | prefix used to locate the CSV         |
| `--coordinates-file`        | `input/{zone}_coordinates.csv` | `COORDINATES_FILE` | alternative path to the CSV           |
| `--start-year`              | `2015`                         | `START_YEAR`       | first year (YYYY)                     |
| `--end-year`                | `2024`                         | `END_YEAR`         | last year (YYYY)                      |
| `--xx` `--yx` `--xy` `--yy` | `1 2 5 6`                      | `XX_COLUMN` …      | column indices (0‑based) for the bbox |

---

### `download-images` – key options

| Flag           | Default      | Description                                                     |
| -------------- | ------------ | --------------------------------------------------------------- |
| `--zone`       | _(required)_ | zone to process                                                 |
| `--start-year` | `2015`       | must match the `download-grid` phase                            |
| `--end-year`   | `2024`       | must match the `download-grid` phase                            |
| `--raw`        | False        | Preserve Flickr response JSONs instead of custom project format |

---

## Output layout

```
outputs/
└── <zone_name>/
    ├── csv/
    │   ├── results_2015_2024.csv             # raw IDs
    │   ├── results_2015_2024_cleaned.csv     # deduplicated IDs
    │   └── downloaded_images_2015_2024.csv   # download log
    ├── img/
    │   └── flickr/
    │       └── <box_id>/<zone_name>_<box_id>_<photo_id>.jpg
    └── json/
        └── <zone_name>_NA_<box_id>.json         # dict {photo_id: photo_info}
```

### `photo_info` schema

```jsonc
{
  "9786543210": {
    "id": "9786543210",
    "text": "Title",
    "description": "…",
    "created_at": "2021-08-15 12:34:01+00:00",
    "created_at_timestamp": "1629030841",
    "taken_at": "2021-08-14 16:23:10",
    "views_count": "17",
    "reply_count": "0",
    "box_id": "13",
    "location_id": "NA",
    "original_secret": null,
    "original_format": null,
    "geo": {
      "coordinates": { "type": "Point", "coordinates": [-3.92, 37.34] },
      "accuracy": "16",
      "context": "0",
      "locality": "Seville"
    },
    "author_id": "123@N01",
    "username": "username",
    "tags": ["cat", "andalucia"],
    "attachments": { "media_keys": { "9786543210": "https://…jpg" } },
    "image_url": "https://…jpg",
    "status": "ok",
    "image_downloaded": true,
    "original_downloaded": false
  }
}
```

---

## Important Limitations

### Flickr API Pagination Limit

Although Flickr's official API documentation primarily refers to rate limits (queries per hour), the `flickr.photos.search` endpoint is known to effectively **cap retrievable results to approximately 4,000 items per query** due to pagination constraints. This limitation is independent of the number of API requests and has been widely reported in previous studies and developer documentation.

**Impact**: If a single grid cell contains more than ~4,000 photos, results may be truncated and some images will not be retrieved.

**Solution**: Refine the spatial grid to smaller cell sizes (e.g., 100 × 100 m cells) to ensure no single cell exceeds this threshold. The tool will automatically warn you when a grid cell approaches or reaches this limit:
- ⚠️ **Warning at 3,500+ photos**: Cell is approaching the limit
- ⚠️ **Critical warning at 4,000+ photos**: Results are likely truncated


---

## Examples

```bash
# Custom column indices
fgd download-grid --zone sierra_nevada --xx 2 --yx 3 --xy 4 --yy 5

# Custom CSV path
fgd download-grid --zone sierra_nevada --coordinates-file /Users/username/Desktop/sierra_nevada_coordinates.csv

# One‑liner pipeline
fgd download-grid --zone sierra_nevada && \
fgd download-images --zone sierra_nevada
```

---

## License

Released under the MIT License.\
© 2025 Manuel Merino Ceballos
