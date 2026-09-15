import pandas as pd
from src.export_parity import iso

def test_iso_timestamp_is_explicit():
    assert iso(pd.Timestamp("2025-01-01T12:00:00Z"))=="2025-01-01T12:00:00+00:00"

def test_fixture_schema_is_stable():
    from src.export_parity import REQUIRED
    assert "symbol" in REQUIRED and "entry" in REQUIRED
    assert "fill_time" in REQUIRED and "result_r" in REQUIRED
