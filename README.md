# Clay CFO Automation Model (Monthly)

**Goal:** Edit a single assumptions file → run one command → get a CFO-ready output pack:
- `outputs/model_outputs_all_scenarios.csv`
- `outputs/model_outputs_base.csv` / `model_outputs_upside.csv` / `model_outputs_downside.csv`
- `outputs/charts/<scenario>/*.png`
- `outputs/cfo_memo_<scenario>.md`
- `outputs/qa_report.md`

## Quickstart
```bash
cd clay-cfo-automation-model
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Inputs
Edit: `inputs/assumptions.yaml`

## Outputs
Generated under `outputs/`.
