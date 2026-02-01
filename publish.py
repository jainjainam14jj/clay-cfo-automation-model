from __future__ import annotations

import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

import yaml


def run(cmd: list[str], cwd: Path) -> str:
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(
            f"Command failed ({p.returncode}): {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
        )
    return p.stdout.strip()


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    root = Path(__file__).resolve().parent

    # 1) Build outputs
    print("[1/4] Running model build (python run.py)…")
    run(["python", "run.py"], cwd=root)

    outputs = root / "outputs"
    docs = root / "docs"
    inputs_path = root / "inputs" / "assumptions.yaml"
    cfg = yaml.safe_load(inputs_path.read_text(encoding="utf-8"))

    # 2) Recreate docs folder and copy the publishable artifacts
    print("[2/4] Syncing outputs → docs/ (GitHub Pages)…")
    if docs.exists():
        shutil.rmtree(docs)
    (docs / "charts" / "base").mkdir(parents=True, exist_ok=True)
    (docs / "charts" / "upside").mkdir(parents=True, exist_ok=True)
    (docs / "charts" / "downside").mkdir(parents=True, exist_ok=True)

    # CSVs
    for fn in [
        "model_outputs_all_scenarios.csv",
        "model_outputs_base.csv",
        "model_outputs_upside.csv",
        "model_outputs_downside.csv",
    ]:
        shutil.copy2(outputs / fn, docs / fn)

    # Memos
    for fn in ["cfo_memo_base.md", "cfo_memo_upside.md", "cfo_memo_downside.md"]:
        shutil.copy2(outputs / fn, docs / fn)

    # Charts by scenario
    for scenario in ["base", "upside", "downside"]:
        src_dir = outputs / "charts" / scenario
        dst_dir = docs / "charts" / scenario
        for png in src_dir.glob("*.png"):
            shutil.copy2(png, dst_dir / png.name)

    # Assumptions summary (for the Lovable app)
    assumptions_summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "horizon": {
            "start_month": cfg.get("start_month"),
            "end_month": cfg.get("end_month"),
        },
        "currency": cfg.get("currency", "USD"),
        "starting_state": {
            "starting_customers": cfg.get("starting_customers"),
            "starting_arr_usd": cfg.get("starting_arr_usd"),
        },
        "growth": {
            "new_customers_per_month": cfg.get("new_customers_per_month"),
            "logo_churn_rate_monthly": cfg.get("logo_churn_rate_monthly"),
            "expansion_rate_monthly": cfg.get("expansion_rate_monthly"),
        },
        "monetization": {
            "seats_per_customer": cfg.get("seats_per_customer"),
            "price_per_seat_monthly": cfg.get("price_per_seat_monthly"),
            "credits_per_customer_monthly": cfg.get("credits_per_customer_monthly"),
            "price_per_1000_credits": cfg.get("price_per_1000_credits"),
        },
        "costs": {
            "cogs_percent_of_revenue": cfg.get("cogs_percent_of_revenue"),
            "ai_cost_per_1000_credits": cfg.get("ai_cost_per_1000_credits"),
            "opex_monthly": cfg.get("opex_monthly", {}),
        },
        "scenarios": cfg.get("scenarios", {}),
    }
    (docs / "assumptions_summary.json").write_text(
        json.dumps(assumptions_summary, indent=2), encoding="utf-8"
    )

    # Simple landing page for Pages
    index = docs / "index.html"
    index.write_text(
        """<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Clay CFO Automation Model — Outputs</title>
    <style>
      body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;max-width:900px;margin:40px auto;padding:0 16px;}
      code{background:#f4f4f4;padding:2px 6px;border-radius:6px;}
      a{color:#2a6fdb}
    </style>
  </head>
  <body>
    <h1>Clay CFO Automation Model — Static Outputs</h1>
    <p>These files are published for the Lovable dashboard via GitHub Pages.</p>

    <h2>Assumptions</h2>
    <ul>
      <li><a href=\"assumptions_summary.json\">assumptions_summary.json</a></li>
    </ul>

    <h2>CSVs</h2>
    <ul>
      <li><a href=\"model_outputs_all_scenarios.csv\">model_outputs_all_scenarios.csv</a></li>
      <li><a href=\"model_outputs_base.csv\">model_outputs_base.csv</a></li>
      <li><a href=\"model_outputs_upside.csv\">model_outputs_upside.csv</a></li>
      <li><a href=\"model_outputs_downside.csv\">model_outputs_downside.csv</a></li>
    </ul>

    <h2>Memos</h2>
    <ul>
      <li><a href=\"cfo_memo_base.md\">cfo_memo_base.md</a></li>
      <li><a href=\"cfo_memo_upside.md\">cfo_memo_upside.md</a></li>
      <li><a href=\"cfo_memo_downside.md\">cfo_memo_downside.md</a></li>
    </ul>

    <h2>Charts</h2>
    <ul>
      <li><a href=\"charts/base/\">charts/base/</a></li>
      <li><a href=\"charts/upside/\">charts/upside/</a></li>
      <li><a href=\"charts/downside/\">charts/downside/</a></li>
    </ul>

    <p><strong>Tip:</strong> Edit <code>inputs/assumptions.yaml</code>, then run <code>python publish.py</code>.</p>
  </body>
</html>
""",
        encoding="utf-8",
    )

    # 3) Commit + push
    print("[3/4] Committing docs/ updates…")
    run(["git", "add", "docs", "publish.py"], cwd=root)
    # commit may fail if nothing changed; handle gracefully
    try:
        run(["git", "commit", "-m", "Publish updated CFO pack"], cwd=root)
    except RuntimeError as e:
        msg = str(e)
        if "nothing to commit" not in msg and "no changes added" not in msg:
            raise
        print("No git changes to commit.")

    print("[4/4] Pushing to origin/main…")
    run(["git", "push"], cwd=root)

    print("Done. GitHub Pages will update shortly.")


if __name__ == "__main__":
    main()
