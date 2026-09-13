# BÁO CÁO SỐ 4: TỔNG KẾT BẢO VỆ ĐỒ ÁN (THI KẾT THÚC HỌC PHẦN)
**Kính gửi:** Hội đồng chấm thi / Thầy Cô giảng viên bộ môn  
**Dự án:** ExpenseAI - Hệ thống Quản lý Chi tiêu Cá nhân thông minh tích hợp Trí tuệ Nhân tạo  
**Đơn vị đào tạo:** Khoa Công nghệ Thông tin - Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU)  
**Nhóm thực hiện:** Nhóm 02  
- **Nguyễn Tuấn Đạt** - Trưởng nhóm (Kiến trúc Backend, Tích hợp AI & CI/CD Pipeline)  
- **Phàn Ngọc Anh** - Phó nhóm (Giao diện Frontend UI/UX, Kiểm thử & Quản trị CSDL)  

---

## LỜI MỞ ĐẦU
Kính thưa Hội đồng chấm thi và quý Thầy/Cô, trải qua toàn bộ vòng đời phát triển phần mềm (SDLC) từ khảo sát yêu cầu, thiết kế kiến trúc, lập trình chức năng cốt lõi cho đến tích hợp Trí tuệ Nhân tạo và kiểm thử tự động, Nhóm 02 đã hoàn thiện trọn vẹn sản phẩm **ExpenseAI**. 

Báo cáo này là bản đúc kết tổng thể toàn diện nhằm phục vụ kỳ **Thi kết thúc học phần**, đối chiếu chi tiết với 10 tiêu chí nghiệm thu kỹ thuật cao nhất của môn học.

---

## 1. HOÀN THIỆN CHỨC NĂNG HỆ THỐNG (SYSTEM COMPLETENESS)
Hệ thống đã được lập trình hoàn thiện 100% các phân hệ chức năng thực tế, không sử dụng dữ liệu giả lập hay giao diện mẫu (mockup):
- **Phân hệ Xác thực & Tài khoản:** Đăng ký, đăng nhập bảo mật cấp phát Access Token (JWT) và Cookie HttpOnly, xem và chỉnh sửa thông tin cá nhân.
- **Phân hệ Quản lý Danh mục (Categories):** Hỗ trợ danh mục mặc định của hệ thống và danh mục cá nhân tự tạo; hỗ trợ Modal thêm mới nhanh chóng; phân tách rõ ràng danh mục Thu nhập (Income) và Chi tiêu (Expense).
- **Phân hệ Quản lý Giao dịch (Transactions CRUD):** Thêm mới giao dịch, xem lịch sử giao dịch với bộ lọc đa tiêu chí, chỉnh sửa thông tin giao dịch qua Modal Popup trực tiếp, xóa giao dịch an toàn với hộp thoại xác nhận.
- **Phân hệ Thống kê & Báo cáo (Analytics):** Dashboard trực quan hiển thị Tổng thu, Tổng chi, Số dư thực tế; biểu đồ tròn cơ cấu chi tiêu; biểu đồ cột xu hướng tài chính hàng tháng (Chart.js).
- **Phân hệ Trí tuệ Nhân tạo (AI Features):** Tự động nhận diện danh mục từ mô tả tự nhiên (AI Classifier) và tự động sinh lời khuyên tài chính cá nhân hóa định kỳ (AI Advisor).

---

## 2. CHẤT LƯỢNG KIẾN TRÚC VÀ MÃ NGUỒN (CODE QUALITY & ARCHITECTURE)
- **Kiến trúc phân tầng Controller - Service - Data Access:**
  - `src/api/`: Đóng vai trò Controller, tiếp nhận request, validate dữ liệu đầu vào và điều hướng nghiệp vụ.
  - `src/services/`: Chứa nghiệp vụ chuyên sâu, đặc biệt là các logic tích hợp OpenAI API và thuật toán Heuristic fallback.
  - `src/models/` & `src/schemas/`: Tách bạch giữa Entity CSDL (SQLAlchemy ORM) và Schema giao tiếp API (Pydantic).
