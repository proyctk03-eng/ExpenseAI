import os
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_toc(paragraph):
    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')  # creates a new element
    fldChar.set(qn('w:fldCharType'), 'begin')  # sets attribute on element
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')  # sets attribute on element
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'   # change 1-3 depending on heading levels you need
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')

    r_element = run._r
    r_element.append(fldChar)
    r_element.append(instrText)
    r_element.append(fldChar2)
    r_element.append(fldChar3)

def create_report():
    doc = Document()
    
    # 4. Khoảng cách (Spacing) & Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)
        
    # Styles configuration
    styles = doc.styles
    
    # Normal Text (13pt, Times New Roman, 1.5 line spacing, 6pt after)
    style_normal = styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(13)
    pf_normal = style_normal.paragraph_format
    pf_normal.line_spacing = 1.5
    pf_normal.space_after = Pt(6)
    
    # Heading 1 (16pt, Bold, UPPERCASE, Centered)
    style_h1 = styles['Heading 1']
    font_h1 = style_h1.font
    font_h1.name = 'Times New Roman'
    font_h1.size = Pt(16)
    font_h1.bold = True
    font_h1.all_caps = True
    font_h1.color.rgb = None
    pf_h1 = style_h1.paragraph_format
    pf_h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf_h1.space_after = Pt(12)
    pf_h1.space_before = Pt(24)
    
    # Heading 2 (14pt, Bold, Left)
    style_h2 = styles['Heading 2']
    font_h2 = style_h2.font
    font_h2.name = 'Times New Roman'
    font_h2.size = Pt(14)
    font_h2.bold = True
    font_h2.color.rgb = None
    
    # Heading 3 (13pt, Bold, Italic)
    style_h3 = styles['Heading 3']
    font_h3 = style_h3.font
    font_h3.name = 'Times New Roman'
    font_h3.size = Pt(13)
    font_h3.bold = True
    font_h3.italic = True
    font_h3.color.rgb = None

    # Code style
    try:
        style_code = styles.add_style('CodeBlock', WD_STYLE_TYPE.PARAGRAPH)
        style_code.font.name = 'Courier New'
        style_code.font.size = Pt(11)
        style_code.paragraph_format.left_indent = Inches(0.5)
    except:
        style_code = styles['CodeBlock']

    # --- COVER PAGE ---
    doc.add_heading('BÁO CÁO TỔNG KẾT DỰ ÁN', level=1)
    doc.add_heading('EXPENSE AI - QUẢN LÝ CHI TIÊU CÁ NHÂN', level=1)
    doc.add_paragraph('\n\n\n')
    doc.add_page_break()

    # --- TOC ---
    doc.add_heading('MỤC LỤC', level=1)
    p_toc = doc.add_paragraph()
    add_toc(p_toc)
    doc.add_paragraph('(Vui lòng click chuột phải chọn "Update Field" để cập nhật Mục lục tự động)', style='Normal')
    doc.add_page_break()

    # --- PHẦN 1 ---
    doc.add_heading('PHẦN 1: GIỚI THIỆU', level=1)
    
    doc.add_heading('1.1. Tổng quan dự án', level=2)
    doc.add_paragraph('Tên dự án: ExpenseAI').runs[0].bold = True
    doc.add_paragraph('Mục tiêu: Xây dựng ứng dụng quản lý chi tiêu cá nhân thông minh, tích hợp AI tự động phân loại giao dịch và đưa ra lời khuyên tài chính cá nhân hóa.')
    doc.add_paragraph('Phạm vi: Web application hoạt động trên cả trình duyệt máy tính và di động.')
    doc.add_paragraph('Công nghệ sử dụng: Python (FastAPI), Cơ sở dữ liệu PostgreSQL, Giao diện HTML/CSS/JS (Light Theme, Glassmorphism), Docker.')

    doc.add_heading('1.2. Thành viên thực hiện', level=2)
    doc.add_paragraph('- Nguyễn Tuấn Đạt (Leader): Phân tích thiết kế, xây dựng Backend FastAPI, Database, và kết nối OpenAI.')
    doc.add_paragraph('- Phàn Ngọc Anh (Co-leader): Thiết kế giao diện (UI/UX), lập trình HTML/CSS, tích hợp Chart.js, kiểm thử (Testing).')

    doc.add_heading('1.3. Môi trường phát triển', level=2)
    doc.add_paragraph('- Hệ điều hành: Windows / Linux (Docker)')
    doc.add_paragraph('- Trình biên dịch/Interpreter: Python 3.10+')
    doc.add_paragraph('- Các thư viện/framework: FastAPI, SQLAlchemy, Pydantic, Chart.js, Bootstrap 5, OpenAI SDK, Pytest.')

    # --- PHẦN 2 ---
    doc.add_heading('PHẦN 2: PHÂN TÍCH & THIẾT KẾ HỆ THỐNG', level=1)
    
    doc.add_heading('2.1. Sơ đồ Use Case', level=2)
    doc.add_paragraph('Hệ thống xoay quanh 1 Actor chính là Người dùng (User). Các Use case chính bao gồm:')
    doc.add_paragraph('- Đăng ký / Đăng nhập / Đổi mật khẩu.')
    doc.add_paragraph('- Quản lý Giao dịch (Thêm, Sửa, Xóa, Xem danh sách).')
    doc.add_paragraph('- Quản lý Danh mục chi tiêu.')
    doc.add_paragraph('- Xem Thống kê & Báo cáo (Tổng quan, Biểu đồ vòng, Biểu đồ cột).')
    doc.add_paragraph('- Nhận lời khuyên từ AI (Dựa trên dữ liệu chi tiêu).')

    doc.add_heading('2.2. Sơ đồ Database (ERD)', level=2)
    doc.add_paragraph('Cơ sở dữ liệu gồm 3 bảng chính:')
    doc.add_paragraph('1. users: id, username, email, hashed_password, role.')
    doc.add_paragraph('2. categories: id, name, type (income/expense), user_id.')
    doc.add_paragraph('3. transactions: id, amount, description, transaction_date, category_id, user_id.')
    doc.add_paragraph('Mối quan hệ: Một User có nhiều Category và Transaction. Một Category có thể thuộc về nhiều Transaction.')

    doc.add_heading('2.3. Thiết kế giao diện (UI/UX)', level=2)
    doc.add_paragraph('Giao diện được thiết kế theo phong cách Minimalism kết hợp Glassmorphism. Màu chủ đạo là xanh dương đậm và gradient. Bố cục 2 cột với Sidebar điều hướng bên trái và Content chính bên phải. Responsive thân thiện với thiết bị di động.')

    # --- PHẦN 3 ---
    doc.add_heading('PHẦN 3: CHI TIẾT TRIỂN KHAI', level=1)
    
    doc.add_heading('3.1. Backend (Python + FastAPI)', level=2)
    doc.add_paragraph('Cấu trúc thư mục được phân chia rõ ràng theo chuẩn mô hình MVC thu gọn (routers, schemas, models).')
    doc.add_heading('Xác thực (Auth)', level=3)
    doc.add_paragraph('Sử dụng JWT Bearer Token. API `/register` và `/login` trả về token lưu ở localStorage.')
    doc.add_heading('Đoạn code gọi AI mẫu:', level=3)
    doc.add_paragraph('response = await client.chat.completions.create(model="gpt-4o-mini", messages=[...])', style='CodeBlock')

    doc.add_heading('3.2. Frontend (HTML/CSS/JS)', level=2)
    doc.add_paragraph('Sử dụng template Jinja2 render SSR. Các thao tác form dùng JavaScript Fetch API gọi về Backend, hiển thị thông báo không cần reload lại toàn bộ trang.')

    doc.add_heading('3.3. Tích hợp AI', level=2)
    doc.add_paragraph('Prompt engineering được áp dụng chặt chẽ. Backend thu thập 30 ngày giao dịch gần nhất, chuyển thành chuỗi JSON và gửi cho model `gpt-4o-mini` kèm System Prompt yêu cầu đóng vai chuyên gia tài chính. Kết quả trả về được định dạng HTML an toàn để render lên Dashboard.')

    # --- PHẦN 4 ---
    doc.add_heading('PHẦN 4: KIỂM THỬ (TESTING)', level=1)
    doc.add_heading('4.1. Phương pháp kiểm thử', level=2)
    doc.add_paragraph('Kết hợp kiểm thử tự động bằng Pytest (35 test cases) cho API và kiểm thử thủ công qua UI.')
    
    doc.add_heading('4.2. Danh sách Test Case', level=2)
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'ID'
    hdr_cells[1].text = 'Mô tả'
    hdr_cells[2].text = 'Kết quả mong đợi'
    hdr_cells[3].text = 'Trạng thái'
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'TC_01'
    row_cells[1].text = 'Đăng nhập sai MK'
    row_cells[2].text = 'Trả về HTTP 401'
    row_cells[3].text = 'PASS'
    
    row_cells = table.add_row().cells
    row_cells[0].text = 'TC_02'
    row_cells[1].text = 'AI Phân loại giao dịch'
    row_cells[2].text = 'Trả về đúng ID Category'
    row_cells[3].text = 'PASS'

    # --- PHẦN 5 ---
    doc.add_heading('PHẦN 5: KẾT QUẢ ĐẠT ĐƯỢC VÀ ĐÁNH GIÁ', level=1)
    doc.add_heading('5.1. Những gì đã làm được', level=2)
    doc.add_paragraph('- Hệ thống chạy ổn định 100% trên môi trường Docker.')
    doc.add_paragraph('- AI hoạt động trơn tru, giúp tiết kiệm thời gian nhập liệu.')
    
    doc.add_heading('5.2. Những hạn chế', level=2)
    doc.add_paragraph('- Do hạn chế API Key, đôi khi tốc độ phản hồi của AI mất khoảng 2-3 giây.')
    
    doc.add_heading('5.3. Hướng phát triển', level=2)
    doc.add_paragraph('- Xây dựng app di động Flutter.')
    doc.add_paragraph('- Thêm tính năng nhắc nhở hóa đơn tự động qua Email.')

    # --- PHẦN 6 ---
    doc.add_heading('PHẦN 6: KẾT LUẬN VÀ KHUYẾN NGHỊ', level=1)
    doc.add_paragraph('Dự án ExpenseAI đã ứng dụng thành công Trí tuệ nhân tạo vào quy trình nghiệp vụ thực tế. Hệ thống không chỉ đáp ứng đủ các tiêu chí quản lý thông thường mà còn đem lại trải nghiệm ưu việt cho người dùng cuối.')

    # --- PHỤ LỤC ---
    doc.add_page_break()
    doc.add_heading('PHỤ LỤC', level=1)
    doc.add_heading('Phụ lục A: Mã nguồn chính', level=2)
    doc.add_paragraph('Các tệp tin mã nguồn có sẵn trong mã nguồn đính kèm (Repository Github).')
    
    doc.add_heading('Phụ lục B: Tài liệu hướng dẫn cài đặt', level=2)
    doc.add_paragraph('1. Cài đặt Docker.')
    doc.add_paragraph('2. Chạy lệnh: docker-compose up -d --build')
    doc.add_paragraph('3. Truy cập: http://localhost:8000')

    os.makedirs(r"C:\Users\Admin\Desktop\báo cáo thu chi\docs", exist_ok=True)
    doc.save(r"C:\Users\Admin\Desktop\báo cáo thu chi\docs\Bao_Cao_Tong_Hop_ExpenseAI.docx")
    print("Báo cáo đã được tạo thành công.")

if __name__ == '__main__':
    create_report()
