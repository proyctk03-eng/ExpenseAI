# KỊCH BẢN THUYẾT TRÌNH VÀ DEMO BẢO VỆ ĐỒ ÁN - NHÓM 02
**Học phần:** Ứng dụng Trí tuệ Nhân tạo trong Phát triển Phần mềm  
**Đơn vị:** Khoa Công nghệ Thông tin - Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU)  
**Đề tài:** ExpenseAI - Hệ thống Quản lý Chi tiêu Cá nhân thông minh tích hợp Trí tuệ Nhân tạo  
**Thời lượng chuẩn:** 7 phút (5 phút trình bày & demo + 2 phút vấn đáp)  

### Thành viên Nhóm 02:
1. **Nguyễn Tuấn Đạt** (Trưởng nhóm)
2. **Phàn Ngọc Anh** (Phó nhóm)

---

## ⏱️ DÒNG THỜI GIAN THỰC HIỆN BẢO VỆ (TIMELINE)

```
00:00 ─── 01:30 : Phần 1 - Đặt vấn đề, Bối cảnh & Kiến trúc Hệ thống (Đạt)
01:30 ─── 04:00 : Phần 2 - Demo Nghiệp vụ cốt lõi & Giao diện người dùng (Anh)
04:00 ─── 05:30 : Phần 3 - Demo Tích hợp AI, Tối ưu Prompt & Fallback (Đạt)
05:30 ─── 07:00 : Phần 4 - Minh chứng Kiểm thử 35/35 Test & CI/CD GitHub (Cả nhóm)
Sau 07:00       : Phần 5 - Vấn đáp và Trả lời câu hỏi của Hội đồng phản biện
```

---

## 🎙️ CHI TIẾT TỪNG PHẦN THUYẾT TRÌNH

### PHẦN 1: ĐẶT VẤN ĐỀ & KIẾN TRÚC HỆ THỐNG (1.5 phút)
> **Người trình bày:** Nguyễn Tuấn Đạt

- **Lời mở đầu:**  
  *"Kính thưa quý Thầy Cô trong Hội đồng chấm thi! Em tên là Nguyễn Tuấn Đạt, cùng bạn Phàn Ngọc Anh là thành viên Nhóm 02. Hôm nay, nhóm chúng em xin phép được báo cáo và bảo vệ đồ án kết thúc học phần với đề tài: **ExpenseAI - Hệ thống Quản lý Chi tiêu Cá nhân thông minh tích hợp Trí tuệ Nhân tạo**."*

- **Vấn đề thực tế:**  
  *"Trong thực tế, sinh viên và người trẻ thường gặp khó khăn trong việc duy trì thói quen ghi chép tài chính cá nhân do các ứng dụng truyền thống đòi hỏi quá nhiều thao tác thủ công phức tạp (tự chọn danh mục, tự tính toán). Vì vậy, nhóm chúng em đã phát triển ExpenseAI với mục tiêu cốt lõi: **Ứng dụng mô hình Invisible AI để tối giản hóa tối đa quy trình nhập liệu và tự động hóa việc đưa ra lời khuyên tài chính thông minh**."*

- **Kiến trúc kỹ thuật:**  
  *"Hệ thống được thiết kế theo kiến trúc 3 tầng chuẩn mực: Backend xây dựng bằng **FastAPI**, lưu trữ dữ liệu trên **PostgreSQL / SQLite** chuẩn hóa 3NF qua SQLAlchemy 2.0, giao diện Web sử dụng **Bootstrap 5 kết hợp Glassmorphism**, và tích hợp mô hình **OpenAI GPT** qua bộ chuyển đổi độc lập."*

---

### PHẦN 2: DEMO NGHIỆP VỤ CỐT LÕI & GIAO DIỆN (2.5 phút)
> **Người thực hiện:** Phàn Ngọc Anh

