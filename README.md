`annofetch` is a powerful command-line tool and Python package for effortlessly downloading genome FASTA files and gene annotation GTF files directly from Ensembl's FTP servers. It supports on-the-fly decompression and crucial post-processing steps like chromosome name style conversion (e.g., Ensembl's `1` to UCSC's `chr1`) based on the specified genome build.

`annofetch` provides a convenient and reproducible way to obtain reference genomic data for your bioinformatics pipelines.

## ✨ Features

* **Download Genomes:** Fetch FASTA files for various species and builds from Ensembl.
* **Download Annotations:** Fetch GTF files for various species and builds from Ensembl.
* **On-the-Fly Decompression:** Automatically handles `.gz` compressed files.
* **Chromosome Name Conversion:**
    * Optionally map `ensemble style chr` to convert to UCSC style (e.g., `1` to `chr1`).
    * **Build-Aware Mapping:** Automatically selects the correct chromosome mapping file (e.g., GRCh38, GRCm39).
* **Clean Command-Line Interface:** Easy-to-use commands powered by `Typer`.
* **Pythonic API:** Can be integrated into larger Python scripts and workflows.
* **Robustness:** Handles network errors, missing files, and provides clear user feedback.


## 🚀 Installation

`annofetch` is designed to be installed as a command-line application. The recommended way to install it is using `pipx`, which installs Python applications into isolated environments to avoid conflicts with system packages.

### Prerequisites

* Python 3.8+
* `pipx` (recommended)


### Using `pipx` (Recommended)

If you don't have `pipx` installed, you can install it via `pip`:

```bash
pip install pipx
pipx ensurepath # Make sure pipx installed apps are in your PATH
```

Then, install `annofetch` from PyPI:

```bash
pipx install annofetch
```

### From Source (for Development)

If you want to contribute or develop `annofetch`, clone the repository and install it in editable mode:

```bash
git clone https://github.com/emontele/annofetch.git
cd annofetch
pip install -e . # Install in editable mode
```

This will make the `annofetch` command available in your terminal.

## 💡 Usage

The `annofetch` command provides two main subcommands: `genome` for FASTA files and `gtf` for GTF files.

### Common Options

* `--species`: Ensembl species name (e.g., `homo_sapiens`, `mus_musculus`).
* `--release`: Ensembl release number (e.g., `100`, `112`).
* `--build`: Genome build name (e.g., `GRCh38`, `GRCm39`).
* `--output-dir`: Directory to save the downloaded file (default: `resources/ref`).


### 🧬 Downloading Genome FASTA Files

Use the `annofetch genome` command.

```bash
annofetch genome --help
```

**Example: Download Human GRCh38 Genome**

```bash
annofetch genome \
  --species homo_sapiens \
  --release 112 \
  --build GRCh38 \
  --output-dir my_genomes/human
```

*(This will save `my_genomes/human/homo_sapiens_GRCh38_112.fa`)*

**Example: Download Mouse GRCm39 Genome with UCSC-style Chromosome Names**

```bash
annofetch genome \
  --species mus_musculus \
  --release 112 \
  --build GRCm39 \
  --add-ucsc-style
```

*(This will convert chromosome names like `1` to `chr1` in `resources/ref/mus_musculus_GRCm39_112.fa`)*

### 📝 Downloading GTF Annotation Files

Use the `annofetch gtf` command.

```bash
annofetch gtf --help
```

**Example: Download Human GRCh38 GTF**

```bash
annofetch gtf \
  --species homo_sapiens \
  --release 112 \
  --build GRCh38
```
*(This will save `resources/ref/homo_sapiens_GRCh38_112.gtf`)*

**Example: Download Human GRCh38 GTF with UCSC-style Chromosome Names**

```bash
annofetch gtf \
  --species homo_sapiens \
  --release 112 \
  --build GRCh38 \
  --add-ucsc-style
```

*(This will convert chromosome names like `1` to `chr1` in `resources/ref/homo_sapiens_GRCh38_112.gtf`)*



## 🗺️ Chromosome Mapping Files

`annofetch` includes a collection of `Ensembl` to `UCSC` chromosome mapping files within its `data/` directory. These files are used for the `--add-ucsc-style` option and are automatically selected based on the `--build` parameter you provide.

The package currently supports mappings for common builds such as:

* `GRCh37` (Human)
* `GRCh38` (Human)
* `GRCm38` (Mouse)
* `GRCm39` (Mouse)
* *(You can extend this by adding more `mapping` files to the `annofecth/data/` directory)*
* *(All `mapping files` where unshamelessy downloaded from `https://github.com/dpryan79/ChromosomeMappings`)

If a mapping file for the specified `--build` is not found, `annofetch` will gracefully inform you and proceed without applying chromosome name conversion.

## 🐍 Using as a Python Library

You can also import and use the `EnsemblDownloader` class directly in your Python scripts:

```python
from annofetch.downloader import EnsemblDownloader

# Initialize the downloader for a specific species, release, and build
human_downloader = EnsemblDownloader(
    species="homo_sapiens",
    release=112,
    build="GRCh38",
    output_dir="/path/to/my_data"
)

# Download genome with UCSC style
print("Downloading human GRCh38 genome (UCSC style)...")
human_downloader.download_genome(add_ucsc_style=True)

# Download GTF without chromosome prefix
print("\nDownloading human GRCh38 GTF (no chr prefix)...")
human_downloader.download_gtf(remove_chr_prefix=True)

# Download mouse genome keeping original names
mouse_downloader = EnsemblDownloader(
    species="mus_musculus",
    release=112,
    build="GRCm39",
    output_dir="/path/to/my_data"
)
print("\nDownloading mouse GRCm39 genome (original names)...")
mouse_downloader.download_genome(add_ucsc_style=False)
```


## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or find any bugs, please open an issue or submit a pull request on GitHub.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Write tests for your changes (if applicable).
5. Commit your changes (`git commit -am 'Add new feature'`).
6. Push to the branch (`git push origin feature/your-feature`).
7. Create a new Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

---


