# Bước 4 — Kế hoạch Kiểm thử, Ma trận Truy vết & Đặc tả UAT (`Test_Plan_and_Traceability`)

- **Dự án**: `MockProject_Group7` — Hệ thống Quản lý Vận tải, Cho thuê xe & Kho bãi Trung chuyển
- **Giai đoạn**: Phần 1 (Software Core) — Bước Lớn 4 (trước khi thiết kế ERD & PostgreSQL)
- **Tài liệu nguồn**: `docs/01_SRS/baseline/08_Acceptance_and_Traceability.pdf`, `docs/99_Support_Documents/1_SWT301/`, và các tài liệu Bước 1–3 (`01_Overview_and_Authorization.md`, `02_SRS_User_Stories_and_Flows.md`, `03_Business_Rules_and_NFR_Constraints.md`).

---

## 1. Chiến lược Kiểm thử Đa tầng (Theo `SWT301` & `SRS/08`)

1. **Tầng 1 — Static Testing (`SWT3` & Linting)**:
   - Walkthrough tài liệu SRS/RDS/ERD/SDS/Test Plan giữa các bước trước khi code (`Gate 1A`–`1D`, `Gate 2`).
   - Linter & Type check (`ruff`, Pydantic strict types, TypeScript `tsc -b`) trên code `backend/` và `frontend/`.
2. **Tầng 2 — Unit Testing (`tests/unit/`)**:
   - Kiểm tra tách biệt logic tính tiền `VND` làm tròn (`BR-03/13`), hàm kiểm tra trùng khoảng `[start, end)` (`BR-07`), tính tồn kho từ chứng từ `POSTED` (`BR-11/12`), state machine transitions, chuẩn hóa SĐT & biển số xe.
3. **Tầng 3 — Integration, Concurrency & Negative Control Testing (`tests/integration/`)**:
   - Dùng `pytest` + `httpx` gọi trực tiếp vào FastAPI + PostgreSQL thật (test transaction rollback/lock).
   - Bao phủ đủ **24 kịch bản `NEG-01`..`NEG-24`**, IDOR/RBAC (`NFR-01`), thu hồi phiên tức thì (`NFR-02`), rate limit & token hash (`NFR-03/12`), upload `<= 5MB` (`NFR-07`), và **bắn request song song (`asyncio.gather`)** kiểm chứng `NFR-05`.
4. **Tầng 4 — System, E2E, NFR & UAT (`tests/e2e/` & `artifacts/`)**:
   - Chạy trọn vẹn **3 kịch bản đầu cuối `E2E-01`..`E2E-03`** (API + React UI), kiểm tra giao diện `390px` & `1366×768` (`NFR-06`), benchmark `NFR-04` (`100k` đơn / `1M` giao dịch kho), diễn tập backup/restore `NFR-09`, và đối chiếu bản ghi thực trong PostgreSQL (không chỉ chụp ảnh giao diện theo `SRS/08` Mục 1).

---

## 2. Ma trận Truy vết Yêu cầu Hai chiều (Traceability Matrix — 40 Stories)

