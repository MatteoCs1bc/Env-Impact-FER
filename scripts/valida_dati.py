"""Controlla i CSV in data/. Uso: python scripts/valida_dati.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import carica_conflitti, carica_indicatori, valida  # noqa: E402


def main() -> int:
    problemi = valida()
    if problemi:
        print(f"Trovati {len(problemi)} problemi:")
        for p in problemi:
            print(f"  - {p}")
        return 1
    ind = carica_indicatori()
    print(
        f"Dati validi: {len(ind)} valori, {ind['fonte'].nunique()} fonti energetiche, "
        f"{ind['fonte_id'].nunique()} fonti bibliografiche, {len(carica_conflitti())} conflitti."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
