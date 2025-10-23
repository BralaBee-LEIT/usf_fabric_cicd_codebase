import argparse, os, zipfile


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        if ".git" in root or "/dist" in root:
            continue
        for file in files:
            fp = os.path.join(root, file)
            arc = os.path.relpath(fp, path)
            ziph.write(fp, arc)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zf:
        zipdir(args.input, zf)
    print(f"Packaged -> {args.output}")