| Phân hệ | Story | Ưu tiên | `BR` liên quan | `NFR` liên quan | `E2E` | `NEG` Controls | Tài liệu `ACTIVE` | Nhóm thực thể DB đích |
|---|---|---|---|---|---|---|---|---|
| **PUB** | `PUB-01` | Must | `BR-18` | `NFR-06`, `NFR-12` | `E2E-01`, `E2E-02` | `NEG-23` | `ORG-COM-001`, `GUIDE-PUB-001`, `FAQ-PUB-001` | `public_contents` |
| **PUB** | `PUB-02` | Must | `BR-01`, `BR-02` | `NFR-05`, `NFR-12` | `E2E-01`, `E2E-02` | `NEG-01` | `POL-PUB-001`, `POL-COM-001` | `service_requests` |
| **PUB** | `PUB-03` | Must | `BR-01` | `NFR-03`, `NFR-05` | `E2E-01`, `E2E-02` | `NEG-01` | `POL-PUB-001` | `service_requests` |
| **PUB** | `PUB-04` | Must | `BR-05`, `BR-18` | `NFR-03` | `E2E-01` | `NEG-02` | `POL-PUB-002`, `POL-COM-001` | `service_requests`, `service_orders`, `public_lookup_attempts` |
| **PUB** | `PUB-05` | Must | `BR-17` | `NFR-01`, `NFR-12` | — | `NEG-23` | `GUIDE-PUB-001`, `FAQ-PUB-001` | `public_contents`, `audit_logs` |
| **SAL** | `SAL-01` | Must | `BR-01`, `BR-16`, `BR-17` | `NFR-01`, `NFR-06` | `E2E-01` | `NEG-03` | `SOP-SAL-001` | `customers`, `audit_logs` |
| **SAL** | `SAL-02` | Must | `BR-01`, `BR-02`, `BR-17` | `NFR-03`, `NFR-06` | `E2E-01..03` | `NEG-02` | `SOP-SAL-001`, `TPL-SAL-002` | `service_requests`, `customers`, `audit_logs` |
| **SAL** | `SAL-03` | Must | `BR-17`, `BR-18` | `NFR-01` | `E2E-01` | `NEG-24` | `SOP-SAL-001`, `TPL-SAL-002` | `service_requests`, `request_interactions`, `audit_logs` |
| **SAL** | `SAL-04` | Must | `BR-03`, `BR-04` | `NFR-01`, `NFR-10` | `E2E-01..03` | `NEG-04` | `POL-SAL-001`, `TPL-SAL-001` | `quotes`, `quote_lines` |
| **SAL** | `SAL-05` | Must | `BR-03`, `BR-04`, `BR-17` | `NFR-01`, `NFR-07` | `E2E-01`, `E2E-02` | `NEG-04` | `POL-SAL-001`, `TPL-SAL-001` | `quotes`, `evidence_files`, `audit_logs` |
| **SAL** | `SAL-06` | Must | `BR-04`, `BR-05`, `BR-17` | `NFR-05` | `E2E-01..03` | `NEG-05` | `POL-SAL-001`, `SOP-SAL-001` | `quotes`, `service_requests`, `service_orders`, `transport_trips`/`rental_records`/`warehouse_lots` |
| **SAL** | `SAL-07` | Must | `BR-06`, `BR-17` | `NFR-01`, `NFR-06` | `E2E-01..03` | `NEG-24` | `POL-SAL-002`, `TPL-SAL-002` | `service_orders`, `audit_logs` |
| **SAL** | `SAL-08` | Must | `BR-13`, `BR-17` | `NFR-05`, `NFR-07` | `E2E-02` | `NEG-15`, `NEG-16` | `POL-SAL-002` | `surcharges`, `evidence_files`, `audit_logs` |
| **SAL** | `SAL-09` | Must | `BR-13`, `BR-15`, `BR-17` | `NFR-01` | — | `NEG-19` | `POL-SAL-002`, `SOP-SAL-001` | `service_orders`, `resource_bookings`, `audit_logs` |
| **TRN** | `TRN-01` | Must | `BR-08`, `BR-16`, `BR-17` | `NFR-01` | `E2E-01`, `E2E-02` | `NEG-07`, `NEG-08` | `SOP-TRN-001` | `vehicles`, `drivers`, `audit_logs` |
| **TRN** | `TRN-02` | Must | `BR-07`, `BR-08`, `BR-17` | `NFR-05`, `NFR-06` | `E2E-01`, `E2E-03` | `NEG-06`, `NEG-07`, `NEG-08` | `POL-TRN-001 v2.0`, `SOP-TRN-001` | `transport_trips`, `resource_bookings` |
| **TRN** | `TRN-03` | Must | `BR-08`, `BR-09`, `BR-18` | `NFR-01` | `E2E-01`, `E2E-03` | `NEG-06`, `NEG-09` | `POL-TRN-001 v2.0`, `TPL-TRN-001` | `transport_trips`, `service_orders`, `resource_bookings` |
| **TRN** | `TRN-04` | Must | `BR-06`, `BR-09`, `BR-17` | `NFR-05`, `NFR-07` | `E2E-01`, `E2E-03` | `NEG-09` | `POL-TRN-001 v2.0`, `TPL-TRN-001` | `transport_trips`, `evidence_files`, `resource_bookings` |
| **TRN** | `TRN-05` | Must | `BR-09`, `BR-17` | `NFR-01` | — | `NEG-10` | `POL-TRN-001 v2.0`, `TPL-TRN-001` | `trip_incidents`, `resource_bookings` |
| **RNT** | `RNT-01` | Must | `BR-07`, `BR-08`, `BR-17` | `NFR-05`, `NFR-06` | `E2E-02` | `NEG-06`, `NEG-07` | `POL-RNT-001`, `SOP-RNT-001` | `rental_records`, `resource_bookings` |
| **RNT** | `RNT-02` | Must | `BR-07`, `BR-08`, `BR-17` | `NFR-01` | `E2E-02` | `NEG-08` | `POL-RNT-001`, `SOP-RNT-001` | `rental_records`, `resource_bookings`, `audit_logs` |
| **RNT** | `RNT-03` | Must | `BR-09`, `BR-17` | `NFR-05`, `NFR-07` | `E2E-02` | `NEG-06`, `NEG-11` | `POL-RNT-001`, `TPL-RNT-001` | `rental_records`, `evidence_files`, `resource_bookings` |
| **RNT** | `RNT-04` | Must | `BR-09`, `BR-17` | `NFR-07` | `E2E-02` | `NEG-10`, `NEG-11` | `POL-RNT-001`, `TPL-RNT-001` | `rental_records`, `evidence_files`, `resource_bookings` |
| **RNT** | `RNT-05` | Must | `BR-06`, `BR-13` | `NFR-01` | `E2E-02` | `NEG-11` | `POL-RNT-001`, `SOP-RNT-001` | `rental_records`, `service_orders`, `surcharges` |
| **WHS** | `WHS-01` | Must | `BR-05`, `BR-10` | `NFR-01` | `E2E-03` | `NEG-14` | `POL-WHS-001`, `SOP-WHS-001 v1.1` | `warehouse_lots`, `lot_lines` |
| **WHS** | `WHS-02` | Must | `BR-10`, `BR-11`, `BR-17` | `NFR-05` | `E2E-03` | `NEG-12` | `POL-WHS-002`, `TPL-WHS-001` | `warehouse_documents`, `warehouse_document_lines` |
| **WHS** | `WHS-03` | Must | `BR-10`, `BR-11`, `BR-17` | `NFR-05` | `E2E-03` | `NEG-12` | `POL-WHS-002`, `TPL-WHS-001` | `warehouse_documents`, `warehouse_document_lines` |
| **WHS** | `WHS-04` | Must | `BR-10`, `BR-18` | `NFR-01`, `NFR-06` | `E2E-03` | `NEG-14` | `POL-WHS-001`, `SOP-WHS-001 v1.1` | `warehouse_documents`, `service_orders` |
| **WHS** | `WHS-05` | Must | `BR-12`, `BR-17` | `NFR-05` | — | `NEG-13` | `POL-WHS-002`, `TPL-WHS-001` | `warehouse_documents`, `warehouse_document_lines`, `audit_logs` |
| **WHS** | `WHS-06` | Must | `BR-06`, `BR-11`, `BR-17` | `NFR-01` | `E2E-03` | `NEG-15` | `POL-WHS-001`, `SOP-WHS-001 v1.1` | `warehouse_lots`, `service_orders`, `warehouse_documents` |
| **PAY** | `PAY-01` | Must | `BR-03`, `BR-06`, `BR-13` | `NFR-01` | `E2E-01..03` | `NEG-16` | `POL-PAY-001`, `SOP-PAY-001` | `service_orders`, `surcharges`, `payments` |
| **PAY** | `PAY-02` | Must | `BR-13`, `BR-14`, `BR-17` | `NFR-05` | `E2E-01..03` | `NEG-17` | `POL-PAY-001`, `TPL-PAY-001` | `payments`, `service_orders` |
| **PAY** | `PAY-03` | Must | `BR-06`, `BR-14`, `BR-17` | `NFR-05` | — | `NEG-18` | `SOP-PAY-001`, `TPL-PAY-001` | `payments`, `audit_logs` |
| **PAY** | `PAY-04` | Must | `BR-13`, `BR-17` | `NFR-06` | `E2E-01`, `E2E-02` | `NEG-20` | `POL-PAY-001`, `POL-ADM-002` | `service_orders`, `payments`, `audit_logs` |
| **ADM** | `ADM-01` | Must | `BR-17` | `NFR-01`, `NFR-02` | `E2E-01..03` | `NEG-22` | `POL-ADM-001` | `users`, `user_sessions` |
| **ADM** | `ADM-02` | Must | `BR-16`, `BR-17` | `NFR-01`, `NFR-02` | `E2E-01..03` | `NEG-21`, `NEG-22` | `POL-ADM-001` | `users`, `roles`, `user_roles`, `user_sessions`, `audit_logs` |
| **ADM** | `ADM-03` | Must | `BR-10`, `BR-16`, `BR-17` | `NFR-01` | — | `NEG-14` | `POL-COM-003 v1.1` | `master_categories`, `audit_logs` |
| **ADM** | `ADM-04` | Must | `BR-17`, `BR-18` | `NFR-01`, `NFR-08` | `E2E-01..03` | `NEG-21`, `NEG-24` | `SOP-ADM-001 v1.1`, `TPL-ADM-001` | `audit_logs` |
| **ADM** | `ADM-05` | Must | `BR-06`, `BR-10`, `BR-13` | `NFR-04`, `NFR-06` | `E2E-01..03` | `NEG-20` | `POL-ADM-002` | Tổng hợp đọc trên `service_orders`, `resource_bookings`, `warehouse_lots`, `payments` |
| **ADM** | `ADM-06` | Should | `BR-10`, `BR-13`, `BR-17`, `BR-18` | `NFR-01` | — | — | `POL-ADM-002` | Tổng hợp CSV theo quyền & bộ lọc + `audit_logs` |

