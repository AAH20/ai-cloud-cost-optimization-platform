from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import RecoveryEngine
from .normalizer import load_costs


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence-backed multi-cloud cost recovery")
    parser.add_argument("analyze", help="FOCUS-compatible CSV file")
    parser.add_argument("--output", "-o", help="write report to a file")
    args = parser.parse_args()
    report = json.dumps(RecoveryEngine(load_costs(args.analyze)).report(), indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()

