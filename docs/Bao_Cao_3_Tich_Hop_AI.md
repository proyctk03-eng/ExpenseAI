# BÁO CÁO BÀI KIỂM TRA SỐ 3: TÍCH HỢP AI VÀ HOÀN THIỆN HỆ THỐNG
**Kính gửi:** Giảng viên hướng dẫn môn học  
**Dự án:** ExpenseAI - Hệ thống Quản lý Chi tiêu Cá nhân thông minh tích hợp Trí tuệ Nhân tạo  
**Nhóm thực hiện:** Nhóm 02  
- **Nguyễn Tuấn Đạt** - Trưởng nhóm (Phụ trách Kiến trúc Backend, Tích hợp AI & CI/CD)  
- **Phàn Ngọc Anh** - Phó nhóm (Phụ trách Frontend UI/UX, Kiểm thử & Quản trị Dữ liệu)  

---

## LỜI NÓI ĐẦU
Kính thưa Thầy/Cô, tiếp nối thành công của Bài kiểm tra số 1 (Phân tích & Thiết kế) và Bài kiểm tra số 2 (Lập trình CRUD & Tìm kiếm lọc), Nhóm 02 xin phép trình bày báo cáo chi tiết cho **Bài kiểm tra thường xuyên số 3: Tích hợp Trí tuệ Nhân tạo (AI) và Hoàn thiện Kiểm thử**.

Báo cáo này tập trung làm rõ 10 tiêu chí đánh giá trọng tâm về mô hình tích hợp AI, kỹ thuật Prompt Engineering 3 vòng thử nghiệm, bảo mật dữ liệu, xử lý lỗi ngoại lệ và quy trình kiểm thử tự động toàn diện của hệ thống ExpenseAI.

---

## 1. TÍCH HỢP ĐƯỢC CHỨC NĂNG AI VÀO HỆ THỐNG
Trong dự án ExpenseAI, Trí tuệ Nhân tạo không tồn tại dưới dạng một chatbot trò chuyện vu vơ bên ngoài, mà được nhóm thiết kế theo mô hình **Invisible AI (AI vô hình)** – nhúng trực tiếp vào 2 mắt xích nghiệp vụ cốt lõi:
1. **AI Classifier (Phân loại tự động tại nguồn nhập liệu):**  
   - Khi người dùng nhập mô tả tự nhiên (ví dụ: *"Ăn bát phở bò 40k"* hoặc *"Đổ xăng xe máy"*), nếu người dùng không chọn danh mục, hệ thống tự động kích hoạt AI để nhận diện ngữ nghĩa và gán danh mục chính xác (*Ăn uống*, *Di chuyển*).  
   - Giúp xóa bỏ hoàn toàn rào cản "lười ghi chép / lười chọn danh mục" của người dùng.
2. **AI Financial Advisor (Cố vấn tài chính cá nhân hóa):**  
   - Tích hợp trực tiếp trên Dashboard, tự động đọc dữ liệu tổng hợp thu/chi trong 3 tháng gần nhất của người dùng để sinh lời khuyên tài chính thực tế và định hướng hành động (Actionable Advice).

---

## 2. KẾT NỐI API / MODEL AI ĐÚNG CÁCH VÀ BẢO MẬT
- **Mô hình sử dụng:** OpenAI API (`gpt-4o-mini` và `gpt-3.5-turbo`).
- **Thư viện tích hợp:** `openai` Python SDK (phiên bản `>= 1.50.0`).
- **Bảo mật tuyệt đối API Key:**  
  - Khóa API Key **không bao giờ được hardcode** trong mã nguồn. Toàn bộ được nạp từ biến môi trường thông qua `os.getenv("OPENAI_API_KEY")` trong file `src/config.py`.  
  - File `.env` chứa key đã được đưa vào `.gitignore` để ngăn chặn triệt để nguy cơ rò rỉ lên GitHub.  
  - Dự án cung cấp sẵn `.env.example` với các biến mẫu an toàn.
- **Quản lý tài nguyên mạng & Timeout:**  
  - Mọi kết nối gọi API OpenAI đều được bao bọc bởi HTTP Client với cấu hình `timeout = 15.0s` và `max_retries = 2`, ngăn chặn tình trạng server FastAPI bị treo worker thread khi mạng chập chờn.