---

## 3. Kịch bản Đầu cuối Bắt buộc (`E2E-01` .. `E2E-03`) & Ví dụ Đối chiếu

### 3.1. Ba luồng E2E (`08_Acceptance_and_Traceability.pdf` Mục 3)
1. **`E2E-01` — Vận tải từ website tới hoàn tất và thu tiền**:
   - Khách xem `PUB-01`, gửi nhu cầu `1.200 kg` (`PUB-02/03`) → `SAL` đối chiếu khách, phân công, ghi trao đổi (`SAL-01..03`) → Lập & phát hành báo giá `2.000.000 VND`, ghi chấp thuận sinh đơn (`SAL-04..06`) → `DSP` phân xe `2.000 kg` + tài xế rảnh (`TRN-01/02`) → Ghi nhận nhận hàng, vận chuyển, giao hàng có bằng chứng và hoàn tất (`TRN-03/04`) → `FIN` ghi thu `1.000.000` rồi `1.000.000` (`PAY-01/02`) → Khách tra cứu (`PUB-04`) không thấy ghi chú/số dư nội bộ; `MGR` đối chiếu dashboard & audit (`ADM-04/05`).
   - *Kỳ vọng*: 1 yêu cầu / 1 đơn / 1 chuyến; đơn hoàn tất trước khi `PAID` vẫn hợp lệ; cuối cùng `PAID`, còn phải thu `0`.
