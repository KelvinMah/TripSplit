"""Reproducible sample extraction evaluation; NOT the resume's 100-case metric."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.preferences import fallback_extract  # noqa: E402

cases = json.loads((Path(__file__).parent / "scenarios.json").read_text(encoding="utf-8"))
correct = 0
for case in cases:
    result = fallback_extract(case["conversation"])
    observed = {item for traveler in result.travelers for item in traveler.interests}
    passed = len(result.travelers) == case["expected_travelers"] and set(case["expected_interests"]).issubset(observed)
    correct += int(passed)
    print(f"{'PASS' if passed else 'FAIL'} {case['id']}")
print(f"Sample exact-case pass rate: {correct}/{len(cases)} ({correct / len(cases):.1%})")
