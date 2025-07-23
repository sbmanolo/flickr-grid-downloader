from dotenv import load_dotenv
from dataclasses import dataclass, field
from pathlib import Path

load_dotenv()  # Reads the .env file and sets environment variables

API_KEY_ENV    = "FLICKR_API_KEY"
API_SECRET_ENV = "FLICKR_API_SECRET"

from flickr_grid_downloader.constants import (
    OUTPUT_DIR, INPUT_DIR,
    API_BASE_TEMPLATE, API_METHODS,
    C_YY, C_XY, C_YX, C_XX
)

@dataclass(slots=True)
class JobConfig:
    """Info based on the user input"""
    zone: str
    start_year: int
    end_year:   int
    api_key:    str
    api_secret: str
    
    # Se rellenan en __post_init__
    zone_base: Path = field(init=False)
    json_path: Path = field(init=False)
    csv_path:  Path = field(init=False)
    img_path:  Path = field(init=False)
    coordinates_path: Path = field(init=False)
    coordinates_file: Path = field(init=False)
    delimiter: str = field(default=",", repr=False)
    xx_column: int = field(default=C_XX)
    yx_column: int = field(default=C_YX)
    xy_column: int = field(default=C_XY)
    yy_column: int = field(default=C_YY)
    
    # Flag to indicate if download JSON data in custom or raw format.
    download_raw_metadata: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        if self.start_year >= self.end_year:
            raise ValueError("start_year must be earlier than end_year")

        self.zone_base        = OUTPUT_DIR / self.zone
        self.json_path        = self.zone_base / "json"
        self.csv_path         = self.zone_base / "csv"
        self.img_path         = self.zone_base / "img"
        self.coordinates_path = INPUT_DIR
        self.coordinates_file = self.coordinates_path / f"{self.zone}_coordinates.csv"
        
        # Create directories if they don't exist
        for path in [
            self.zone_base, self.json_path, self.csv_path,
            self.img_path, self.coordinates_path
        ]:
            path.mkdir(parents=True, exist_ok=True)

    # reusable helpers --------------------------
    @property
    def api_base(self) -> str:
        return API_BASE_TEMPLATE.format(api_key=self.api_key)

    def api_method(self, name: str) -> str:
        return API_METHODS[name]