"""Test dei dati e dell'avvio delle pagine. Uso: python -m pytest"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.data import valida

PAGINE = sorted(Path(__file__).resolve().parent.parent.joinpath("pages").glob("*.py"))


def test_dati_validi():
    assert valida() == []


@pytest.mark.parametrize("pagina", PAGINE, ids=lambda p: p.stem)
def test_pagina_senza_errori(pagina):
    at = AppTest.from_file(str(pagina), default_timeout=60).run()
    assert not at.exception, at.exception
