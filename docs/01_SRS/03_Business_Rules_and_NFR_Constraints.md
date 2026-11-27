# Bước 3 — Quy tắc Nghiệp vụ (`BR-01..18`), Ràng buộc Dữ liệu & `NFR-01..12`

- **Dự án**: `MockProject_Group7` — Hệ thống Quản lý Vận tải, Cho thuê xe & Kho bãi Trung chuyển
- **Giai đoạn**: Phần 1 (Software Core) — Bước Lớn 3 (theo `00_Overall_SRS.pdf` Mục 3, 5, 6 & `1_SWR302`)
- **Mục tiêu**: Biến toàn bộ quy tắc nghiệp vụ (`BR`), quy ước kiểm tra dữ liệu và yêu cầu phi chức năng (`NFR`) thành **ràng buộc kỹ thuật cụ thể** cho PostgreSQL, Backend Python (`FastAPI`/`SQLAlchemy`) và Frontend (`React + TypeScript`) trước khi dựng ERD.

---

## 1. Giải mã 18 Quy tắc Nghiệp vụ (`BR-01` .. `BR-18`) thành Ràng buộc Kỹ thuật

| Mã | Nội dung tóm tắt (SRS 00) | Ràng buộc tại PostgreSQL (DB Level) | Ràng buộc tại Backend Python (Service / Pydantic) |
|---|---|---|---|
| **`BR-01`** | Mã yêu cầu, khách hàng, báo giá, đơn, chuyến, lô, chứng từ duy nhất, do hệ thống cấp, không sửa sau khi tạo; mã tra cứu không thay thế token. | `UNIQUE NOT NULL` trên cột `code` từng bảng; trigger/app chặn update `code`. | Generator sinh mã chuẩn (`REQ-...`, `CUS-...`, `QOT-...`, `ORD-...`, `TRP-...`, `RNT-...`, `LOT-...`, `DOC-...`); bỏ qua/từ chối mọi field `code` do client gửi khi update. |
| **`BR-02`** | 1 yêu cầu thuộc 1 loại dịch vụ (`TRANSPORT` / `RENTAL` / `WAREHOUSE`); trường bắt buộc phụ thuộc loại dịch vụ; đổi loại sau khi phát hành báo giá phải đóng yêu cầu cũ và tạo yêu cầu mới có liên kết. | `service_type` `NOT NULL`, `parent_request_id` (nullable FK tự tham chiếu) để lưu liên kết yêu cầu mới ↔ cũ. | Pydantic discriminated schema theo `service_type`; chặn `PATCH` đổi `service_type` nếu yêu cầu đã có báo giá `SENT/ACCEPTED/SUPERSEDED`. |
| **`BR-03`** | Dòng phí có `quantity > 0`, `unit_price >= 0`; ít nhất 1 dòng có thành tiền `> 0`; thành tiền dòng làm tròn đến đồng; tổng = tổng các dòng đã làm tròn; dùng VND, chưa tự tính thuế. | Lưu tiền bằng **`BIGINT`** (`line_total_vnd`, `total_amount_vnd`); `CHECK (quantity > 0 AND unit_price_vnd >= 0)`. | Dùng `Decimal` + `ROUND_HALF_UP` về `int` VND khi tính `qty * unit_price`; cấm dùng `float`; kiểm tra `sum(line_totals) > 0` ở validator. |
| **`BR-04`** | Mỗi yêu cầu chỉ có 1 phiên bản báo giá đang chờ (`SENT`); phát hành bản mới chuyển bản `SENT` cũ sang `SUPERSEDED`; chỉ `SENT` chưa quá `23:59:59` ngày hiệu lực (theo `Asia/Ho_Chi_Minh`) và chưa bị thay thế mới được `ACCEPTED`/`REJECTED`. | Partial Unique Index: `CREATE UNIQUE INDEX uq_one_sent_quote_per_req ON quotes (request_id) WHERE status = 'SENT'`. | Trong transaction phát hành: lock `request_id`, chuyển bản `SENT` hiện tại → `SUPERSEDED`, phát hành bản mới. Khi chấp thuận/từ chối: kiểm tra `status == 'SENT'` và `now_vn <= end_of_day(valid_until)`. |
| **`BR-05`** | 1 yêu cầu sinh tối đa 1 `ServiceOrder`; tạo lại cùng yêu cầu trả về đơn đã có; chấp thuận báo giá + tạo đơn phải atomic. | `request_id BIGINT UNIQUE NOT NULL` trên bảng `service_orders`. | `accept_quote_and_create_order` chạy trong 1 DB transaction duy nhất (`Quote=ACCEPTED` + `Request=CONFIRMED` + `ServiceOrder=CONFIRMED` + bản ghi vận hành); dùng `idempotency_key` + xử lý duplicate trả đơn đã có. |
| **`BR-06`** | Phân biệt hoàn thành vận hành (`COMPLETED`) và thanh toán (`PAID`). | Hai cột tách biệt hoàn toàn (`general_status` vs `payment_status`). | Hoàn tất vận hành không tự tạo giao dịch thu hay đổi `payment_status`; đảo khoản thu không mở lại `ServiceOrder.general_status = 'COMPLETED'`. |
| **`BR-07`** | Khoảng lịch `[start_at, end_at)` với `end_at > start_at`; chồng lịch nếu `start_A < end_B AND start_B < end_A`; vận tải & thuê xe kiểm tra trên cùng nguồn lịch; tài xế kiểm tra tương tự với vận tải. | `CHECK (end_at > start_at)`; bảng dùng chung `resource_bookings` có PostgreSQL `EXCLUDE USING gist` với `tstzrange(start_at, end_at, '[)')` cho `vehicle_id` và `driver_id` khi `status IN ('HELD', 'IN_USE')`. | Trước khi giữ/phân công/đổi lịch: lock xe/tài xế, truy vấn overlap trên `resource_bookings` (`HELD`/`IN_USE`). Lịch `08:00–10:00` và `10:00–12:00` hợp lệ (không chồng). |
| **`BR-08`** | Chỉ xe `ACTIVE`, đủ tải trọng khai báo (`payload_capacity_kg >= weight_kg`), không bị chặn bảo dưỡng/ngừng dùng mới được giữ/phân công; chỉ tài xế `ACTIVE` được phân công; an toàn khi thao tác đồng thời. | `vehicles.status`, `drivers.status`, `CHECK (payload_capacity_kg > 0)`. | Trong transaction phân công: `SELECT ... FOR UPDATE` trên `vehicles` & `drivers`, kiểm tra `status == 'ACTIVE'` và tải trọng; từ chối cả khi gửi trực tiếp ID qua API. |
| **`BR-09`** | Khi xe chưa thực sự trả/giải phóng hoặc chuyến chưa kết thúc (`IN_USE`), chặn bắt đầu chuyến/bàn giao thuê tiếp theo dù giờ kết thúc dự kiến đã qua; kéo dài lịch trùng tương lai chỉ cảnh báo `DSP`, không âm thầm ghi đè. | Trạng thái `IN_USE` trên `resource_bookings` chỉ kết thúc khi `released_at` thực tế được ghi nhận. | Khi `PICKED_UP` (`TRN-03`) hoặc `HANDED_OVER` (`RNT-03`): kiểm tra không có booking khác của xe/tài xế đang ở trạng thái `IN_USE`. Khi gia hạn lịch dự kiến: trả danh sách booking xung đột để điều phối tự xử lý. |
| **`BR-10`** | Mỗi dòng hàng trong lô dùng 1 đơn vị đếm cố định (kiện/thùng/pallet) và số lượng nguyên dương; không cộng/quy đổi khác đơn vị; khối lượng `kg` lưu riêng khi cần vận tải. | `unit_id` (FK cố định theo `lot_lines`), `CHECK (expected_qty > 0)` và `CHECK (qty > 0)` là `INTEGER`. | Sau khi dòng hàng đã phát sinh chứng từ kho (`POSTED`/`DRAFT`), cấm sửa `item_code` và `unit_id`. Dashboard/báo cáo nhóm tồn theo `(item, unit)`, cấm cộng gộp các đơn vị khác nhau. |
| **`BR-11`** | Tồn dòng hàng = `SUM(nhập POSTED) - SUM(xuất POSTED)` (tính cả điều chỉnh đã `POSTED`); `DRAFT` không đổi tồn; xuất phải chống tồn âm & ghi lặp; không sửa/xóa phiếu đã `POSTED`. | Bảng chứng từ `warehouse_documents` + `warehouse_document_lines` là sổ cái bất biến khi `status = 'POSTED'`; `idempotency_key` `UNIQUE`. | Khi `POST` phiếu xuất: `SELECT ... FOR UPDATE` trên `lot_lines`, tính lại tồn khả dụng hiện tại ngay trong transaction; nếu bất kỳ dòng nào thiếu tồn → rollback toàn bộ phiếu, giữ nguyên `DRAFT`. |
| **`BR-12`** | Sửa sai phiếu `POSTED` bằng phiếu điều chỉnh liên kết `source_doc_id`, có lý do và `MGR` duyệt; điều chỉnh giảm nhập không làm tồn âm; không điều chỉnh vượt số lượng còn điều chỉnh được của phiếu nguồn. | `source_doc_id` (FK tự tham chiếu), `approved_by`, `approved_at`, `reason`. | Khi `WHS` đề nghị và khi `MGR` duyệt: khóa dòng nguồn + `lot_lines`, tính `adjustable_remaining = source_qty - SUM(approved_adjustments)`, kiểm tra đủ tồn trước khi `POSTED`. |
| **`BR-13`** | Đơn chưa hủy: `total_receivable = quoted_total + SUM(surcharge APPROVED)`; `total_paid = SUM(RECEIPT POSTED) - SUM(REVERSAL POSTED)`; `remaining = total_receivable - total_paid`; cấm thu vượt `remaining` & số dư âm; đơn hủy có phải thu hiệu lực = 0. | Lưu số tiền `BIGINT CHECK (amount_vnd > 0)` trên `surcharges` và `payments`. | Khi ghi thu tiền: `SELECT ... FOR UPDATE` trên `service_orders`, tính lại `remaining` tại thời điểm xác nhận; nếu `amount > remaining` hoặc `general_status == 'CANCELLED'` → từ chối (`409`/`422`). |
| **`BR-14`** | Thu tiền dương gắn đơn; khoản thu `POSTED` không sửa/xóa; `FIN` đảo toàn bộ 1 khoản thu sai với lý do, tối đa 1 lần/khoản; không phát lệnh hoàn tiền ngân hàng, không quản lý tạm ứng/đặt cọc. | `reversed_payment_id BIGINT UNIQUE` trên bảng `payments` (bảo đảm tối đa 1 bản ghi đảo cho mỗi khoản thu gốc); `CHECK (tx_type IN ('RECEIPT', 'REVERSAL'))`. | Chỉ đảo khoản có `tx_type == 'RECEIPT'` và chưa từng có bản ghi trỏ tới nó; cấm đảo bản ghi `REVERSAL`. |
| **`BR-15`** | Chỉ hủy đơn chưa bắt đầu thực hiện (`detail_status IN ('UNASSIGNED','ASSIGNED','RESERVED','WAITING_RECEIPT')` và chưa có nhập kho `POSTED`) và chưa có khoản thu hiệu lực (`total_paid == 0` và không có `RECEIPT` hiệu lực) và không còn phụ phí `PENDING/APPROVED`; hủy thì giải phóng lịch cùng lúc. | Transaction cập nhật đồng thời `service_orders.general_status = 'CANCELLED'`, bản ghi vận hành `= 'CANCELLED'`, `resource_bookings.status = 'RELEASED'`. | Kiểm tra đủ điều kiện `BR-15` ở Backend trước khi cho `MGR` chốt hủy kèm `reason`; từ chối ngay nếu đã nhận hàng/bàn giao/nhập kho hoặc còn tiền thu hiệu lực. |
| **`BR-16`** | Không hard delete đối tượng đã được tham chiếu bởi giao dịch (`Customer`, `Vehicle`, `Driver`, `User`, `MasterCategory`). | `status` (`ACTIVE`/`INACTIVE`) + `RESTRICT` trên mọi khóa ngoại giao dịch (không dùng `ON DELETE CASCADE` cho dữ liệu nghiệp vụ). | Chỉ cung cấp API `deactivate` / `archive` (soft deactivation); mọi endpoint `DELETE` nghiệp vụ bị loại bỏ hoặc chỉ cho phép hủy bản `DRAFT` chưa xác nhận. |
| **`BR-17`** | Mọi thay đổi trạng thái, giá trị, phân công, chứng từ, quyền đều lưu người thực hiện, thời gian, đối tượng, hành động, trước/sau, lý do (nếu hủy/điều chỉnh/đảo). | Bảng `audit_logs` append-only (không cấp API `UPDATE`/`DELETE`). | Mọi service method thay đổi trạng thái/giá trị/quyền đều gọi `AuditService.record(...)` trong **cùng transaction** với nghiệp vụ chính. |
| **`BR-18`** | Tra cứu công khai (`GST`) chỉ xem trạng thái công khai, mốc thời gian, loại dịch vụ, thông tin hỗ trợ; không lộ ghi chú nội bộ, giá vốn, số dư, dữ liệu khách khác, thông tin tài xế riêng tư hoặc tài liệu bàn giao nội bộ. | Tách trường nội bộ (`internal_notes`, `driver_phone`, `total_amount_vnd`, `remaining`) khỏi query/DTO công khai. | Dùng **dedicated Pydantic Response Schema** (`PublicTrackingResponse`) chỉ chứa whitelist trường công khai; tuyệt đối không trả object ORM thô ra API. |

