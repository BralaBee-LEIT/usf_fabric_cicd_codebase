import argparse
from utilities.purview_api import trigger_scan

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True, choices=["dev", "qa", "prod"])
    args = ap.parse_args()
    collection = f"usf-{args.env}"
    trigger_scan(collection, f"scan-{args.env}")
    print(f"[trigger_purview_scan] Triggered Purview scan for {args.env}.")