2. **`E2E-02` — Thuê xe và trả muộn có phát sinh**:
   - Tiếp nhận nhu cầu thuê, chốt báo giá `3.000.000 VND`, tạo đơn → `DSP` giữ xe không xung đột, bàn giao có odo/tình trạng/bằng chứng (`RNT-01..03`) → Thiết lập tình huống quá giờ hẹn trả nhưng chưa nhận lại, thử bàn giao cho việc tiếp theo (phải bị chặn `BR-09`) → Ghi nhận trả muộn, odo hợp lệ, đề nghị phụ phí `300.000 VND` (`RNT-04`, `SAL-08`) → `MGR` duyệt phụ phí, `DSP` hoàn tất, `FIN` thu đủ `3.300.000 VND` (`RNT-05`, `PAY-02`).
3. **`E2E-03` — Kho nhập nhiều lần, xuất từng phần và nối vận tải**:
   - Tạo đơn kho & lô `100` kiện dự kiến (`WHS-01`) → Nhập `60` kiện rồi `40` kiện bằng 2 phiếu `POSTED` (`WHS-02`, tồn `100`) → Lập nháp xuất `30` kiện (tồn vẫn `100`), xác nhận xuất (tồn `70`) (`WHS-03`) → Tạo đơn vận tải riêng cùng khách điểm lấy là kho, liên kết phiếu xuất `70` kiện (`WHS-04`) → Xác nhận xuất `70` (tồn `0`), `DSP` nhận hàng & thực hiện chuyến → `WHS` xác nhận kết thúc nhận thêm & chốt đơn kho (`WHS-06`), `FIN` thu riêng cho 2 đơn.

