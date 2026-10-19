import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def example():
    return json.loads((ROOT / "examples" / "native_calculate.json").read_text(encoding="utf-8"))
