from __future__ import annotations
import typer

from flickr_grid_downloader.config import JobConfig
from flickr_grid_downloader.console import console
from flickr_grid_downloader.cli import app
from flickr_grid_downloader.tools.image_downloader import ImageDownloader
from flickr_grid_downloader.utils.flickr_client import FlickrClient


@app.command("download-images")
def download_images(
    ctx: typer.Context,
    zone: str = typer.Option(..., prompt=True, envvar="ZONE", help="Zone to download the images from."),
    start_year: int = typer.Option(2015, envvar="START_YEAR"),
    end_year:   int = typer.Option(2024, envvar="END_YEAR"),
    raw: bool = typer.Option(False, envvar="DOWNLOAD_RAW", help="Download raw Flickr JSON data instead of using the custom format.")
):
    
    api_key = ctx.obj["api_key"]
    api_secret = ctx.obj["api_secret"]

    cfg = JobConfig(
        zone=zone,
        start_year=start_year,
        end_year=end_year,
        api_key=api_key,
        api_secret=api_secret,
        download_raw_metadata=raw,
    )

    console.print("\n[bold magenta]Starting Flickr img downloader CLI[/]\n")

    console.print("[bold cyan]Using the following configuration:[/]")
    console.print(f"📍 [bold blue]Zone:           [/] {zone}")
    console.print(f"🗓️  [bold blue]Start Year:     [/] {start_year}")
    console.print(f"🗓️  [bold blue]End Year:       [/] {end_year}")
    console.print(f"🔧 [bold blue]Output format:  [/] {'Raw' if raw else 'Custom'}\n")

    api  = FlickrClient(api_key=api_key, api_secret=api_secret)
    ImageDownloader(cfg, api).run()

if __name__ == "__main__":
    app()