### 3.2. Ví dụ đối chiếu thanh toán bắt buộc (`06_Payment_Tracking.pdf`)
- Đơn giá chốt `2.000.000 VND` + phụ phí `APPROVED` `200.000` + phụ phí `PENDING` `100.000` → Phải thu = `2.200.000`.
- Thu `1.000.000` → Đã thu `1.000.000`, Còn lại `1.200.000` (`PARTIALLY_PAID`).
- Đảo khoản thu này → Đã thu `0`, Còn lại `2.200.000` (`UNPAID`).
- Từ chối phụ phí `100.000` → Tổng phải thu vẫn `2.200.000`; phụ phí `PENDING` phải được xử lý hết mới được hoàn tất dịch vụ.

---

## 4. Danh mục 24 Kịch bản Ngoại lệ & Kiểm soát (`NEG-01` .. `NEG-24`)

| Mã | Kịch bản kiểm thử & Kết quả kỳ vọng | Truy vết chính |
|---|---|---|
| **`NEG-01`** | Gửi form thiếu SĐT/sai ngày/số lượng âm: không tạo yêu cầu, báo lỗi đúng trường, giữ dữ liệu hợp lệ; gửi lặp cùng lần gửi hợp lệ chỉ tạo 1 hồ sơ. | `PUB-02/03`, `BR-02`, `NFR-05/12` |
| **`NEG-02`** | Tra cứu mã đúng + token sai hoặc đã thu hồi: trả thông báo chung, không lộ hồ sơ; thử quá `10 lần/15m` bị chặn tạm; token đúng không trả ghi chú nội bộ/số dư. | `PUB-04`, `SAL-02`, `BR-18`, `NFR-03` |
| **`NEG-03`** | Tạo hồ sơ khách hàng trùng SĐT thì cảnh báo, không tự gộp; khách `INACTIVE` bị chặn tạo đơn mới. | `SAL-01`, `BR-16` |
| **`NEG-04`** | Phát hành báo giá bản 2 làm bản 1 (`SUPERSEDED`) không thể chấp thuận; báo giá hết ngày hiệu lực (`EXPIRED`) không thể chấp thuận. | `SAL-04/05`, `BR-03/04` |
| **`NEG-05`** | Hai người cùng xác nhận 1 báo giá đồng thời: chỉ 1 đơn và 1 bản ghi vận hành; thử lỗi giữa chừng không lưu thành công một phần. | `SAL-06`, `BR-05`, `NFR-05` |
| **`NEG-06`** | Gán chuyến vào xe đã giữ cho thuê cùng giờ bị từ chối; lịch `08:00–10:00` và `10:00–12:00` liền nhau hợp lệ nhưng vẫn chặn bắt đầu việc sau nếu xe chưa trả thực tế. | `TRN-02/03`, `RNT-01/03`, `BR-07/09` |
| **`NEG-07`** | Xe thiếu tải, `MAINTENANCE` hoặc tài xế `INACTIVE` bị từ chối; hai lệnh cạnh tranh giữ cùng xe chỉ 1 thành công. | `TRN-01/02`, `RNT-01`, `BR-08`, `NFR-05` |
| **`NEG-08`** | Đổi xe/lịch mới xung đột thất bại phải giữ nguyên booking cũ; ngừng xe đang có lịch tương lai bắt buộc xử lý lịch trước. | `TRN-01/02`, `RNT-02`, `BR-08` |
| **`NEG-09`** | Ghi giao hàng trước nhận hàng, nhảy cóc trạng thái hoặc thiếu bằng chứng bị từ chối; giao không thành công giữ `IN_TRANSIT` & tạo sự cố. | `TRN-03/04/05` |
| **`NEG-10`** | Kéo dài chuyến trùng lịch tiếp theo cảnh báo các lịch liên quan, không ghi đè; xe đang thực hiện (`IN_USE`) chặn bắt đầu lượt sau. | `TRN-05`, `RNT-04`, `BR-09` |
| **`NEG-11`** | Kilomet trả nhỏ hơn kilomet giao hoặc thời gian trả trước bàn giao bị từ chối; trả muộn không tự sinh tiền phạt. | `RNT-03/04/05` |
| **`NEG-12`** | Hai phiếu cùng xuất `7` trong khi tồn `10` đồng thời: chỉ 1 được `POSTED`, phiếu kia giữ `DRAFT` và tồn còn `3`; xác nhận lại phiếu đã `POSTED` không trừ lần 2. | `WHS-02/03`, `BR-11`, `NFR-05` |
| **`NEG-13`** | Nhập `100`, xuất `80`, đề nghị điều chỉnh giảm nhập `30` bị chặn; hoàn lại `5` xuất sai được `MGR` duyệt làm tồn `20 → 25`; không điều chỉnh lặp hay vượt nguồn. | `WHS-05`, `BR-12` |
| **`NEG-14`** | Không gắn phiếu xuất với đơn vận tải khác khách; không sửa mã đơn vị dòng đã giao dịch; không cộng kiện với pallet thành tổng số lượng. | `WHS-01/04`, `ADM-03/05`, `BR-10` |
| **`NEG-15`** | Tồn về `0` nhưng còn phiếu `DRAFT`, điều chỉnh chờ duyệt hoặc phụ phí `PENDING` thì chặn đóng đơn; đóng xong chặn nhập/xuất/điều chỉnh thêm. | `WHS-06`, `SAL-08` |
| **`NEG-16`** | Phụ phí chưa duyệt không cộng tiền; duyệt lặp 2 lần chỉ cộng 1; chặn tạo phụ phí mới sau `COMPLETED`/`CANCELLED`. | `SAL-08`, `PAY-01`, `BR-13` |
| **`NEG-17`** | Thu lớn hơn số dư hoặc 2 lần thu cạnh tranh gây vượt thu bị từ chối; gửi lại cùng `idempotency_key` không ghi đôi. | `PAY-02`, `BR-13/14`, `NFR-05` |
| **`NEG-18`** | Đảo khoản thu 1 lần làm số dư đúng; đảo lần 2 bị từ chối; đơn `COMPLETED` không mở lại do đảo thu. | `PAY-03/04`, `BR-06/14` |
| **`NEG-19`** | `MGR` hủy đơn đã giữ xe nhưng chưa thực hiện/chưa thu: giải phóng lịch; đã nhận hàng/bàn giao/nhập kho hoặc còn khoản thu hiệu lực thì chặn hủy. | `SAL-09`, `BR-15` |
| **`NEG-20`** | Khoản còn thu đúng ngày đến hạn chưa quá hạn; qua ngày kế tiếp mới bật quá hạn; Dashboard đối chiếu khớp danh sách lọc, không đếm đôi nhiều dòng phí. | `PAY-04`, `ADM-05` |
| **`NEG-21`** | Truy cập API sai vai trò, sửa ID đối tượng để đọc/ghi trái quyền (IDOR) đều bị chặn; `ADM` đơn vai trò không có quyền thu tiền/xuất kho. | `ADM-02`, `NFR-01` |
| **`NEG-22`** | Khóa tài khoản, thu hồi vai trò, đặt lại mật khẩu làm phiên mất quyền ngay; chặn khóa tài khoản `ADM` hoạt động cuối cùng. | `ADM-01/02`, `NFR-02` |
| **`NEG-23`** | Nội dung `DRAFT`/`HIDDEN` không lộ công khai; input script XSS không thực thi; file sai định dạng hoặc quá `5 MB` bị chặn, tải file trái quyền bị chặn. | `PUB-01/05`, `NFR-07/12` |
| **`NEG-24`** | Xem `audit_logs` đổi giá/lịch/quyền/chứng từ; không cho sửa/xóa audit; 2 người sửa cùng hồ sơ không âm thầm ghi đè mất thay đổi trước. | `SAL-03/07`, `ADM-04`, `BR-17` |

