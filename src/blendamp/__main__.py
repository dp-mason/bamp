import click
from .blendamp import convert


@click.command()
@click.option("--to-winamp/--to-blendamp", default=True)
@click.option("--winamp-dir", default="winamp_skin")
@click.option("--blendamp-dir", default="blendamp")
@click.option("--save-comps", is_flag=True, default=False)
@click.option("--delete-existing", is_flag=True, default=False)
def cli_convert(to_winamp, winamp_dir, blendamp_dir, save_comps, delete_existing):
    convert(to_winamp, winamp_dir, blendamp_dir, save_comps, delete_existing)
    return


if __name__ == "__main__":
    cli_convert()