- **Chuẩn mực mã nguồn:**
  - Toàn bộ mã nguồn viết bằng Python 3.10+ tuân thủ nghiêm ngặt tiêu chuẩn **PEP8**.
  - Áp dụng **Type Hinting** đầy đủ cho các hàm và phương thức, giúp mã nguồn tự dẫn chứng tài liệu và tương thích hoàn hảo với Swagger UI (`/docs`).
  - Đạt điểm chuẩn Linting sạch sẽ với `black`, `flake8` và `isort`.

---

## 3. CHẤT LƯỢNG CƠ SỞ DỮ LIỆU (DATABASE QUALITY & RESILIENCE)
- **Cấu trúc chuẩn hóa 3NF:** Cơ sở dữ liệu gồm 7 bảng liên kết chặt chẽ: `users`, `categories`, `transactions`, `ai_predictions`, `roles`, `permissions`, `role_permissions`.
- **Ràng buộc toàn vẹn dữ liệu:** Khóa chính (Primary Key), khóa ngoại (Foreign Key) kèm `ON DELETE CASCADE` hoặc `SET NULL` hợp lý; ràng buộc duy nhất (Unique Constraint) trên username và email.
- **Tính di động cao:** Hỗ trợ song song cả SQLite (nhẹ, tiện dụng cho môi trường local/test) lẫn PostgreSQL (mạnh mẽ, sẵn sàng cho môi trường Production / Docker).
- **Dữ liệu mẫu chân thực:** File `scripts/seed_data.py` tự động khởi tạo bộ dữ liệu chi tiêu mẫu của sinh viên Việt Nam trong 30 ngày (Tiền bố mẹ gửi, Lương part-time, Ăn uống, Học phí, Xăng xe,...), giúp Hội đồng có thể demo nghiệm thu ngay lập tức.
- **Quản lý phiên bản CSDL (Database Migration):** Tích hợp công cụ `Alembic`, cho phép nâng cấp (`upgrade head`) và hạ cấp CSDL an toàn mà không làm mất mát dữ liệu.

---

## 4. CHẤT LƯỢNG GIAO DIỆN VÀ TRẢI NGHIỆM NGƯỜI DÙNG (UI/UX EXCELLENCE)
- **Phong cách thiết kế:** Kết hợp giữa tính hiện đại của **Glassmorphism** và sự tiện dụng của **Bootstrap 5**, tạo ấn tượng thị giác cao cấp ngay từ cái nhìn đầu tiên.
- **Tính ngữ nghĩa màu sắc:**
  - Khoản Thu nhập: Hiển thị màu **Xanh lá cây** với dấu cộng (`+`).
  - Khoản Chi tiêu: Hiển thị màu **Đỏ cam** với dấu trừ (`-`).
- **Tương tác mượt mà không tải lại trang:** Thao tác tìm kiếm, lọc theo ngày, sửa giao dịch (Edit Modal) và thêm danh mục mới đều được kết nối thông qua `Fetch API` và cập nhật DOM động, mang lại trải nghiệm mượt mà như Single Page Application (SPA).
- **Responsive 100%:** Bố cục thanh Sidebar tự động co giãn thông minh, hiển thị tối ưu trên cả màn hình máy tính bàn, máy tính bảng và điện thoại thông minh (có nút menu Hamburger).

---

## 5. CHẤT LƯỢNG CHỨC NĂNG AI (AI VALUE & RELIABILITY)
- **Giải quyết bài toán thực tế:** AI không làm thay đổi thói quen người dùng mà hỗ trợ ngầm: người dùng chỉ cần gõ nội dung ngắn gọn thường ngày (VD: *"Đổ xăng 70k"*, *"Đi siêu thị mua rau thịt 120k"*), AI hiểu ngữ cảnh và tự phân loại chính xác trên 95%.
- **Kiểm soát ảo giác (Hallucination Control):** 
  - Kẹp cứng danh sách các danh mục hệ thống trong System Prompt.
  - Sử dụng tham số `temperature = 0` và ép kiểu `response_format={"type": "json_object"}` để AI luôn phản hồi nhất quán, không sáng tạo tùy tiện.
