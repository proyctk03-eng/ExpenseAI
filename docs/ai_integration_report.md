# BÁO CÁO TÍCH HỢP TRÍ TUỆ NHÂN TẠO (AI)
**Dự án: Hệ thống Quản lý Chi tiêu Cá nhân tích hợp AI**

> **Lưu ý dành cho sinh viên:** Dưới đây là cấu trúc báo cáo chuyên sâu về phần Tích hợp AI (Đánh trọng tâm vào bài KT3 và Báo cáo tổng kết). Bạn có thể chỉnh sửa lại số liệu hoặc câu chữ cho phù hợp với cách bạn thuyết trình.

---

## 1. Các Chức năng AI Đã Triển khai
*Mẫu viết:*
> Trong hệ thống này, Trí tuệ nhân tạo (OpenAI GPT-3.5) không hoạt động tách rời mà được nhúng sâu vào các luồng nghiệp vụ lõi (Core Business Flow), bao gồm 2 chức năng chính:
> 
> 1. **AI Classifier (Phân loại tự động):** Khi người dùng ghi nhận khoản thu/chi nhưng lười chọn danh mục, hệ thống sẽ gửi mô tả văn bản (VD: "Đi Grab đến cty") lên AI. AI sẽ tự động hiểu ngữ nghĩa và gán giao dịch này vào danh mục "Di chuyển".
> 2. **AI Financial Advisor (Tư vấn tài chính):** Tại trang Dashboard, hệ thống tổng hợp báo cáo chi tiêu của 3 tháng gần nhất (gom nhóm theo danh mục) và gửi lên AI để xin lời khuyên tối ưu hóa dòng tiền mang tính cá nhân hóa.

## 2. Phương thức Kết nối API
*Mẫu viết:*
> Hệ thống sử dụng thư viện `openai` phiên bản mới nhất (>= 1.0.0) của Python. 
> Quá trình gọi API được thực thi qua object `OpenAI(api_key=...)`. Khóa API (API Key) tuyệt đối không hard-code trong mã nguồn mà được đưa ra ngoài file cấu hình `.env` để tránh lộ lọt khi đưa code lên Github.
> Ngoài ra, để ngăn hệ thống bị treo khi API của OpenAI phản hồi chậm, một cấu hình `httpx.Timeout(15.0)` đã được thiết lập để ép đóng kết nối nếu thời gian chờ vượt quá giới hạn.

## 3. Thiết kế và Tối ưu Prompt
*Mẫu viết:*
> Để kiểm soát độ chính xác của AI, các Prompt được thiết kế theo cấu trúc tách biệt giữa **System Prompt** (quy định vai trò và định dạng đầu ra) và **User Prompt** (cung cấp dữ liệu).
> 
> **Quá trình tối ưu Prompt (Prompt Engineering):**
> - **Lần 1 (Cơ bản):** Ban đầu yêu cầu AI trả về danh mục. Kết quả trả về thường có chứa văn bản thừa như *"Danh mục phù hợp là: Ăn uống"*, gây lỗi khi Backend bóc tách dữ liệu.
> - **Lần 2 (Ràng buộc định dạng):** Thêm yêu cầu *"Chỉ trả về JSON"*. Tuy nhiên đôi khi AI vẫn trả về chuỗi JSON bị thiếu ngoặc, dẫn đến lỗi `JSONDecodeError`.
> - **Lần 3 (Tối ưu - Phiên bản hiện tại):** Sử dụng tính năng `response_format={"type": "json_object"}` của GPT-3.5-turbo. System prompt được nâng cấp thành: *"Hãy phân loại... Chỉ trả về JSON duy nhất có dạng `{"category": "Tên", "confidence": 0.95}`"*. Nhờ đó, AI trả về kết quả cấu trúc chuẩn 100%, Backend dễ dàng parse JSON và sử dụng.

