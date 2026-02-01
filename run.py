from __future__ import annotations

from pathlib import Path
import yaml
import pandas as pd

from src.build_model import build_model
from src.qa_checks import run_qa
from src.charts import save_charts
from src.memo import render_memo


def main() -> None:
    root = Path(__file__).resolve().parent
    inputs_path = root / "inputs" / "assumptions.yaml"
    out_dir = root / "outputs"

    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = yaml.safe_load(inputs_path.read_text(encoding="utf-8"))

    scenarios = list((cfg.get("scenarios") or {}).keys())
    if not scenarios:
        scenarios = [str(cfg.get("active_scenario", "base"))]

    all_frames: list[pd.DataFrame] = []
    all_issues: list[str] = []

    for scenario_name in scenarios:
        df = build_model(cfg, scenario_name=str(scenario_name))
        all_frames.append(df)

        # Per-scenario outputs
        df_out = df.copy()
        df_out["month"] = df_out["month"].dt.strftime("%Y-%m")
        (out_dir / f"model_outputs_{scenario_name}.csv").write_text(df_out.to_csv(index=False), encoding="utf-8")

        charts_dir = out_dir / "charts" / str(scenario_name)
        save_charts(df, charts_dir)

        issues = run_qa(df)
        all_issues.append(f"## {scenario_name}\n" + "\n".join(f"- {x}" for x in issues))

        render_memo(
            template_path=root / "templates" / "cfo_memo_template.md",
            out_path=out_dir / f"cfo_memo_{scenario_name}.md",
            cfg={**cfg, "active_scenario": str(scenario_name)},
            df=df,
        )

    # All scenarios in one file
    df_all = pd.concat(all_frames, ignore_index=True)
    df_all_out = df_all.copy()
    df_all_out["month"] = df_all_out["month"].dt.strftime("%Y-%m")
    (out_dir / "model_outputs_all_scenarios.csv").write_text(df_all_out.to_csv(index=False), encoding="utf-8")

    (out_dir / "qa_report.md").write_text("\n\n".join(all_issues) + "\n", encoding="utf-8")

    print("Done. Outputs written to:", out_dir)


if __name__ == "__main__":
    main()
