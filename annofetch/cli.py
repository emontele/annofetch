# annofetch/cli.py

import typer
from typing_extensions import Annotated
from annofetch.downloader import EnsemblDownloader

app = typer.Typer(
    name="annofetch",
    help="A CLI for downloading genome and annotation files from Ensembl.",
    add_completion=False,
    rich_markup_mode="rich"
)

def get_downloader(species: str, release: int, build: str, output_dir: str):
    """
    Helper function to initialize the EnsemblDownloader and handle potential errors.
    This avoids code duplication between commands.
    """
    try:
        return EnsemblDownloader(species=species, release=release, build=build, output_dir=output_dir)
    except ValueError as e:
        print(f"❌ Error: Missing required parameter. {e}")
        raise typer.Exit(code=1)

@app.command()
def genome(
    species: Annotated[str, typer.Option(help="Ensembl species name (e.g., 'homo_sapiens')")],
    release: Annotated[int, typer.Option(help="Ensembl release number (e.g., 112)")],
    build: Annotated[str, typer.Option(help="Genome build (e.g., 'GRCh38')")],
    suffix: Annotated[str, typer.Option(help="File suffix for the FASTA file.")] = "primary_assembly",
    output_dir: Annotated[str, typer.Option(help="Directory to save the file.")] = "resources/ref",
    add_ucsc_style: Annotated[bool, typer.Option(
        "--add-ucsc-style", 
        help="Convert chromosome names to UCSC style (e.g., '1' -> 'chr1'). Requires a mapping file for the build."
    )] = False,
):
    """
    Downloads a genome FASTA file from Ensembl.
    """
    downloader = get_downloader(species, release, build, output_dir)
    
    # --- Robustness Check for Build-Aware Mapping (for genome command) ---
    if add_ucsc_style and not downloader.chr_map:
        print(f"⚠️  [bold yellow]Warning:[/bold yellow] Cannot perform UCSC style conversion for genome. No mapping file found for build '[bold cyan]{build}[/bold cyan]'.")
        print("   Proceeding with download without chromosome name conversion.")
        add_ucsc_style = False # Disable the impossible request

    downloader.download_genome(suffix=suffix, add_ucsc_style=add_ucsc_style)

@app.command()
def gtf(
    species: Annotated[str, typer.Option(help="Ensembl species name (e.g., 'homo_sapiens')")],
    release: Annotated[int, typer.Option(help="Ensembl release number (e.g., 112)")],
    build: Annotated[str, typer.Option(help="Genome build (e.g., 'GRCh38')")],
    output_dir: Annotated[str, typer.Option(help="Directory to save the file.")] = "resources/ref",
    add_ucsc_style: Annotated[bool, typer.Option(
        "--add-ucsc-style", 
        help="Convert chromosome names to UCSC style (e.g., '1' -> 'chr1'). Requires a mapping file for the build."
    )] = False,
):
    """
    Downloads a GTF annotation file with optional chromosome style conversion.
    
    """


    downloader = get_downloader(species, release, build, output_dir)
    
    # --- Robustness Check for Build-Aware Mapping (for gtf command) ---
    if add_ucsc_style and not downloader.chr_map:
        print(f"⚠️  [bold yellow]Warning:[/bold yellow] Cannot perform UCSC style conversion. No mapping file found for build '[bold cyan]{build}[/bold cyan]'.")
        print("   Proceeding with download without chromosome name conversion.")
        add_ucsc_style = False

    downloader.download_gtf(
        add_ucsc_style=add_ucsc_style
    )

if __name__ == "__main__":
    app()