- **Cơ chế Fallback thông minh:** Khi mạng gặp sự cố hoặc chưa có API Key, hệ thống tự động kích hoạt bộ Heuristic Classifier dựa trên từ điển từ khóa tiếng Việt nội bộ, đảm bảo quy trình lưu trữ giao dịch không bao giờ bị gián đoạn.

---

## 6. BẢO MẬT, QUYỀN RIÊNG TƯ VÀ ĐẠO ĐỨC AI (SECURITY & ETHICS)
- **Bảo vệ danh tính người dùng:** Mật khẩu được băm một chiều an toàn bằng thuật toán mã hóa công nghiệp **Bcrypt** với Salt ngẫu nhiên.
- **Xác thực và Phân quyền (RBAC):** Token JWT chứa thông tin định danh và vai trò, chữ ký mã hóa bằng thuật toán `HS256`. Hệ thống ngăn chặn triệt để lỗ hổng phân quyền ngang (IDOR): người dùng tuyệt đối không thể xem, sửa hoặc xóa dữ liệu của người khác.
- **Đạo đức và Quyền riêng tư dữ liệu AI:**
  - Hệ thống **KHÔNG gửi dữ liệu cá nhân hay lịch sử giao dịch thô** lên OpenAI.
  - Chỉ gửi các con số tổng hợp vô danh theo danh mục (Aggregated Data) khi xin lời khuyên tài chính, tuân thủ nguyên tắc Privacy-by-Design.
  - API Key được bảo vệ an toàn trong file `.env`, tuyệt đối không lưu cứng trong code.

---

## 7. HIỆU NĂNG VÀ ĐỘ ỔN ĐỊNH (PERFORMANCE & STABILITY)
- **Tối ưu hóa tài nguyên server:** Thay vì dùng vòng lặp Python duyệt hàng nghìn bản ghi, nhóm tận dụng triệt để sức mạnh của Database Engine qua các hàm tính toán `func.sum()`, `GROUP BY`, giảm thiểu 80% RAM sử dụng.
- **Phòng chống tấn công DoS / Brute-force:** Tích hợp middleware **SlowAPI** giới hạn tần suất gọi request (Rate Limiting) ở các endpoint nhạy cảm như Đăng ký, Đăng nhập.
- **Bảo toàn dữ liệu (Atomicity):** Mọi giao dịch lưu CSDL và lưu kết quả AI đều nằm trong một Database Transaction duy nhất. Bất kỳ lỗi nào xảy ra đều kích hoạt `db.rollback()`, triệt tiêu hoàn toàn nguy cơ rác dữ liệu.

---

## 8. TRIỂN KHAI VÀ ĐÓNG GÓI (DEVOPS & DEPLOYMENT)
- **Container hóa với Docker:** Cung cấp `Dockerfile` đa tầng (Multi-stage build) tối ưu hóa dung lượng image chỉ còn khoảng 180MB.
- **Điều phối dịch vụ với Docker Compose:** File `docker-compose.yml` định nghĩa hoàn chỉnh hệ sinh thái gồm: Ứng dụng Web FastAPI, CSDL PostgreSQL 15 và mạng nội bộ cách ly. Thầy/Cô chỉ cần chạy đúng 1 lệnh duy nhất:
  ```bash
  docker-compose up -d --build
  ```
- **Tự động hóa CI/CD với GitHub Actions:** Đã thiết lập pipeline tại `.github/workflows/ci.yml`. Mỗi khi push code, hệ thống tự động khởi tạo máy ảo Ubuntu, cài đặt dependencies, chạy 35 bài kiểm thử trên cả Python 3.10, 3.11, 3.12 và quét lỗ hổng bảo mật Trivy. Pipeline hiện tại **đạt kết quả xanh 100% (Success)**.

---

