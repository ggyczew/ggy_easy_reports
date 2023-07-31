import click
from easy_reports import EasyReport
from pathlib import Path


@click.group()
def cli():
    pass


@cli.command("create")
@click.option(
    "--symbol",
    type=click.STRING,
    prompt="Enter new report symbol",
    help="New report symbol. Will be used to create folder for it's definition",
)
def create(symbol):
    """Create new report boilerplate"""
    click.echo(f"Creating report {symbol}...")

    app = EasyReport()

    if Path('settings.py').exists():
        app.base_config.from_pyfile('settings.py')
    app.create_boilerplate(symbol)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
