from __future__ import annotations
import csv, time
from pathlib import Path
from typing import Sequence

from flickr_grid_downloader.config import JobConfig
from flickr_grid_downloader.utils.flickr_client import FlickrClient
from flickr_grid_downloader.console import get_logger

log = get_logger(__name__)


class ZoneDownloader:
    SLEEP = 0.7          # seg entre peticiones; evita rate-limit

    def __init__(self, cfg: JobConfig, api: FlickrClient) -> None:
        """
        Initializes the ZoneDownloader with a configuration and an API client.
        :param cfg: JobConfig containing zone and API credentials.
        :param api: FlickrClient instance for making API requests.
        """

        self.cfg = cfg
        self.api = api

        # paths derived from the configuration.
        self.bbox_csv  = cfg.coordinates_file
        self.done_csv  = cfg.csv_path / f"checked_grids_{cfg.start_year}_{cfg.end_year}.csv"
        self.results   = cfg.csv_path / f"results_{cfg.start_year}_{cfg.end_year}.csv"

        self.xx = cfg.xx_column
        self.yx = cfg.yx_column
        self.xy = cfg.xy_column
        self.yy = cfg.yy_column

        # Create directories if they don't exist
        self.results.parent.mkdir(parents=True, exist_ok=True)

    def _load_done(self) -> set[str]:
        """Load the done CSV file and return a set of processed box IDs."""
        if not self.done_csv.exists():
            return set()
        with self.done_csv.open() as f:
            return {row[0] for row in csv.reader(f)}

    def _append_row(self, path: Path, row: Sequence[str]) -> None:
        """Append a row to the CSV file, creating it if it doesn't exist."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", newline="") as f:
            csv.writer(f).writerow(row)

    def _date_range_params(self) -> dict[str, str]:
        """Returns the date range parameters for the API request."""
        return {
            "min_taken_date": f"{self.cfg.start_year}-01-01 00:00:00",
            "max_taken_date": f"{self.cfg.end_year}-12-31 23:59:59",
            "sort": "date-posted-asc",
        }

    def check_zone(self, box_id: str, bbox: str) -> None:
        """Downloads photos for a given bounding box."""
        page, pages, total = 1, 1, 0
        had_errors = False

        while page <= pages:
            params = {
                **self._date_range_params(),
                "bbox": bbox,
                "page": page,
            }
            try:
                data = self.api.search_photos(**params)

                if not data:
                    log.warning("No photos found in grid %s page %s", box_id, page)
                if data['stat'] != 'ok':
                    raise ValueError(f"Flickr API error: {data.get('message', 'Unknown error')}")

                meta  = data["photos"]
                pages = meta["pages"]
                photos = meta["photo"]

                for p in photos:
                    self._append_row(
                        self.results,
                        [box_id, str(page), p["id"], p["owner"], p["secret"], p["title"]],
                    )
                total += len(photos)
                page += 1
            except Exception as exc:
                had_errors = True
                log.error("Error in grid %s page %s → %s", box_id, page, exc)
                break # change this line for break the loop on error in case you want to raise an exception

        # Register the completion of the box
        self._append_row(self.done_csv, [box_id, str(total), str(had_errors)])

    # ---------- CLI entry ----------
    def run(self) -> None:
        """Main method to run the zone downloader."""
        done = self._load_done()

        with self.bbox_csv.open() as f:
            reader = csv.reader(f, delimiter=self.cfg.delimiter)
            header = next(reader)          # ignore header row

            for idx, row in enumerate(reader, start=1):
                box_id = row[0]
                if box_id in done:
                    log.debug("Grid %s already done. Skipping.", box_id)
                    continue

                bbox = f"{row[self.xx]},{row[self.yx]},{row[self.xy]},{row[self.yy]}"
                log.info(f"({idx}) Checking grid {box_id}")
                self.check_zone(box_id, bbox)
                time.sleep(self.SLEEP)

        log.info("Zone %s: All done! ✅", self.cfg.zone)
