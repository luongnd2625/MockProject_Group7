"""Gate 1C verification tests for Step 3 Business Rules (BR-01..18), NFRs (NFR-01..12), and 11 core entities."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STEP3_DOC = ROOT / "docs/01_SRS/03_Business_Rules_and_NFR_Constraints.md"


def test_step3_doc_covers_all_business_rules_and_nfrs() -> None:
    assert STEP3_DOC.is_file()
    content = STEP3_DOC.read_text(encoding="utf-8")

    missing_br = [f"BR-{i:02d}" for i in range(1, 19) if f"BR-{i:02d}" not in content]
    assert not missing_br, f"Missing Business Rules: {missing_br}"

    missing_nfr = [f"NFR-{i:02d}" for i in range(1, 13) if f"NFR-{i:02d}" not in content]
    assert not missing_nfr, f"Missing NFRs: {missing_nfr}"


def test_step3_doc_covers_all_11_data_entity_groups() -> None:
    content = STEP3_DOC.read_text(encoding="utf-8")
    expected_entities = [
        "Customer",
        "ServiceRequest",
        "Quote / QuoteLine",
        "ServiceOrder",
        "Vehicle / Driver",
        "ResourceBooking",
        "TransportTrip",
        "RentalRecord",
        "WarehouseLot / LotLine",
        "WarehouseDocument",
        "Payment / Charge",
    ]
    missing = [e for e in expected_entities if e not in content]
    assert not missing, f"Missing core entity groups: {missing}"
    assert "BIGINT" in content
    assert "idempotency_key" in content
    assert "version" in content
