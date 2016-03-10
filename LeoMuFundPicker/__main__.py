#!/usr/bin/python

import click
from downloader import Downloader
from xlsexporter import XlsExporter

@click.command()
@click.option("--download", type=click.Choice(['all']))
def cli_entry(download):

    downloader = Downloader()
    exporter = XlsExporter()
    downloader.save_all_mutual_fund_info(exporter)

    exporter.save_file()


if __name__ == "__main__":
    cli_entry()
