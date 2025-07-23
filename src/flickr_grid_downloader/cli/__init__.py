import typer
from flickr_grid_downloader import config

def _require(name: str, value: str | None) -> str:
    """Ensure that a required value is provided."""
    if value is None:
        raise typer.BadParameter(f"{name} is required. Please set it via the environment variable {name} or pass it as an argument.")
    return value

app = typer.Typer(help="Flickr Grid Downloader CLI", add_completion=False)

@app.callback()
def common(
    ctx: typer.Context,
    api_key: str = typer.Option(help="API key for Flickr. Can be set via the FLICKR_API_KEY environment variable or passed as an argument.", envvar=config.API_KEY_ENV),
    api_secret: str = typer.Option(help="API secret for Flickr. Can be set via the FLICKR_API_SECRET environment variable or passed as an argument.", envvar=config.API_SECRET_ENV),
):

    ctx.obj = {
        "api_key": _require(config.API_KEY_ENV, api_key),
        "api_secret": _require(config.API_SECRET_ENV, api_secret),
    }

# Import the CLI commands after defining the app to avoid circular imports
from . import download_grid_cli, download_images_cli