## 4. Sử dụng Dữ liệu Hệ thống trong AI
*Mẫu viết:*
> Chức năng AI Tư vấn Tài chính là minh chứng rõ nhất cho việc sử dụng dữ liệu hệ thống. Thay vì bắt người dùng tự gõ câu hỏi, hệ thống Backend sẽ tự động dùng SQL (Aggregation) để cào dữ liệu giao dịch trong 90 ngày qua của chính người dùng đang đăng nhập.
> 
> **Đảm bảo bảo mật (Privacy):** Hệ thống KHÔNG gửi lịch sử chi tiết từng giao dịch lên máy chủ của OpenAI. Dữ liệu được nhóm lại thành con số tổng hợp (Ví dụ: `{"Ăn uống": 5000000, "Di chuyển": 1500000}`) trước khi nhét vào prompt. Điều này bảo vệ tối đa quyền riêng tư của người dùng.

## 5. Xử lý Lỗi và Giới hạn AI
*Mẫu viết:*
> Do AI là hệ thống bên ngoài, việc tích hợp đòi hỏi cơ chế phòng vệ (Defensive Programming) cao:
> - **Bắt lỗi mạng:** Nếu OpenAI sập mạng hoặc Timeout, hàm `try-except` sẽ bắt lỗi `OpenAIError`. Hệ thống sẽ không crash mà trả về danh mục Fallback mặc định là "Khác".
> - **Bắt lỗi dữ liệu:** Nếu nội dung người dùng nhập quá ngắn (bỏ trống) hoặc có ký tự lạ khiến JSON bị gãy, hệ thống sẽ bắt lỗi `JSONDecodeError` và ghi log ẩn danh (logger.error).

## 6. Hiển thị Kết quả trên Giao diện
*Mẫu viết:*
> Trải nghiệm của người dùng (UX) khi sử dụng AI được thiết kế liền mạch:
> - Tại Form tạo giao dịch: Khi người dùng bấm lưu, nút "Lưu" biến thành "Đang xử lý (AI)..." và khóa lại (disable) để người dùng biết hệ thống đang nghĩ. Khi AI phân loại xong, giao dịch xuất hiện ngay lập tức trong bảng.
> - Tại màn hình Dashboard: Có một khu vực dành riêng mang tên "Lời khuyên từ AI (BETA)". Lời khuyên được trả về bằng văn bản in nghiêng, ngắn gọn, dễ đọc, giúp người dùng nắm bắt tình trạng tài chính trong nháy mắt.

## 7. Kiểm thử Chức năng AI
*Mẫu viết:*
> Việc kiểm thử (Testing) một tính năng AI sinh văn bản là khá khó vì kết quả luôn thay đổi. Dự án sử dụng kỹ thuật **Mocking** (`unittest.mock.patch` của Python) để cô lập chức năng này.
> Trong các file unit test (`pytest`), hàm gọi AI được giả lập (mock) để luôn trả về `{"category": "Giải trí", "confidence": 0.98}` mà không tốn tiền gửi Request thật lên OpenAI. Qua đó, ta kiểm thử thành công việc Database có gán đúng danh mục này cho Giao dịch hay không.

## 8. Ứng dụng AI vào Quá trình Review Code
*(Khu vực này bạn nêu ví dụ về việc bạn đã dùng ChatGPT / Antigravity AI để hỗ trợ như thế nào trong lúc code)*

**Ví dụ tham khảo:**
> Trong quá trình xây dựng API, tôi đã sử dụng AI (ChatGPT) làm "Người đánh giá mã nguồn" (Code Reviewer). 
> - **Hoạt động thực tế:** Tôi đã copy toàn bộ file `src/api/transactions.py` vào khung chat và yêu cầu AI rà soát lỗ hổng.
> - **Phản hồi của AI:** AI đã chỉ ra rằng quá trình lưu Giao dịch và Danh mục (nếu tự tạo mới) đang không được đặt chung trong một khối nguyên tử (Atomicity). 
> - **Cải tiến:** Nhờ gợi ý đó, tôi đã áp dụng `db.flush()` để lấy ID tạm thời và đưa tất cả vào chung một khối `try-except` với `db.rollback()`. Nếu AI phân tích lỗi hoặc DB sập, toàn bộ thao tác sẽ bị hủy để bảo toàn dữ liệu. Minh chứng hình ảnh cuộc hội thoại được đính kèm ở phụ lục.