---

## 5. Kỹ thuật Thiết kế Test Sớm (`SWT4`) & Bộ Dữ liệu UAT Tối thiểu

### 5.1. Áp dụng Kỹ thuật `SWT4`
- **State Transition Testing**: Bao phủ mọi cạnh hợp lệ và cạnh cấm của `ServiceRequest`, `Quote`, `ServiceOrder`, `TransportTrip`, `RentalRecord`, `WarehouseLot/Document`, `Payment`.
- **Boundary Value Analysis (BVA)**:
  - Upload file: `0 byte` (chặn), `5.242.880 bytes` (5 MB — cho phép), `5.242.881 bytes` (chặn).
  - Rate limit gửi form: lần thứ `5` trong 10 phút (cho phép), lần thứ `6` (HTTP `429`).
  - Rate limit tra cứu sai: lần thứ `10` trong 15 phút, lần thứ `11` (khóa tạm).
  - Lịch `[start, end)`: `[08:00, 10:00)` vs `[10:00, 12:00)` (hợp lệ), `[08:00, 10:01)` vs `[10:00, 12:00)` (xung đột).
  - Hiệu lực báo giá: `23:59:59` ngày hết hạn `Asia/Ho_Chi_Minh` (hợp lệ), `00:00:00` ngày kế tiếp (`EXPIRED`).
  - Ngày đến hạn thanh toán: `today == due_date` (chưa quá hạn), `today == due_date + 1 day` (quá hạn).