---

## 2. Quy ước Kiểm tra Đầu vào & Chuẩn Dữ liệu (SRS 00 Mục 5)

### 2.1. Quy tắc validation chung (Pydantic Base Validators)
1. **Chuỗi văn bản**: tự động `.strip()` khoảng trắng đầu/cuối; tên `1–200` ký tự; ghi chú tối đa `2.000` ký tự. Lỗi validation chuẩn hóa dạng `{ field, message }` để Frontend hiển thị đúng trường lỗi và **giữ nguyên dữ liệu hợp lệ đã nhập**.
2. **Điện thoại & Email**: SĐT bắt buộc ở hồ sơ/yêu cầu, chuẩn hóa cho phép dấu `+` đầu và `8–15` chữ số (`^(\+)?[0-9]{8,15}$` sau chuẩn hóa khoảng trắng/gạch nối); email tùy chọn nhưng nếu có phải hợp lệ (`EmailStr`). Khớp SĐT chỉ cảnh báo trùng, **không** tự gộp khách hàng.
3. **Biển số xe**: chuẩn hóa viết hoa, loại bỏ khoảng trắng và dấu phân cách (`-`, `.`) lưu vào `plate_normalized` (`UNIQUE`) để chống nhập trùng dưới các định dạng khác nhau (`TRN-01`).
4. **Mốc thời gian (`Asia/Ho_Chi_Minh`)**:
   - Thời điểm dự kiến khi tạo mới: `>= now()`.
   - Thời điểm thực tế do nhân viên nhập (`occurred_at`): `<= now()` và `>= previous_actual_milestone`. Cho phép ghi nhận muộn bằng cách lưu tách biệt `occurred_at` (thực tế) và `recorded_at` (giờ hệ thống khi nhập).
