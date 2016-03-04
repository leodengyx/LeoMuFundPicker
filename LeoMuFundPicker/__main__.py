#!/usr/bin/python

import click
from downloader import Downloader
from xlsexporter import XlsExporter

@click.command()
@click.option("--download", type=click.Choice(['all']))
def cli_entry(download):
    downloader = Downloader()
    downloader.save_all_mutual_fund_info()

    exporter = XlsExporter()
    for mutual_fund_inst in downloader.mutual_fund_inst_list:
        exporter.write_mutual_fund_to_file(mutual_fund_inst)
    exporter.save_file()


if __name__ == "__main__":
    cli_entry()