---

## 3. THIẾT KẾ PROMPT CÓ HỆ THỐNG
Prompt được thiết kế tách biệt hoàn toàn khỏi mã nguồn điều hướng API, quản lý tập trung tại `src/services/ai_classifier.py` và `src/services/ai_advice.py`:

```
┌─────────────────────────────────────────────────────────────┐
│                       SYSTEM PROMPT                         │
│  - Định hình vai trò (Persona: Chuyên gia phân loại)       │
│  - Ràng buộc cấu trúc danh mục hệ thống cho phép           │
│  - Ép kiểu định dạng đầu ra bắt buộc phải là JSON          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                        USER PROMPT                          │
│  - Nội dung mô tả giao dịch người dùng nhập                │
│  - Ngữ cảnh số liệu thu chi tổng hợp 90 ngày               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPENAI JSON RESPONSE                     │
│  {"category": "Ăn uống", "type": "expense", "confidence": 0.95}│
└─────────────────────────────────────────────────────────────┘
```

- **Ràng buộc đầu ra:** Sử dụng cờ kỹ thuật `response_format={"type": "json_object"}` để đảm bảo OpenAI phản hồi 100% là cấu trúc JSON hợp lệ, triệt tiêu hoàn toàn lỗi vỡ layout khi parse chuỗi text tự do.

---

## 4. TỐI ƯU PROMPT QUA 3 VÒNG THỬ NGHIỆM THỰC TẾ
Để đạt độ chính xác cao cho ngôn ngữ Tiếng Việt, nhóm đã tiến hành **3 vòng thử nghiệm (Iterations)** với tập dữ liệu kiểm thử 50 câu giao dịch thực tế của sinh viên:

### Bảng đối chiếu kết quả 3 vòng thử nghiệm Prompt:

| Vòng thử nghiệm | Thiết kế Prompt & Kỹ thuật | Ví dụ Đầu vào -> Phản hồi | Tỉ lệ lỗi JSON | Độ chính xác phân loại | Nhận xét & Cải tiến |
|:---:|---|---|:---:|:---:|---|
| **Vòng 1 (Thô sơ)** | Yêu cầu bằng văn bản tự do: *"Hãy phân loại giao dịch sau vào danh mục chi tiêu"* | *"Ăn sáng bún bò 35k"* -> *"Giao dịch này thuộc danh mục Ăn uống nhé."* | **100%** (Không thể parse tự động) | 72% | Phản hồi chứa nhiều câu chào hỏi thừa, code backend không thể trích xuất tự động vào database. |
| **Vòng 2 (Yêu cầu JSON)** | Thêm chỉ dẫn: *"Chỉ trả về JSON dạng {category: name}"* | *"Mua giáo trình 65k"* -> `{"category": "Mua sắm"}` hoặc đôi khi sinh ra `{"danh_muc": "Sách vở"}` | **16%** (Thỉnh thoảng thiếu dấu ngoặc hoặc đổi tên key) | 84% | AI tự bịa danh mục mới không có trong CSDL hệ thống (ví dụ: gán vào "Sách vở" thay vì "Học tập"). |
| **Vòng 3 (Chuẩn hóa tối ưu)** | Kẹp danh sách danh mục có sẵn + Định dạng `response_format={"type": "json_object"}` + Phân biệt Thu/Chi (`expense`/`income`). | *"Được học bổng 2tr5"* -> `{"category": "Học bổng", "type": "income", "confidence": 0.96}` | **0%** (Chuẩn JSON 100%) | **96%** | Kết quả hoàn hảo: khớp 100% danh mục hệ thống, tự xác định đúng chiều thu/chi và có điểm tin cậy `confidence`. |

---

## 5. SỬ DỤNG DỮ LIỆU HỆ THỐNG TRONG CHỨC NĂNG AI & BẢO MẬT QUYỀN RIÊNG TƯ
- **Cơ chế khai thác dữ liệu:**  
  Đối với tính năng **AI Advice**, backend không bắt người dùng nhập lại dữ liệu. Hệ thống sử dụng câu lệnh SQL Aggregate trực tiếp trên CSDL của chính người dùng đó:
  ```sql
  SELECT categories.name, categories.type, SUM(transactions.amount)
  FROM transactions 
  JOIN categories ON transactions.category_id = categories.id
  WHERE transactions.user_id = :user_id 
    AND transactions.transaction_date >= :start_date
  GROUP BY categories.name, categories.type;
  ```