- **Đăng nhập & Seed Data thực tế:**  
  *"Sau đây em xin phép thao tác trực tiếp trên sản phẩm thật của nhóm. Hệ thống đã có sẵn tài khoản mẫu với bộ dữ liệu chi tiêu chân thực của sinh viên trong 30 ngày vừa qua. Em tiến hành đăng nhập vào hệ thống..."*  
  *(Thao tác: Đăng nhập -> Vào trang Lịch sử giao dịch)*

- **Trình diễn Bộ lọc & Tìm kiếm đa tiêu chí:**  
  *"Tại trang Lịch sử giao dịch, giao diện được phân tách ngữ nghĩa rất trực quan: màu xanh lá kèm dấu cộng cho khoản Thu nhập và màu đỏ kèm dấu trừ cho khoản Chi tiêu. Em xin thử nghiệm thanh công cụ bộ lọc:  
  - Tìm kiếm từ khóa: Gõ 'phở' -> Bảng lập tức lọc ra các giao dịch ăn sáng.  
  - Lọc theo khoảng ngày: Chọn từ ngày 01 đến ngày 10 -> Dữ liệu cập nhật ngay lập tức qua Fetch API mà không cần tải lại trang."*

- **Trình diễn Chỉnh sửa (Modal Edit) & Thêm Danh mục mới:**  
  *"Khi cần điều chỉnh thông tin, em chỉ cần bấm vào nút Sửa tại giao dịch, một Modal Popup hiện lên cho phép cập nhật số tiền và mô tả. Đồng thời, tại trang Cài đặt, người dùng có thể tạo thêm các Danh mục chi tiêu cá nhân một cách nhanh chóng qua Modal tạo danh mục."*

---

### PHẦN 3: DEMO TÍCH HỢP AI, PROMPT & CƠ CHẾ PHÒNG VỆ (1.5 phút)
> **Người thực hiện:** Nguyễn Tuấn Đạt

- **Trình diễn AI Classifier (Phân loại tự động):**  
  *"Bây giờ em xin phép trình diễn tính năng AI cốt lõi của hệ thống. Em mở form Thêm giao dịch mới, nhập số tiền `45000` và mô tả hoàn toàn bằng ngôn ngữ tự nhiên: `Ăn trưa cơm tấm sườn trứng`. Tại ô Danh mục, em để mặc định là `AI tự động phân loại`. Khi bấm Lưu, backend gửi mô tả lên OpenAI, mô hình nhận diện chính xác ngữ nghĩa và tự động gán vào danh mục `Ăn uống`."*

- **Giải thích kỹ thuật 3 vòng tối ưu Prompt:**  
  *"Để đạt được độ chính xác trên 96% và không bao giờ bị lỗi format, nhóm đã trải qua 3 vòng thử nghiệm Prompt: từ Prompt tự do gây lỗi parse JSON ở vòng 1, đến vòng 2 yêu cầu JSON nhưng AI tự bịa danh mục, và đạt mức hoàn thiện ở vòng 3 khi kẹp cứng danh mục hệ thống và dùng cờ `response_format={'type': 'json_object'}`."*

- **Dashboard & Cơ chế Phòng thủ (Fallback):**  
  *"Trên Dashboard, tính năng AI Advisor tự động cào dữ liệu tổng hợp 90 ngày để đưa ra lời khuyên tài chính cá nhân hóa. Đặc biệt, hệ thống tuân thủ nguyên tắc Privacy-by-Design: không gửi dữ liệu thô ra ngoài. Nếu mất kết nối mạng hoặc hết tiền OpenAI, cơ chế Heuristic Fallback nội bộ sẽ tự kích hoạt, đảm bảo ứng dụng không bao giờ bị sập."*

---

### PHẦN 4: MINH CHỨNG KIỂM THỬ VÀ CI/CD GITHUB (1.5 phút)
> **Người thực hiện:** Cả nhóm (Đạt & Anh)

