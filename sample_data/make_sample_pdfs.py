#!/usr/bin/env python3
"""Generate tiny synthetic bill PDFs for Gemini multimodal demo.

Stdlib only. Re-run from repo root:
    python sample_data/make_sample_pdfs.py
"""

from __future__ import annotations

import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

BILLS = [
    {
        "out": "electricity_bill_June2025.pdf",
        "title": "Shanghai Power — electricity bill (synthetic)",
        "lines": [
            "SHANGHAI POWER SUPPLY COMPANY",
            "ELECTRICITY BILL — ACCOUNT 3101-4482-00",
            "",
            "Customer: GreenLeaf Trading Co., Ltd.  (FICTIONAL)",
            "Service Address: Unit 801, 88 Century Avenue, Pudong, Shanghai",
            "Billing Period: June 2025 (2025-06-01 to 2025-06-30)",
            "Meter No. P02183441",
            "Previous reading: 41,250.00 kWh",
            "Current reading:  47,250.00 kWh",
            "Multiplier: 1",
            "Rate: Commercial - General (B)",
            "Energy: 6,000.00 kWh x 0.852 CNY/kWh = 5,112.00 CNY",
            "Demand: 18 kW x 39.00 CNY/kW = 702.00 CNY",
            "Total consumption for June 2025: 6,000 kWh",
            "Amount Due: 5,988.60 CNY (incl. VAT)",
            "Due Date: 2025-07-20",
            "Note: All consumption figures stated on this bill are metered.",
        ],
    },
    {
        "out": "natural_gas_bill_June2025.pdf",
        "title": "Shanghai Gas — natural gas bill (synthetic)",
        "lines": [
            "SHANGHAI GAS GROUP — INVOICE / BILLING STATEMENT",
            "",
            "Customer: GreenLeaf Trading Co., Ltd.  (FICTIONAL)",
            "Account: G-7702-5561",
            "Service Address: Unit 801, 88 Century Avenue, Pudong, Shanghai",
            "Billing Month: June 2025",
            "Meter G0921 previous reading: 2,140.0 m3",
            "Meter G0921 current reading:  2,460.0 m3",
            "Natural gas consumed this period: 320 m3",
            "Unit price: 3.95 CNY/m3",
            "Amount: 1,264.00 CNY",
            "Use: office pantry cooking and winter heating boiler (Nov-Mar).",
        ],
    },
]


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_simple_pdf(path: Path, title: str, lines: list[str]) -> None:
    """Minimal PDF 1.4 with Helvetica body text. Intentionally tiny."""
    y0 = 760
    leading = 16
    content_cmds = ["BT", "/F1 11 Tf", f"50 {y0} Td"]
    first = True
    for line in [title, ""] + lines:
        if not first:
            content_cmds.append(f"0 -{leading} Td")
        first = False
        content_cmds.append(f"({_escape(line)}) Tj")
    content_cmds.append("ET")
    stream = "\n".join(content_cmds).encode("latin-1", errors="replace")

    objects = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    add(b"<< /Type /Catalog /Pages 2 0 R >>")
    add(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    add(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
    )
    add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    buf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, body in enumerate(objects, start=1):
        offsets.append(len(buf))
        buf.extend(f"{i} 0 obj\n".encode("ascii"))
        buf.extend(body)
        buf.extend(b"\nendobj\n")
    xref_at = len(buf)
    buf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    buf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        buf.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    buf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_at}\n%%EOF\n"
        ).encode("ascii")
    )
    path.write_bytes(bytes(buf))


def main() -> None:
    stamp = datetime.date.today().isoformat()
    for bill in BILLS:
        dest = HERE / bill["out"]
        write_simple_pdf(dest, bill["title"] + f"  generated {stamp}", bill["lines"])
        print(f"{dest.name}\t{dest.stat().st_size} bytes")


if __name__ == "__main__":
    main()