- **Decision Table**: Kiểm tra ma trận quyền 7 vai trò + tài khoản kiêm 2 vai trò (`ADM-02`, `NFR-01`).

### 5.2. Bộ Dữ liệu UAT & Tài khoản Tối thiểu (`data/seed/` — `SRS/08` Mục 2)

| Nhóm dữ liệu | Số lượng & Trạng thái bắt buộc khi viết Script Seed DB |
|---|---|
| **Tài khoản** | >= 1 tài khoản riêng cho mỗi role `SAL`, `DSP`, `WHS`, `FIN`, `MGR`, `ADM` + 1 tài khoản `LOCKED` + 1 tài khoản kiêm 2 vai trò. |
| **Khách hàng** | >= 5 khách (gồm cá nhân, doanh nghiệp, 1 hồ sơ `INACTIVE`, và 2 hồ sơ trùng thông tin liên hệ để test cảnh báo `NEG-03`). |
| **Xe / Tài xế** | >= 6 xe ở ít nhất 2 mức tải trọng (gồm `ACTIVE`, `MAINTENANCE`, `INACTIVE`); >= 4 tài xế (có 1 `INACTIVE`). |
| **Website / Yêu cầu** | CMS đủ 3 dịch vụ + bản `DRAFT`/`HIDDEN`; >= 12 yêu cầu (có dữ liệu thiếu, `CLOSED_LOST`, và yêu cầu đã `CONFIRMED`). |
| **Báo giá / Đơn** | >= 9 đơn (3 đơn/dịch vụ ở các trạng thái khác nhau); có báo giá nhiều phiên bản (`SUPERSEDED`), `EXPIRED` và `REJECTED`. |
| **Kho** | >= 3 lô (có lô 2 dòng khác đơn vị, nhập nhiều lần, xuất một phần, điều chỉnh và 1 lô tồn `0` chờ kết thúc). |
| **Thanh toán** | Có đơn `UNPAID`, `PARTIALLY_PAID`, `PAID`, quá hạn, khoản thu đã `REVERSED`, và đơn `COMPLETED` vẫn còn phải thu. |