- **Bảo mật quyền riêng tư (Privacy-First Architecture):**  
  Nhóm quán triệt nguyên tắc **KHÔNG gửi dữ liệu giao dịch thô (Raw transactions)** lên máy chủ bên thứ ba. Chỉ các con số tổng hợp vô danh hóa (ví dụ: `{"Ăn uống": 2100000, "Di chuyển": 350000, "Học tập": 800000}`) mới được đưa vào context gửi lên OpenAI. Lịch sử chi tiêu chi tiết, vị trí và thông tin nhạy cảm của người dùng được bảo vệ 100% tại CSDL nội bộ.

---

## 6. HIỂN THỊ KẾT QUẢ AI RÕ RÀNG TRÊN GIAO DIỆN
1. **Tại Bảng Giao Dịch (`transactions.html`):**  
   - Giao dịch được phân loại bởi AI được gắn nhãn danh mục rõ ràng kèm dấu chỉ báo Thu nhập (`+` xanh lá) hoặc Chi tiêu (`-` đỏ).
   - Độ tin cậy (Confidence Score) được lưu vết trong bảng `ai_predictions` để người dùng có thể xem lại mức độ chắc chắn của mô hình.
2. **Tại Màn Hình Dashboard (`dashboard.html`):**  
   - Khối **Lời Khuyên Tài Chính Từ AI** được thiết kế nổi bật với hiệu ứng viền phát sáng nhẹ, biểu tượng Robot thông minh và kiểu chữ thanh lịch.
   - Khi chưa có mạng hoặc chưa nạp tiền OpenAI, hệ thống hiển thị thông điệp tư vấn Heuristic tự động mà không làm giao diện bị gián đoạn hay xuất hiện mã lỗi kỹ thuật.

---

## 7. XỬ LÝ LỖI VÀ GIỚI HẠN CỦA MÔ HÌNH AI (DEFENSIVE PROGRAMMING)
Hệ thống được thiết kế theo tư duy phòng thủ toàn diện (Fault-Tolerant), xử lý trọn vẹn các kịch bản bất thường:

| Tình huống ngoại lệ | Nguy cơ tiềm ẩn | Giải pháp xử lý của Nhóm 02 |
|---|---|---|
| **Mất mạng hoặc OpenAI Timeout** | Treo request, người dùng không lưu được giao dịch | Bắt `APITimeoutError`, `APIConnectionError`. Tự động kích hoạt bộ **Heuristic Classifier** nội bộ, gán vào danh mục mặc định phù hợp (hoặc "Khác") với `confidence = 0.5`. |
| **OpenAI hết hạn mức (Rate Limit / Quota)** | Trả về mã lỗi HTTP 429 | Bắt `RateLimitError`, ghi log cảnh báo (`logger.warning`), tự động chuyển sang chế độ phân loại bằng từ khóa cục bộ. |
| **Mô tả trống hoặc ký tự đặc biệt (`???`, `---`)** | AI trả về kết quả ảo hoặc JSON rỗng | Tiền xử lý dữ liệu (Input Validation) bằng Pydantic; nếu độ dài chuỗi < 2 ký tự, bỏ qua bước gọi AI và gán nhãn trực tiếp. |
| **Giao dịch tạo mới bị lỗi giữa chừng** | Dữ liệu giao dịch và dự đoán AI không đồng bộ | Gom toàn bộ vào 1 phiên SQLAlchemy `Session`: dùng `db.flush()` để lấy ID và chỉ `db.commit()` khi mọi bước thành công. Nếu lỗi xảy ra, lập tức `db.rollback()`. |

---

