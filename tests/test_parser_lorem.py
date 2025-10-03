import sys
from pathlib import Path

import pytest

# Ensure ocr-service is on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ocr-service"))

from intelligent_receipt_parser import receipt_parser

LOREM_RECEIPT_TEXT = """
LOREM SHOP
123 ANYWHERE ST

1: 0275 Ut wisi enim           2.99
2: 1227 Nibh euismod            1.30
3: 0942 Rdol magna             17.00
4: 0257 Mnonuy nibh             6.99
5: 1693 Kaoreet dolore          1.20
6: 9463 Taliquam erat           5.10
7: 0059 Aeuismod               10.00
8: 3556 Knonuy nib              4.99

Discount                       $5.99
TOTAL                          $34.50
""".strip()

EXPECTED_ITEMS = [
    "Ut Wisi Enim",
    "Nibh Euismod",
    "Rdol Magna",
    "Mnonuy Nibh",
    "Kaoreet Dolore",
    "Taliquam Erat",
    "Aeuismod",
    "Knonuy Nib",
]

@pytest.mark.parametrize("text", [LOREM_RECEIPT_TEXT])
def test_parser_handles_numbered_code_lines(text):
    items = receipt_parser.parse_receipt_items(text)
    names = {item["name"] for item in items}

    for expected in EXPECTED_ITEMS:
        assert expected in names, f"Missing item: {expected}"

    unwanted = {
        name
        for name in names
        if any(token in name.lower() for token in ["discount", "total", "net @", "net /", "net"])
    }
    assert not unwanted, f"Parser included unwanted summary lines: {unwanted}"

    assert len(items) >= len(EXPECTED_ITEMS)