### 5.3. Xác nhận 12 Yêu cầu Phi chức năng (`NFR-01` .. `NFR-12`)

| Nhóm `NFR` | Cách xác nhận trong lộ trình Software |
|---|---|
| `NFR-01`, `NFR-02`, `NFR-03` | `NEG-02/21/22`, test đăng nhập sai, idle timeout 30m, thu hồi phiên tức thì, token không lộ URL/log. |
| `NFR-04`, `NFR-05` | Benchmark `100k` đơn / `1M` giao dịch kho (`p95 <= 2s/3s`); bắn request cạnh tranh & gửi lặp `NEG-01/05/07/12/16/17/18`. |
| `NFR-06`, `NFR-07`, `NFR-12` | Viewport `390px` & `1366×768`, phân trang/lọc; `NEG-01/23` (file sai loại/`>5MB`, XSS script, rate limit `5 req/10m`). |
| `NFR-08`, `NFR-09`, `NFR-10`, `NFR-11` | Truy lỗi bằng `X-Correlation-ID` (`NEG-24`); diễn tập backup & restore DB + tệp (`NFR-09`); kiểm tra OpenAPI & không lộ stack trace (`NFR-10`); triển khai sạch trên môi trường tách biệt theo runbook & release tag (`NFR-11`). |

---

## 6. Cổng Verify Gate 1D (Điều kiện Mở khóa Thiết kế ERD & PostgreSQL)

- [x] **40/40 User Stories** đã được truy vết đủ tới `BR-01..18`, `NFR-01..12`, `E2E-01..03`, `NEG-01..24`, tài liệu `ACTIVE`, và bảng DB đích.
- [x] Toàn bộ **3 E2E**, **24 NEG**, kỹ thuật biên **`SWT4`**, và **bộ dữ liệu UAT tối thiểu** đã chốt làm đầu vào trực tiếp cho PostgreSQL Schema, Constraints & Seed Scripts.
- [x] **Sẵn sàng chuyển sang Thiết kế ERD & Database PostgreSQL** (`docs/02_Design_ERD_SDS/01_ERD_and_PostgreSQL_Schema.md`).