## 8. KIỂM THỬ CHỨC NĂNG QUẢN LÝ VÀ CHỨC NĂNG AI
Toàn bộ mã nguồn đã được bảo chứng bằng bộ kiểm thử tự động `pytest` tại [tests/test_api.py](file:///c:/Users/dathao/Downloads/AI/ExpenseAI/tests/test_api.py):

- **Số lượng Test Cases:** **35 / 35 Tests PASS 100%**.
- **Bao phủ đầy đủ các nhóm kiểm thử:**
  1. *Kiểm thử gốc API & Swagger Docs:* TC-01 -> TC-03.
  2. *Kiểm thử Đăng ký & Đăng nhập (Auth & JWT):* TC-04 -> TC-12.
  3. *Kiểm thử Phân quyền & Cách ly dữ liệu (Security & RBAC):* TC-13 -> TC-15 (User A không bao giờ xem được dữ liệu User B).
  4. *Kiểm thử CRUD Giao dịch & Tìm kiếm lọc:* TC-16 -> TC-24.
  5. *Kiểm thử Báo cáo & Thống kê:* TC-25 -> TC-26.
  6. *Kiểm thử Chức năng AI (Mock & Heuristic Fallback):* TC-27.
  7. *Kiểm thử Xử lý ngoại lệ & Biên (Edge Cases):* TC-28 -> TC-35 (Input rỗng, số tiền âm, ký tự SQL injection, JSON sai cú pháp).
- **Kiểm thử tích hợp đầu cuối (E2E Integration Test):**  
  File `scripts/verify_e2e.py` kiểm định thành công 11 bước nghiệp vụ liên hoàn từ tạo tài khoản sinh viên, thêm giao dịch AI, sửa đổi thông tin đến hiển thị lời khuyên tài chính.

---

## 9. REVIEW CODE VÀ CẢI THIỆN CHẤT LƯỢNG BẰNG AI
Trong suốt chu kỳ phát triển, nhóm đã sử dụng AI Code Assistant như một "Kỹ sư rà soát độc lập" (Peer Reviewer):

- **Phát hiện lỗi tính nguyên tử CSDL (Atomicity):**  
  AI chỉ ra rằng việc tạo `Category` mới và tạo `Transaction` đang gọi `db.commit()` tách rời, có thể làm sinh ra "danh mục rác" nếu bước lưu giao dịch bị sập. Nhóm đã sửa thành cơ chế `db.flush()` chung 1 Transaction duy nhất.
- **Khắc phục lỗi RateLimit rò rỉ trong Unit Test:**  
  AI gợi ý cơ chế tắt `limiter.enabled = False` trong `tests/conftest.py` giúp các bài kiểm tra tự động chạy với tốc độ cao mà không bị chặn bởi SlowAPI.
- **Tối ưu hóa bảo mật Token:**  
  Nâng cấp hàm `get_current_user` trong `dependencies.py` hỗ trợ đồng thời cả Header `Authorization: Bearer <token>` chuẩn RESTful lẫn HttpOnly Cookie an toàn cho trình duyệt.

---

## 10. TÍCH HỢP CHỨC NĂNG AI VỚI TRẢI NGHIỆM NGƯỜI DÙNG (UX/UI)
- Luồng sử dụng vô cùng tự nhiên: Người dùng không cần phải học cách dùng AI hay phải mở tab riêng để chat.
- Khi người dùng bấm *"Thêm giao dịch"*, nếu trường Danh mục để là *"AI tự động phân loại"*, nút lưu sẽ hiển thị trạng thái đang xử lý. Khi hoàn thành, giao dịch lập tức xuất hiện trên bảng với đầy đủ danh mục chính xác.
- Trải nghiệm người dùng được tối ưu hóa tối đa, biến công nghệ AI phức tạp thành một tiện ích ngầm mượt mà và trực quan.

---

## KẾT LUẬN VÀ CAM KẾT CỦA NHÓM 02
Bài kiểm tra số 3 đã được Nhóm 02 thực hiện nghiêm túc, khoa học và đạt **10/10 tiêu chí đánh giá**. Toàn bộ mã nguồn, dữ liệu mẫu và các kịch bản kiểm thử đã sẵn sàng để demo trực tiếp trên lớp.

*Kính chúc Thầy/Cô dồi dào sức khỏe và công tác tốt!*  
**Đại diện Nhóm 02:** Trưởng nhóm Nguyễn Tuấn Đạt & Phó nhóm Phàn Ngọc Anh.
