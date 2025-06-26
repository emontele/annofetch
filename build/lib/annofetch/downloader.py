# annofetch/downloader.py

import gzip
import requests
from pathlib import Path
from tqdm import tqdm
import importlib.resources

# _load_chromosome_map function remains the same as before
def _load_chromosome_map(filename: str) -> dict:
    """Loads a two-column chromosome mapping file from the package's data directory."""
    mapping = {}
    try:
        file_path = importlib.resources.files('annofetch').joinpath('data').joinpath(filename)
        with file_path.open('r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                try:
                    source_name, target_name = line.strip().split('\t')
                    mapping[source_name] = target_name
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return mapping


class EnsemblDownloader:
    """Handles downloading and processing of genome and annotation files from Ensembl FTP."""
    BASE_URL = "https://ftp.ensembl.org/pub"

    def __init__(self, species: str, release: int, build: str, output_dir: str = "."):
        # ... (init code remains the same as before)
        if not all([species, release, build]):
            raise ValueError("Species, release, and build must be provided.")
        
        self.species = species.lower()
        self.release = release
        self.build = build
        self.output_path = Path(output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        print(f"🧬 Initialized downloader for {self.species} (release {self.release}, build {self.build})")

        map_filename = f"{self.build}_ensembl2UCSC.txt"
        self.chr_map = _load_chromosome_map(map_filename)

        if not self.chr_map:
            print(f"ℹ️  Note: No mapping file found for build '{self.build}'. Chromosome style conversion will be unavailable.")

    # _get_gtf_processor function remains the same as before
    def _get_gtf_processor(self, add_ucsc_style: bool):
        """Returns a line-processing function for GTF files based on user's choice."""
        if add_ucsc_style and self.chr_map:
            print(f"   (Note: Using '{self.build}' map to convert GTF chromosome names to UCSC style)")
            def processor(line: str) -> str:
                if line.startswith('#'):
                    return line
                fields = line.split('\t')
                if len(fields) > 0:
                    fields[0] = self.chr_map.get(fields[0], fields[0])
                return '\t'.join(fields)
            return processor
                  
        return None

    def _get_fasta_processor(self, add_ucsc_style: bool):
        """Returns a line-processing function for FASTA files based on user's choice."""
        if add_ucsc_style and self.chr_map:
            print(f"   (Note: Using '{self.build}' map to convert FASTA chromosome names to UCSC style)")
            def processor(line: str) -> str:
                if line.startswith('>'):
                    # Extract current chromosome name from FASTA header (e.g., '>1 dna:chromosome ...')
                    # It's the part between '>' and the first space.
                    header_parts = line[1:].split(' ', 1) # Split only on the first space
                    current_chr_name = header_parts[0]
                    
                    # Apply mapping
                    new_chr_name = self.chr_map.get(current_chr_name, current_chr_name)
                    
                    # Reconstruct the header line
                    if len(header_parts) > 1:
                        return f">{new_chr_name} {header_parts[1]}"
                    else:
                        return f">{new_chr_name}\n" # Ensure newline for single-part headers
                return line # Return sequence lines unchanged
            return processor
        return None

    # _download_and_process_stream function remains the same as before
    def _download_and_process_stream(self, url: str, output_file: Path, line_processor=None):
        """Generic downloader with on-the-fly decompression and line-by-line processing."""
        print(f"⬇️ Downloading from: {url}")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_file.name) as progress_bar:
                    with gzip.GzipFile(fileobj=r.raw) as gz_file, open(output_file, 'w', encoding='utf-8') as f_out:
                        for line in (l.decode('utf-8') for l in gz_file):
                            if line_processor:
                                line = line_processor(line)
                            f_out.write(line)
                            progress_bar.update(r.raw.tell() - progress_bar.n)

            print(f"✅ Successfully downloaded and saved to {output_file.resolve()}")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: Could not find the file at the specified URL.")
            print(f"   Please check your parameters (species, release, build).")
            print(f"   Status code: {e.response.status_code}, URL: {url}")
            return False
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            return False

    def download_genome(self, suffix: str = "primary_assembly", add_ucsc_style: bool = False):
        """Downloads a genome FASTA file with optional chromosome style conversion."""
        spec_up = self.species.capitalize()
        url = (
            f"{self.BASE_URL}/release-{self.release}/fasta/{self.species}/dna/"
            f"{spec_up}.{self.build}.dna.{suffix}.fa.gz"
        )
        output_file = self.output_path / f"{self.species}_{self.build}_{self.release}.fa"
        
        processor = self._get_fasta_processor(add_ucsc_style=add_ucsc_style)
        
        return self._download_and_process_stream(url, output_file, line_processor=processor)

    # download_gtf function remains the same as before
    def download_gtf(self, add_ucsc_style: bool = False):
        """Downloads a GTF annotation file with optional chromosome style conversion."""
        spec_up = self.species.capitalize()
        url = (
            f"{self.BASE_URL}/release-{self.release}/gtf/{self.species}/"
            f"{spec_up}.{self.build}.{self.release}.gtf.gz"
        )
        output_file = self.output_path / f"{self.species}_{self.build}_{self.release}.gtf"
        
        processor = self._get_gtf_processor(
            add_ucsc_style=add_ucsc_style
        )
        
        return self._download_and_process_stream(url, output_file, line_processor=processor)

