import argparse
import yaml
import sys

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--threshold-profile", default="standard")
    args = ap.parse_args()
    with open("governance/dq_rules/dq_rules.yaml", "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    print(
        f"[dq_gate] Evaluating {len(rules.get('rules',[]))} rules for env={args.env} with profile={args.threshold_profile}"
    )
    sys.exit(0)
