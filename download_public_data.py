"""Download the public ME/CFS blood RNA-seq datasets listed in MANIFEST.csv into ./public_mecfs_data/<dataset>/.

Every file is fetched from its original source (GEO, NCBI, UCSC, PMC, STRING) and checked against the SHA-256 in the manifest:
  strict -> a mismatch is an error (the file is not what the analyses used);
  warn   -> a mismatch is reported but kept (the source may have updated the file);
  none   -> no check (the source changes daily, e.g. NCBI gene_info).
Files that are already present with a matching hash are skipped. Standard library only (Python >= 3.8).

Usage:
  python download_public_data.py                     # ME/CFS datasets
  python download_public_data.py --reference         # also STRING v12 (reference network, ~85 MB)
  python download_public_data.py --datasets GSE270045 GSE128078
  python download_public_data.py --list              # show what is in the manifest
Embargoed entries (embargo_until in the future) are never downloaded automatically; the script prints how to get them.
"""
import argparse, csv, datetime as dt, hashlib, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEST = HERE / "public_mecfs_data"
MANIFEST = HERE / "MANIFEST.csv"


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def fetch(url, out, retries=3):
    tmp = out.with_suffix(out.suffix + ".part")
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})   # GEO serves a browser check to browser-like agents
            with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
                ctype = r.headers.get("Content-Type", "")
                got = 0
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b); got += len(b)
                    print(f"\r    {got / 1e6:8.1f} MB", end="", flush=True)
            print()
            if "text/html" in ctype and not out.name.endswith((".html", ".txt")):
                raise IOError("server returned an HTML page instead of the file (blocked or not found)")
            tmp.replace(out)
            return
        except Exception as e:                                                     # noqa: BLE001
            print(f"\n    attempt {attempt}/{retries} failed: {e}")
            tmp.unlink(missing_ok=True)
            if attempt < retries:
                time.sleep(10 * attempt)
    raise IOError(f"could not download {url}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", nargs="*", help="only these dataset ids (default: all ME/CFS datasets)")
    ap.add_argument("--reference", action="store_true", help="also download reference files (STRING v12)")
    ap.add_argument("--list", action="store_true", help="list the manifest and exit")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    if a.list:
        for r in rows:
            print(f"{r['dataset']:12s} {r['group']:9s} {int(r['size_bytes']) / 1e6:9.1f} MB  {r['file']}")
        return
    today = dt.date.today(); errors = []
    for r in rows:
        if a.datasets and r["dataset"] not in a.datasets:
            continue
        if not a.datasets and r["group"] == "reference" and not a.reference:
            continue
        out_dir = DEST / r["dataset"]; out_dir.mkdir(parents=True, exist_ok=True); out = out_dir / r["file"]
        print(f"[{r['dataset']}] {r['file']}  ({int(r['size_bytes']) / 1e6:.1f} MB)")
        emb = r["embargo_until"].strip()
        if emb and today < dt.date.fromisoformat(emb):
            print(f"    EMBARGOED until {emb}: not downloaded. {r['notes']}")
            continue
        if emb and not out.exists():
            print(f"    Manual download required (private-to-public GEO series): open {r['url']}, download {r['file']} and put it in {out_dir}")
            continue
        if out.exists() and (r["hash_check"] == "none" or sha256(out) == r["sha256"]):
            print("    already present (hash OK)"); continue
        try:
            fetch(r["url"], out)
        except IOError as e:
            errors.append(f"{r['dataset']}/{r['file']}: {e}"); continue
        if r["hash_check"] == "none":
            print("    downloaded (no hash check: source updates this file)"); continue
        h = sha256(out)
        if h == r["sha256"]:
            print("    SHA-256 OK")
        elif r["hash_check"] == "strict":
            errors.append(f"{r['dataset']}/{r['file']}: SHA-256 mismatch ({h})")
        else:
            print(f"    WARNING: SHA-256 differs from the manifest (source may have been updated): {h}")
    if errors:
        print("\nProblems:\n  " + "\n  ".join(errors)); sys.exit(1)
    print(f"\nDone. Files are in {DEST}")


if __name__ == "__main__":
    main()
