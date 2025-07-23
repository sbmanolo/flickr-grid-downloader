from __future__ import annotations
import csv
from pathlib import Path
from typing import Iterable, Sequence

from flickr_grid_downloader.console import get_logger

log = get_logger(__name__)

class DuplicateCleaner:
    """
    Deduplicates the results CSV:
    • Keeps the first occurrence of each photo_id.
    • Creates a *_cleaned.csv* file without repetitions.
    """
    def __init__(self, in_path: Path, out_path: Path) -> None:
        """
        Initializes the DuplicateCleaner with input and output file paths.
        :param in_path: Path to the input CSV file containing results.
        :param out_path: Path where the cleaned CSV file will be saved.
        """
        if not in_path.exists():
            raise FileNotFoundError(f"Input file '{in_path}' does not exist.")
        self.in_path  = in_path
        self.out_path = out_path

    def _write_rows(self, rows: Iterable[Sequence[str]]) -> None:
        """
        Writes the given rows to the output CSV file.
        If the file already exists, it will be overwritten.
        """
        with self.out_path.open("w", newline="") as f:
            csv.writer(f).writerows(rows)

    def clean(self) -> Path:
        """
        Reads the input CSV, removes duplicate photo_ids, and writes the cleaned data to the output CSV.
        Returns the path to the cleaned CSV file.
        """
        seen: set[str] = set()
        deduped: list[Sequence[str]] = []

        with self.in_path.open() as f:
            reader = csv.reader(f)

            # Data does not have a header, so we start reading directly
            for row in reader:
                photo_id = row[2]             # 'id' column is at index 2
                if photo_id in seen:
                    continue
                seen.add(photo_id)
                deduped.append(row)

        self._write_rows(deduped)
        log.info("Cleaned: %s → %s (‑%d rows)",
                 self.in_path.name, self.out_path.name,
                 len(list(csv.reader(self.in_path.open()))) - len(deduped))
        return self.out_path