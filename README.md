# Public ME/CFS blood RNA-seq data

This repository contains a reproducible way to download public **ME/CFS blood transcriptome datasets** (plus one PASC dataset and a reference network) from their original sources. Each file is verified with SHA-256.

It holds **no raw data itself**. The script downloads everything into `public_mecfs_data/`, which Git ignores.

```bash
python download_public_data.py              # the ME/CFS datasets (~1.35 GB, mostly GSE214283)
python download_public_data.py --reference  # also STRING v12 (~85 MB)
python download_public_data.py --list       # what is in the manifest
python download_public_data.py --datasets GSE270045 GSE128078
```

Requirements: Python ≥ 3.8 (standard library only) and an internet connection.

## Datasets

| Dataset | Tissue | Design | Groups | Reference |
|---|---|---|---|---|
| **GSE128078** | whole blood | days 1, 2, 3, 7 around two cardiopulmonary exercise tests (CPET) | 14 ME/CFS, 11 controls | Bouquet et al., *PLoS One* 2019 |
| **GSE214283** | PBMC, single-cell (10x) | rest (D1) and 24 h after CPET (D2) | 30 ME/CFS, 28 controls (after QC) | Vu et al., *Cell Rep Med* 2024 |
| **GSE227375** | PBMC, bulk | baseline, maximal exertion, recovery | ME/CFS and controls (162 samples with NCBI counts) | Van Booven et al., 2023 |
| **GSE270045** | whole blood | single draw | 19 post-COVID ME/CFS, 17 controls | GEO GSE270045 |
| GSE295721 (PASC) | leukocytes | cross-sectional and follow-up | PASC, post-COVID without PASC, healthy | Beimers et al., *Sci Rep* 2026 |
| STRING v12 (reference) | — | human protein–protein interactions | — | Szklarczyk et al., *NAR* 2023 |

**Notes:**
- **GSE128078:** the GEO file holds isoform-level FPKM keyed by RefSeq accession. UCSC's `refGene` (hg19) table maps accessions to gene symbols.
- **GSE214283:** the clinical bins come from the paper's Data S1 (`mmc2.xlsx`).
- **GSE227375:** GEO has no submitter count matrix, so we use the **NCBI-generated** raw counts. NCBI Gene's `gene_info` maps Entrez IDs to symbols; it is updated daily, so its hash is not checked.
- **GSE270045:** in this series, controls and patients come from different sample series (prefixes CCI/HP vs S), so group and sample source are confounded.
- **GSE295721 (PASC):** it is **private on GEO until 2026-12-01**. The script will not download it before then. After that date, download the counts from the GEO page and place them in `public_mecfs_data/GSE295721/`. This dataset is PASC, not ME/CFS; it is included for comparison.

## Files in this repository
- `MANIFEST.csv`: every file with its source URL, size, SHA-256, hash policy (`strict` / `warn` / `none`), embargo date and citation.
- `download_public_data.py`: the downloader.
- `metadata/`: small sample tables taken from GEO (group, time point, person), used to assign samples:
  - `GSE128078_samples.csv`
  - `GSE214283_samples.csv`
  - `GSE227375_samples_soft.txt`
  - `GSE270045_samples_soft.txt`

## Hash policy
- **`strict`:** a mismatch means the file differs from the one used in our analyses, and the script reports an error.
- **`warn`:** the source may legitimately update the file (UCSC, PMC, NCBI counts, STRING), so a mismatch is only reported.
- **`none`:** the source changes daily (NCBI `gene_info`), so there is no check.

## Use and citation
The data belong to their original authors and repositories. Please cite the publications above and follow each source's terms (GEO/NCBI, UCSC, PMC; STRING is CC BY 4.0). Nothing here is redistributed. The script only fetches from the original sources.

If GEO starts returning HTML pages or HTTP 403 errors, NCBI is temporarily rate-limiting. Wait and re-run: files already downloaded and verified are skipped.
