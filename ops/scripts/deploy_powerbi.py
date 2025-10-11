import argparse
from utilities.powerbi_api import deploy_via_pipeline

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", required=True)
    ap.add_argument("--stage", required=True)
    args = ap.parse_args()
    deploy_via_pipeline(args.pipeline, args.stage)
    print("[deploy_powerbi] Triggered Power BI deployment pipeline (placeholder).")
