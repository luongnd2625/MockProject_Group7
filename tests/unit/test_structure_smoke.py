"""Gate 0 smoke tests verifying repository structure and baseline configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_directories_exist() -> None:
    expected_dirs = [
        "artifacts",
        "backend/app/api",
        "backend/app/core",
        "backend/app/db/migrations",
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/repositories",
        "backend/app/services",
        "data/policies",
        "data/seed",
        "data/uploads",
        "docs/00_Quy_Trinh",
        "docs/01_SRS/baseline",
        "docs/02_Design_ERD_SDS",
        "docs/03_Testing_UAT",
        "docs/04_Project_Management",
        "docs/05_Release_Manuals",
        "docs/99_Support_Documents",
        "frontend/src/portals/public",
        "frontend/src/portals/internal",
        "src",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "tests/agent_eval",
    ]
    for rel in expected_dirs:
        assert (ROOT / rel).is_dir(), f"Missing directory: {rel}"


def test_srs_baseline_pdfs_moved_into_docs() -> None:
    srs_dir = ROOT / "docs/01_SRS/baseline"
    pdfs = sorted(p.name for p in srs_dir.glob("*.pdf"))
    assert len(pdfs) == 9
    assert "00_Overall_SRS.pdf" in pdfs
    assert "08_Acceptance_and_Traceability.pdf" in pdfs
    assert not (ROOT / "SRS").exists()
    assert not (ROOT / "Support Documents").exists()


def test_src_agent_modules_match_reference_architecture() -> None:
    expected_files = [
        "__init__.py",
        "agent_orchestrator.py",
        "config.py",
        "evaluator.py",
        "generate_policy_pdfs.py",
        "llm_client.py",
        "memory_manager.py",
        "mock_systems.py",
        "models.py",
        "rag_engine.py",
        "tool_registry.py",
        "validators.py",
    ]
    for name in expected_files:
        assert (ROOT / "src" / name).is_file(), f"Missing src module: {name}"


def test_backend_config_defaults() -> None:
    from backend.main import get_app_info

    info = get_app_info()
    assert info["name"] == "MockProject_Group7"
    assert info["timezone"] == "Asia/Ho_Chi_Minh"
    assert info["currency"] == "VND"


def test_step1_overview_doc_exists() -> None:
    doc = ROOT / "docs/01_SRS/01_Overview_and_Authorization.md"
    assert doc.is_file()
    content = doc.read_text(encoding="utf-8")
    assert "MockProject_Group7" in content
    for role in ("GST", "SAL", "DSP", "WHS", "FIN", "MGR", "ADM"):
        assert role in content