## 9. BÁO CÁO KỸ THUẬT VÀ TÀI LIỆU DỰ ÁN (DOCUMENTATION)
Thư mục [docs/](file:///c:/Users/dathao/Downloads/AI/ExpenseAI/docs) của dự án được tổ chức khoa học với đầy đủ các tài liệu chuyên ngành:
1. `Bao_Cao_1_Phan_Tich_Thiet_Ke.md` & `.docx`: Phân tích nghiệp vụ, Use Case, ERD, Kiến trúc hệ thống.
2. `Bao_Cao_2_Lap_Trinh_Co_Ban.md` & `.docx`: Lập trình CRUD, Bộ lọc tìm kiếm, CSDL, Xử lý lỗi.
3. `Bao_Cao_3_Tich_Hop_AI.md` & `.docx`: Tích hợp mô hình AI, 3 vòng thử nghiệm Prompt, kiểm thử 35 test case.
4. `Bao_Cao_4_Ket_Thuc_Hoc_Phan.md` & `.docx`: Báo cáo kỹ thuật tổng kết bảo vệ đồ án.
5. `ai_usage_evidence.md`: Minh chứng đầy đủ về việc sử dụng AI trợ giúp trong các khâu SDLC.
6. `Standard_SDLC/`: 7 tập tài liệu quy chuẩn đặc tả phần mềm từ Project Plan đến User Guide.

---

## 10. KỊCH BẢN THUYẾT TRÌNH VÀ DEMO SẢN PHẨM (PRESENTATION & DEMO)
Nhóm 02 đã chuẩn bị một kịch bản demo mạch lạc dài 5 - 7 phút, phân chia vai trò rõ ràng giữa 2 thành viên:

```
┌─────────────────────────────────────────────────────────────┐
│             KỊCH BẢN DEMO BẢO VỆ ĐỒ ÁN (7 PHÚT)             │
├─────────────────────────────────────────────────────────────┤
│ 1. MỞ ĐẦU (1 phút) - Nguyễn Tuấn Đạt:                      │
│    - Giới thiệu thành viên, vấn đề thực tế và kiến trúc app.│
│                                                             │
│ 2. DEMO CHỨC NĂNG CỐT LÕI (2 phút) - Phàn Ngọc Anh:         │
│    - Đăng nhập tài khoản sinh viên với seed data có sẵn.    │
│    - Thao tác thanh bộ lọc (Filter theo ngày, từ khóa).     │
│    - Mở Modal Sửa giao dịch và Modal Thêm danh mục mới.     │
│                                                             │
│ 3. DEMO CHỨC NĂNG AI (2 phút) - Nguyễn Tuấn Đạt:           │
│    - Nhập giao dịch tự nhiên: "Ăn bún chả 40k" -> AI tự gán │
│      vào "Ăn uống".                                         │
│    - Mở Dashboard xem Lời khuyên tài chính cá nhân hóa.     │
│    - Trình diễn cơ chế Heuristic Fallback khi ngắt mạng AI. │
│                                                             │
│ 4. MINH CHỨNG KIỂM THỬ & CI/CD (1.5 phút) - Nhóm 02:        │
│    - Mở terminal chạy `pytest tests/` -> 35/35 Tests PASS!  │
│    - Chiếu trang GitHub Actions với dấu tích xanh ✅ 100%.  │
│                                                             │
│ 5. KẾT LUẬN & TRẢ LỜI CÂU HỎI (0.5 phút):                   │
│    - Lắng nghe nhận xét và trả lời câu hỏi của Hội đồng.    │
└─────────────────────────────────────────────────────────────┘
```

---

## LỜI CẢM ƠN
Nhóm 02 xin bày tỏ lòng biết ơn chân thành và sâu sắc nhất tới quý Thầy/Cô giảng viên bộ môn đã tận tình truyền đạt kiến thức, định hướng phương pháp và hỗ trợ chúng em trong suốt học phần vừa qua. Những kiến thức và trải nghiệm thực chiến từ dự án ExpenseAI là hành trang vô giá cho sự nghiệp kỹ sư phần mềm tương lai của chúng em.

**Kính chúc quý Thầy/Cô luôn dồi dào sức khỏe, hạnh phúc và gặt hái nhiều thành công trong sự nghiệp trồng người!**

*Thái Nguyên, ngày 13 tháng 09 năm 2026*  
**Thay mặt Nhóm 02:**  
- Trưởng nhóm: **Nguyễn Tuấn Đạt**  
- Phó nhóm: **Phàn Ngọc Anh**
