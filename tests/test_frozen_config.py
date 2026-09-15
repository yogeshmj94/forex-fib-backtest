import json
from pathlib import Path

def test_frozen_research_config():
    cfg=json.loads(Path("config.json").read_text())
    assert cfg["stop_buffer_pips"] == 3.0
    assert len(cfg["pairs"]) == 20

def test_production_risk_is_documented_separately():
    # Backtest config may preserve the OOS research risk. Production EA risk is
    # frozen at 0.20% after portfolio/Monte-Carlo analysis.
    text=Path("docs/EA_VALIDATION.md").read_text()
    assert "0.20% of initial account balance" in text
    assert "fixed 1R take profit" in text
