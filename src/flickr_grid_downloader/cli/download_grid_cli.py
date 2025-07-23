from __future__ import annotations
import typer
from pathlib import Path

from flickr_grid_downloader.config import JobConfig
from flickr_grid_downloader.console import console
from flickr_grid_downloader.cli import app
from flickr_grid_downloader.tools.grid_downloader import ZoneDownloader
from flickr_grid_downloader.utils.flickr_client import FlickrClient
from flickr_grid_downloader.constants import INPUT_DIR, C_XX, C_YX, C_XY, C_YY

ZONE_HELP_TEXT = """
Zone to download the grid from.
A file called '{zone}_coordinates.csv' must exist in the 'input' directory. 
\n\n
The default expected columns must be the following:
"id","X.x","Y.x","vertex_index.x","vertex_part.x","X.y","Y.y","vertex_index.y","vertex_part.y"
1,-3.92974262579894,37.4425324910326,3,0,-3.91854945597732,37.451633458244,1,0
\n\n
If the coordinates order is different, you can specify the column indices using the options --xx, --yx, --xy, and --yy.
"""

@app.command("download-grid")
def download_grid_cmd(
    ctx: typer.Context,
    zone: str = typer.Option(..., prompt=True, envvar="ZONE", help=ZONE_HELP_TEXT),
    coordinates_file: Path | None = typer.Option(None, envvar="COORDINATES_FILE", help="CSV file with coordinates for the grid. If not provided, defaults to 'input/{zone}_coordinates.csv'"),
    delimiter: str = typer.Option(",", envvar="DELIMITER", help="Delimiter for the coordinates CSV file. Default is ','"),
    start_year: int = typer.Option(2015, envvar="START_YEAR"),
    end_year:   int = typer.Option(2024, envvar="END_YEAR"),
    xx: int = typer.Option(C_XX, envvar="XX_COLUMN", help="Index for X.x coordinate column (0-based)"),
    yx: int = typer.Option(C_YX, envvar="YX_COLUMN", help="Index for Y.x coordinate column (0-based)"),
    xy: int = typer.Option(C_XY, envvar="XY_COLUMN", help="Index for X.y coordinate column (0-based)"),   
    yy: int = typer.Option(C_YY, envvar="YY_COLUMN", help="Index for Y.y coordinate column (0-based)"),
):
    
    api_key = ctx.obj["api_key"]
    api_secret = ctx.obj["api_secret"]

    cfg = JobConfig(
        zone=zone,
        start_year=start_year,
        end_year=end_year,
        api_key=api_key,
        api_secret=api_secret,
        xx_column=xx,
        yx_column=yx,
        xy_column=xy,
        yy_column=yy,
        delimiter=delimiter,
    )

    if not coordinates_file:
        coordinates_file = Path(INPUT_DIR) / f"{zone}_coordinates.csv"
    if not coordinates_file.exists():
        raise typer.BadParameter(f"Coordinates file '{coordinates_file}' does not exist. Please provide a valid path or ensure the file exists in the input directory.")

    console.print("\n[bold magenta]Starting Flickr grid downloader CLI[/]\n")

    console.print("[bold cyan]Using the following configuration:[/]")
    console.print(f"📍 [bold blue]Zone:            [/] {zone}")
    console.print(f"📁 [bold blue]Coordinates file:[/] {coordinates_file.name}")
    console.print(f"🗓️  [bold blue]Start Year:      [/] {start_year}")
    console.print(f"🗓️  [bold blue]End Year:        [/] {end_year}")
    console.print(f"📊 [bold blue]Columns:         [/] XX={xx}, YX={yx}, XY={xy}, YY={yy}\n")

    api  = FlickrClient(api_key=api_key, api_secret=api_secret)
    ZoneDownloader(cfg, api).run()

if __name__ == "__main__":
    app()