5. **Số học & Tiền tệ**:
   - `weight_kg > 0` (chỉ số dương); số lượng kho nguyên dương `int > 0`; `odo >= 0` và `odo_return >= odo_handover`.
   - Tiền tệ VND lưu `int` / `BIGINT`, không dùng dấu phẩy động.
6. **Chống ghi đè đồng thời (Optimistic Locking)**: Các đối tượng cập nhật chung (`Customer`, `ServiceRequest`, `Quote`, `ServiceOrder`) mang cột `version INTEGER NOT NULL DEFAULT 1`. Request sửa gửi kèm `expected_version`; nếu DB `version != expected_version` → trả `409 Conflict` yêu cầu tải lại/giải quyết xung đột.

### 2.2. Ánh xạ 11 Nhóm Đối tượng Dữ liệu (Đầu vào trực tiếp cho Bước thiết kế ERD)

| # | Nhóm đối tượng (SRS 00 Mục 5) | Bảng DB dự kiến | Trường khóa/bất biến & Ràng buộc chính từ `BR`/`NFR` |
|---|---|---|---|
| 1 | `Customer` | `customers` | `code` UNIQUE, `phone_normalized` (indexed để cảnh báo trùng), `status`, `version` |
| 2 | `ServiceRequest` | `service_requests`, `request_interactions` | `code` UNIQUE, `service_type`, `source`, `raw_payload` JSONB (bất biến), `lookup_token_hash` (128-bit hash), `idempotency_key` UNIQUE, `version` |
| 3 | `Quote / QuoteLine` | `quotes`, `quote_lines` | `code` UNIQUE, `version_no`, partial unique `status='SENT'` per request (`BR-04`), `valid_until`, `total_amount_vnd BIGINT` |
| 4 | `ServiceOrder` | `service_orders`, `surcharges` | `code` UNIQUE, `request_id` **UNIQUE** (`BR-05`), `quote_id`, `snapshot_json` JSONB, `general_status`, `payment_due_date`, `version` |
| 5 | `Vehicle / Driver` | `vehicles`, `drivers` | `vehicles.plate_normalized` UNIQUE, `payload_capacity_kg > 0`, `drivers.code` UNIQUE, `status` (`BR-08/16`) |
| 6 | `ResourceBooking` | `resource_bookings` | `vehicle_id`, `driver_id` (nullable cho thuê xe), `source_type`, `source_id`, `[start_at, end_at)` GIST EXCLUDE (`BR-07/08/09`) |
| 7 | `TransportTrip` | `transport_trips`, `trip_incidents` | `order_id` UNIQUE, `detail_status`, `weight_kg > 0`, `actual_pickup_at`, `actual_delivery_at`, `released_at`, `has_incident` |
| 8 | `RentalRecord` | `rental_records` | `order_id` UNIQUE, `detail_status`, `handover_at`, `handover_odo`, `return_at`, `return_odo`, `handover_report`, `return_report` |
| 9 | `WarehouseLot / LotLine` | `warehouse_lots`, `lot_lines` | `lot_code` UNIQUE, `order_id` UNIQUE, `unit_id` (khóa cứng sau giao dịch `BR-10`), `expected_qty > 0` |
| 10 | `WarehouseDocument` | `warehouse_documents`, `warehouse_document_lines`, `evidence_files` | `doc_code` UNIQUE, `doc_type`, `status`, `source_doc_id` (điều chỉnh `BR-12`), `linked_transport_order_id`, `idempotency_key` UNIQUE (`BR-11`) |
| 11 | `Payment / Charge` & `Content / User / Audit` | `payments`, `surcharges`, `public_contents`, `users`, `roles`, `user_roles`, `user_sessions`, `master_categories`, `audit_logs` | `payments.reversed_payment_id` UNIQUE (`BR-14`), `bank_ref` unique per order when `BANK_TRANSFER`, `audit_logs` append-only (`BR-17`) |