- **Chạy Pytest trực tiếp tại Terminal:**  
  *"Để chứng minh độ tin cậy và sự ổn định của toàn bộ hệ thống, em xin phép chạy lệnh kiểm thử tự động tại terminal:  
  `pytest tests/`  
  -> Kết quả hiển thị: **35/35 Test Cases PASS 100%** trong chưa đầy 15 giây, bao phủ từ xác thực JWT, bảo mật phân quyền RBAC, kiểm tra dữ liệu biên đến các luồng tích hợp AI."*

- **Chứng minh Pipeline CI/CD GitHub Actions Xanh Tuyệt Đối:**  
  *(Chuyển sang tab trình duyệt mở GitHub repository: `github.com/proyctk03-eng/ExpenseAI`)*  
  *"Mã nguồn của nhóm được quản lý chuyên nghiệp trên GitHub. Nhóm đã cấu hình sẵn quy trình DevOps tự động qua GitHub Actions. Như Thầy/Cô đang thấy trên màn hình, commit mới nhất đã vượt qua toàn bộ các bước build, kiểm thử trên 3 phiên bản Python 3.10, 3.11, 3.12 và quét bảo mật Trivy, đạt **dấu tích xanh ✅ 100%**."*

- **Kết luận:**  
  *"Bài báo cáo của Nhóm 02 đến đây là kết thúc. Chúng em xin chân thành cảm ơn quý Thầy/Cô đã lắng nghe và rất mong nhận được những câu hỏi đóng góp từ Hội đồng ạ!"*

---

## 🎯 BỘ CÂU HỎI VẤN ĐÁP PHẢN BIỆN DỰ KIẾN & CÂU TRẢ LỜI MẪU

### Câu hỏi 1: Tại sao nhóm không dùng Chatbot mà lại chọn mô hình Invisible AI?
> **Trả lời:**  
> *"Dạ thưa Thầy/Cô, theo khảo sát trải nghiệm người dùng thực tế, người dùng ghi chép chi tiêu cần sự nhanh gọn (dưới 5 giây cho 1 khoản chi). Việc bắt người dùng mở một cửa sổ chat để gõ hội thoại qua lại sẽ làm tăng số bước thao tác và gây mệt mỏi. Mô hình Invisible AI giúp AI hoạt động như một trợ lý ngầm tự động hóa quy trình, mang lại giá trị thực tiễn cao nhất cho người dùng ạ."*

### Câu hỏi 2: Nếu OpenAI bị quá tải hoặc mất mạng thì hệ thống xử lý như thế nào?
> **Trả lời:**  
> *"Dạ thưa Thầy/Cô, nhóm đã lập trình cơ chế phòng vệ Fault-Tolerant:  
> 1. Thiết lập Timeout 15 giây để không làm treo server.  
> 2. Đặt khối `try...except` bắt lỗi `APITimeoutError` và `RateLimitError`.  
> 3. Tự động chuyển hướng sang bộ Heuristic Classifier nội bộ (sử dụng từ điển từ khóa tiếng Việt) để phân loại tạm thời hoặc gán vào danh mục 'Khác'. Nhờ đó, giao dịch của người dùng luôn được lưu thành công vào CSDL mà không bị gián đoạn ạ."*

### Câu hỏi 3: Việc gửi dữ liệu chi tiêu lên OpenAI có vi phạm quyền riêng tư của người dùng không?
> **Trả lời:**  
> *"Dạ thưa Thầy/Cô, hệ thống của nhóm tuân thủ nghiêm ngặt nguyên tắc Privacy-by-Design:  
> - Tuyệt đối KHÔNG gửi danh sách chi tiết các khoản chi, địa điểm hay thời gian cụ thể lên OpenAI.  
> - Backend chỉ chạy câu lệnh SQL Aggregate tính ra các con số tổng hợp theo danh mục (ví dụ: Ăn uống 2 triệu, Học tập 500k) và ẩn danh hoàn toàn thông tin người dùng trước khi đưa vào prompt tư vấn. Do đó, tính riêng tư và bảo mật dữ liệu của người dùng được đảm bảo tuyệt đối ạ."*
