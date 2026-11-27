"""Gate 1D verification tests ensuring Step 4 Traceability Matrix & Test Plan are complete before ERD design."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STEP4_DOC = ROOT / "docs/03_Testing_UAT/Test_Plan_and_Traceability.md"


def test_step4_traceability_covers_all_40_stories() -> None:
    assert STEP4_DOC.is_file()
    content = STEP4_DOC.read_text(encoding="utf-8")

    expected_stories = (
        [f"PUB-0{i}" for i in range(1, 6)]
        + [f"SAL-0{i}" for i in range(1, 10)]
        + [f"TRN-0{i}" for i in range(1, 6)]
        + [f"RNT-0{i}" for i in range(1, 6)]
        + [f"WHS-0{i}" for i in range(1, 7)]
        + [f"PAY-0{i}" for i in range(1, 5)]
        + [f"ADM-0{i}" for i in range(1, 7)]
    )
    missing = [s for s in expected_stories if f"`{s}`" not in content]
    assert not missing, f"Missing stories in Traceability Matrix: {missing}"


def test_step4_covers_all_e2e_neg_br_and_nfr() -> None:
    content = STEP4_DOC.read_text(encoding="utf-8")

    missing_e2e = [f"E2E-0{i}" for i in range(1, 4) if f"E2E-0{i}" not in content]
    assert not missing_e2e, f"Missing E2E scenarios: {missing_e2e}"

    missing_neg = [f"NEG-{i:02d}" for i in range(1, 25) if f"NEG-{i:02d}" not in content]
    assert not missing_neg, f"Missing NEG scenarios: {missing_neg}"

    missing_br = [f"BR-{i:02d}" for i in range(1, 19) if f"BR-{i:02d}" not in content]
    assert not missing_br, f"Missing BR references: {missing_br}"

    missing_nfr = [f"NFR-{i:02d}" for i in range(1, 13) if f"NFR-{i:02d}" not in content]
    assert not missing_nfr, f"Missing NFR references: {missing_nfr}"
