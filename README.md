# MockProject_Group7 — Hệ thống Quản lý Vận tải, Cho thuê xe & Kho bãi Trung chuyển

Dự án **MockProject_Group7** triển khai theo chiến lược **2 Giai đoạn Lớn (Software-First → AI Agent)**:
1. **Phần 1 — Software Core** (`backend/` Python FastAPI + PostgreSQL, `frontend/` React + TypeScript): Xây dựng đầy đủ 7 phân hệ nghiệp vụ theo bộ SRS (`PUB`, `SAL`, `TRN`, `RNT`, `WHS`, `PAY`, `ADM`), kèm **Test & Verify xen kẽ sau mỗi bước** trước khi đóng băng (`v1.0-software-freeze`).
2. **Phần 2 — Tích hợp AI Agent** (`src/`): Kích hoạt sau khi chốt Software, triển khai 12 module chuẩn theo kiến trúc tham chiếu (`PolicyRAGEngine`, `AgentOrchestrator`, `ToolRegistry`, `MemoryManager`, `Validators`, `Evaluator`).

## Cấu trúc thư mục
- `artifacts/` — Báo cáo kiểm thử, kết quả benchmark hiệu năng (`NFR-04`), kết quả eval AI Agent.
- `backend/` — Backend API bằng Python (FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL).
- `data/` — Tài liệu nghiệp vụ (`policies/`), dữ liệu UAT (`seed/`), vùng lưu tệp đính kèm (`uploads/`).
- `docs/` — Toàn bộ tài liệu dự án phân loại theo nhóm (`00_Quy_Trinh`, `01_SRS`, `02_Design_ERD_SDS`, `03_Testing_UAT`, `04_Project_Management`, `05_Release_Manuals`, `99_Support_Documents`).
- `frontend/` — Giao diện Web bằng React + TypeScript (Public Portal 390px+ & Internal Portal 1366x768).
- `src/` — Lõi AI Agent bằng Python (12 modules, kích hoạt ở Phần 2).
- `tests/` — Kiểm thử đa tầng (`unit/`, `integration/`, `e2e/`, `agent_eval/`).

## Kiểm tra nhanh (Gate 0)
```bash
pytest -q
```
