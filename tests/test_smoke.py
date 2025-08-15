import os
from src.analysis import analyze_stock

def test_env_token():
    assert os.getenv("TUSHARE_TOKEN") is not None, "TUSHARE_TOKEN 未配置"

def test_analyze_smoke():
    ts_code = os.getenv("TEST_TS_CODE", "600519.SH")
    res = analyze_stock(ts_code, start="20180101")
    assert "composite" in res and "subscores" in res