---

## 3. Ánh xạ 12 Yêu cầu Phi chức năng (`NFR-01` .. `NFR-12`) vào Kiến trúc Software

| Mã | Chỉ tiêu nghiệm thu (SRS 00 Mục 6) | Giải pháp kỹ thuật bắt buộc (PostgreSQL + FastAPI + React/TS) |
|---|---|---|
| **`NFR-01`** | Mọi API nội bộ yêu cầu đăng nhập & đúng quyền; chống truy cập chéo theo ID (IDOR). | Dependency `get_current_active_user` + `require_roles(...)` + kiểm tra scope đối tượng ở Service layer; trả `401`/`403`. |
| **`NFR-02`** | Băm mật khẩu chuẩn; không lộ secret; đăng xuất/khóa user vô hiệu phiên ngay. | `argon2-cffi` (Argon2id) cho mật khẩu; secret chỉ qua `.env`; bảng `user_sessions` kiểm tra `revoked_at IS NULL` & `user.status == 'ACTIVE'` trên từng request. |
| **`NFR-03`** | Tra cứu công khai: mã + token `>= 128 bit` lưu dạng băm; không lộ URL/log; thu hồi/cấp lại bởi `SAL`; khóa sau `10 lần sai/IP/15m`. | `secrets.token_urlsafe(24)` (192-bit), lưu `HMAC-SHA256(token, TOKEN_HASH_PEPPER)` vào DB; gửi qua `POST /api/public/tracking` body (không query param); rate limit theo IP trong DB/cache. |
| **`NFR-04`** | `50` phiên nội bộ + `200` công khai đồng thời; `100.000` đơn, `1.000.000` giao dịch kho, `30` xe; `p95 <= 2s` (đọc), `<= 3s` (ghi) trong `>= 30 phút`. | Composite index trên `(status, created_at)`, `(order_id, tx_type)`, `(lot_line_id, doc_status)`, `(vehicle_id, start_at, end_at)`; keyset/offset pagination hợp lý; connection pool SQLAlchemy (`pool_size`, `max_overflow`). |
| **`NFR-05`** | Nhất quán khi gửi lặp & cạnh tranh (xác nhận báo giá, giữ lịch, nhập/xuất, thu/đảo tiền). | `idempotency_key` + DB transaction `READ COMMITTED`/`SERIALIZABLE` kết hợp `SELECT ... FOR UPDATE` + PostgreSQL `UNIQUE`/`EXCLUDE` constraints. |
| **`NFR-06`** | Phân trang, lọc, tìm theo mã; UI `1366×768` (nội bộ) và `390px` (công khai) không tràn ngang/che nút. | API danh sách chuẩn hóa `?page=&page_size=&search=&status=`; Frontend dùng CSS responsive/grid kiểm thử tại viewport `390×844` và `1366×768`. |
| **`NFR-07`** | Đính kèm chỉ nhận `PDF/JPG/PNG`, `<= 5 MB/tệp`; kiểm tra ở backend, lưu tên an toàn, không thực thi; tải file đúng quyền. | Kiểm tra `Content-Length <= 5*1024*1024` + magic bytes (`%PDF`, `\xFF\xD8\xFF`, `\x89PNG`); lưu tên UUID không đuôi thực thi ngoài web root; tải qua API có RBAC (`Content-Disposition: attachment`). |
| **`NFR-08`** | Log kỹ thuật có `correlation_id`; audit đọc theo đối tượng/người/thời gian; không log password/token/PII thừa. | Middleware gắn `X-Correlation-ID` (UUID4) vào mọi log & error response; log formatter mask các trường `password`, `token`, `lookup_token`, `secret`. |
| **`NFR-09`** | Backup DB + tệp hằng ngày; `RPO <= 24h`, `RTO <= 8h`; kiểm thử restore trước go-live. | Script `pg_dump -Fc` + đồng bộ `data/uploads/` hằng ngày kèm runbook khôi phục & đối chiếu số dư/tồn/lịch. |
| **`NFR-10`** | UI không truy cập thẳng DB; có OpenAPI contract; validation backend; không lộ stack trace. | React chỉ gọi FastAPI qua REST JSON; Swagger/OpenAPI tự sinh tại `/openapi.json` (tắt ở prod nếu cần nhưng xuất tài liệu); global exception handler trả thông báo an toàn + `correlation_id`. |
| **`NFR-11`** | Cấu hình theo môi trường, secret ngoài source, Alembic migration có phiên bản, health check, runbook, rollback, HTTPS & release tag. | `.env` ngoài Git, Alembic migrations, `GET /health` kiểm tra kết nối PostgreSQL, tài liệu triển khai sạch tại `docs/05_Release_Manuals/`. |
| **`NFR-12`** | Chống XSS trong input & CMS; giới hạn gửi yêu cầu công khai `5 yêu cầu/IP/10 phút`. | Sanitize HTML (whitelist tags cho CMS, escape toàn bộ text user nhập; React auto-escape); rate-limit middleware trên `POST /api/public/requests` trả HTTP `429` kèm `Retry-After`. |

---

## 4. Checklist Verify Gate 1C

- [x] Đủ **18/18 Business Rules (`BR-01`..`BR-18`)** được dịch thành ràng buộc DB + Backend rõ ràng.
- [x] Đủ **12/12 NFRs (`NFR-01`..`NFR-12`)** được ánh xạ vào kiến trúc PostgreSQL + FastAPI + React/TS.
- [x] Đủ **11 nhóm đối tượng dữ liệu** (SRS 00 Mục 5) kèm khóa duy nhất, kiểu `BIGINT` VND, `version` locking và `idempotency_key`.
- [x] Sẵn sàng lập **Ma trận Truy vết & Test Plan sớm (Bước Lớn 4)** trước khi vẽ ERD.
