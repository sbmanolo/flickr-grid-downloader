from __future__ import annotations
import json
import csv
import time
import requests
from pathlib import Path
from typing import Sequence
from requests import Response

from flickr_grid_downloader.config import JobConfig
from flickr_grid_downloader.utils.flickr_client import FlickrClient
from flickr_grid_downloader.console import get_logger
from flickr_grid_downloader.tools.duplicate_cleaner import DuplicateCleaner
from flickr_grid_downloader.utils.photo_info import build_photo_info

log = get_logger(__name__)

class ImageDownloader:
    SLEEP = 0.3  # Seconds between requests to avoid rate limiting

    def __init__(self, cfg: JobConfig, api: FlickrClient) -> None:
        self.cfg = cfg
        self.api = api

        self.results_csv        = cfg.csv_path / f"results_{cfg.start_year}_{cfg.end_year}.csv"
        self.results_cleaned    = cfg.csv_path / f"results_{cfg.start_year}_{cfg.end_year}_cleaned.csv"
        self.downloaded_images_csv       = cfg.csv_path / f"downloaded_images_{cfg.start_year}_{cfg.end_year}.csv"
        self.json_dir           = cfg.json_path

        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.downloaded_images_csv.touch(exist_ok=True)

    # ---------- Helper ----------
    def _append_row(self, path: Path, row: Sequence[str]) -> None:
        with path.open("a", newline="") as f:
            csv.writer(f).writerow(row)

    # ---------- Image ----------
    def _image_url(self, server: str, photo_id: str, secret: str,
                   original_secret: str | None, fmt: str) -> tuple[str, bool]:
        """
        Returns (url, original_downloaded)
        • Priority to _b size (medium/large) because the original is usually large.
        """
        # DISABLED. In case we want to download the original image (much larger) we must implement this logic.
        # if original_secret:    
        #     return (f"https://live.staticflickr.com/{server}/{photo_id}_{original_secret}_o.{fmt}", True)
        return (f"https://live.staticflickr.com/{server}/{photo_id}_{secret}_b.{fmt}", False)

    def _download_to(self, url: str, dest: Path) -> bool:
        try:
            r: Response = requests.get(url, timeout=60, stream=True)
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as exc:
            log.error("Image %s not downloaded → %s", url, exc)
            return False

    # ---------- Main loop ----------
    def _process_photo(self, photo_row: Sequence[str]) -> None:
        box_id, page, photo_id, owner, secret, title = photo_row

        # Call the API to get full metadata
        info = self.api.get_info(photo_id)
        photo = info["photo"]

        server = photo["server"]
        secret = photo["secret"]
        original_secret = photo.get("originalsecret")
        fmt = photo.get("originalformat", "jpg")

        url, original_flag = self._image_url(server, photo_id, secret, original_secret, fmt)
        img_dir = self.cfg.img_path / box_id
        img_dir.mkdir(parents=True, exist_ok=True)
        img_path = img_dir / f"{self.cfg.zone}_{box_id}_{photo_id}.jpg"

        ok = self._download_to(url, img_path)

        # --- JSON cache ----------
        json_path = self.json_dir / f"{self.cfg.zone}_{box_id}.json"
        data: dict[str, dict] = {}
        if json_path.exists():
            data = json.loads(json_path.read_text())

        # Construye la info del photo_info
        if self.cfg.download_raw_metadata:
            data[photo_id] = {
                "title": title,
                "url": url,
                "downloaded": ok,
                "original": original_flag,
                "meta": info,
            }
        else:
            data[photo_id] = build_photo_info(
                photo_id=photo_id,
                box_id=box_id,
                api_payload=info,
                image_url=url,
                downloaded=ok,
                original_downloaded=original_flag
            )

        data[photo_id]["metadata_format"] = "raw" if self.cfg.download_raw_metadata else "custom"

        json_path.write_text(json.dumps(data, indent=2))

        self._append_row(self.downloaded_images_csv, [photo_id, box_id, "ok" if ok else "error", str(ok)])


    # ---------- CLI entry ----------
    def run(self) -> None:
        # 1) Deduplicate CSV (If cleaned does not exist or if results_csv is newer)
        if not self.results_cleaned.exists() or \
           self.results_csv.stat().st_mtime > self.results_cleaned.stat().st_mtime:
            DuplicateCleaner(self.results_csv, self.results_cleaned).clean()

        done: set[str] = set()
        with self.downloaded_images_csv.open() as f:
            done = {row[0] for row in csv.reader(f)}

        log.info("Downloading images for %s.", self.cfg.zone)
        if done:
            log.info("Skipping %d already downloaded photos\n",  len(done))

        with self.results_cleaned.open() as f:
            reader = csv.reader(f)
            header = next(reader)

            total = sum(1 for _ in reader)
            f.seek(0); next(reader)         # vuelve al inicio tras contar

            for idx, row in enumerate(reader, start=1):
                photo_id = row[2]
                if photo_id in done:
                    continue

                log.info("%s %d/%d (box %s) - photo_id=%s", self.cfg.zone, idx, total, row[0], photo_id)

                self._process_photo(row)
                time.sleep(self.SLEEP)

        log.info("✅ Finished downloading images for %s ✅", self.cfg.zone)