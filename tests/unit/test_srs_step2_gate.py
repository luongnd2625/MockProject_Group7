"""Gate 1B verification tests for Step 2 SRS User Stories, State Machines, and ACTIVE document rules."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
STEP2_DOC = ROOT / "docs/01_SRS/02_SRS_User_Stories_and_Flows.md"


def test_step2_doc_contains_all_40_user_stories() -> None:
    assert STEP2_DOC.is_file()
    content = STEP2_DOC.read_text(encoding="utf-8")

    expected_stories = (
        [f"PUB-0{i}" for i in range(1, 6)]
        + [f"SAL-0{i}" for i in range(1, 10)]
        + [f"TRN-0{i}" for i in range(1, 6)]
        + [f"RNT-0{i}" for i in range(1, 6)]
        + [f"WHS-0{i}" for i in range(1, 7)]
        + [f"PAY-0{i}" for i in range(1, 5)]
        + [f"ADM-0{i}" for i in range(1, 7)]
    )
    assert len(expected_stories) == 40
    missing = [story for story in expected_stories if f"**`{story}`**" not in content]
    assert not missing, f"Missing User Story specifications: {missing}"


def test_step2_doc_uses_active_versions_and_excludes_superseded_as_rules() -> None:
    content = STEP2_DOC.read_text(encoding="utf-8")

    for active_doc in ("POL-COM-003 v1.1", "POL-TRN-001 v2.0", "SOP-WHS-001 v1.1", "SOP-ADM-001 v1.1"):
        assert active_doc in content, f"Missing ACTIVE doc reference: {active_doc}"

    forbidden_superseded = [
        r"POL-COM-003\s+v1\.0",
        r"POL-TRN-001\s+v1\.0",
        r"POL-TRN-001\s+v1\.1",
        r"SOP-WHS-001\s+v1\.0",
        r"SOP-ADM-001\s+v1\.0",
    ]
    for pattern in forbidden_superseded:
        assert not re.search(pattern, content), f"Found superseded version reference: {pattern}"
