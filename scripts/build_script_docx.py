"""
Script xuất bản Kich_Ban_Demo_Thuyet_Trinh_Nhom_02.docx chuẩn học thuật ICTU.
"""
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

NAVY_BLUE = RGBColor(26, 54, 93)     # #1A365D
SLATE_GRAY = RGBColor(71, 85, 105)   # #475569
DARK_TEXT = RGBColor(30, 41, 59)     # #1E293B

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color_hex="CCCCCC"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color_hex}"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/><w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="none"/></w:tblBorders>')
    tblPr.append(borders)

def build_script_docx():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(3.5)
        section.right_margin = Cm(2.0)

    # Header
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_top = p_top.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG (ICTU)\nKHOA CÔNG NGHỆ THÔNG TIN")
    r_top.font.name = "Times New Roman"
    r_top.font.size = Pt(12)
    r_top.font.bold = True
    r_top.font.color.rgb = NAVY_BLUE

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("KỊCH BẢN THUYẾT TRÌNH VÀ DEMO BẢO VỆ ĐỒ ÁN - NHÓM 02")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(16)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY_BLUE

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(20)
    r_sub = p_sub.add_run("Thời lượng chuẩn: 7 phút (5 phút trình bày & demo + 2 phút vấn đáp phản biện)")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = SLATE_GRAY

    # Timeline Table
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(12)
    p_h1.paragraph_format.space_after = Pt(6)
    r_h1 = p_h1.add_run("1. DÒNG THỜI GIAN THỰC HIỆN BẢO VỆ (TIMELINE)")
    r_h1.font.name = "Times New Roman"
    r_h1.font.size = Pt(13)
    r_h1.font.bold = True
    r_h1.font.color.rgb = NAVY_BLUE

    table = doc.add_table(rows=6, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    headers = ["Thời gian", "Phần nội dung", "Người trình bày"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        set_cell_background(cell, "1A365D")
        set_cell_margins(cell, 100, 100, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data = [
        ["00:00 - 01:30", "Phần 1 - Đặt vấn đề, Bối cảnh & Kiến trúc Hệ thống", "Nguyễn Tuấn Đạt (Trưởng nhóm)"],
        ["01:30 - 04:00", "Phần 2 - Demo Nghiệp vụ cốt lõi & Giao diện người dùng", "Phàn Ngọc Anh (Phó nhóm)"],
        ["04:00 - 05:30", "Phần 3 - Demo Tích hợp AI, Tối ưu Prompt & Agent Memory tự học", "Nguyễn Tuấn Đạt (Trưởng nhóm)"],
        ["05:30 - 07:00", "Phần 4 - Minh chứng Kiểm thử 36/36 Test Pytest & CI/CD GitHub Actions", "Cả nhóm (Đạt & Anh)"],
        ["Sau 07:00", "Phần 5 - Vấn đáp và Trả lời phản biện trước Hội đồng", "Cả nhóm phối hợp"]
    ]
    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            set_cell_margins(cell, 80, 80, 80, 80)
            if row_idx % 2 == 0:
                set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)

    # Detailed Speech
    sections = [
        ("PHẦN 1: ĐẶT VẤN ĐỀ & KIẾN TRÚC HỆ THỐNG (1.5 phút) - Nguyễn Tuấn Đạt",
         "• Lời chào mở đầu: Kính thưa quý Thầy Cô trong Hội đồng chấm thi! Em tên là Nguyễn Tuấn Đạt, cùng bạn Phàn Ngọc Anh là thành viên Nhóm 02. Hôm nay, nhóm chúng em xin phép được báo cáo và bảo vệ đồ án kết thúc học phần với đề tài: ExpenseAI - Hệ thống Quản lý Chi tiêu Cá nhân thông minh tích hợp Trí tuệ Nhân tạo.\n"
         "• Vấn đề thực tế: Trong thực tế, hơn 85% người dùng từ bỏ việc ghi chép chi tiêu sau 2 tuần vì thủ công rườm rà. ExpenseAI giải quyết triệt để vấn đề này bằng mô hình Invisible AI và Agent Memory tự học.\n"
         "• Kiến trúc 3 tầng: Backend FastAPI hiệu năng cao, CSDL PostgreSQL 15 chuẩn 3NF (8 bảng thực thể) kết hợp SQLAlchemy 2.0, giao diện OpenDesign Glassmorphism và tích hợp OpenAI GPT."),

        ("PHẦN 2: DEMO NGHIỆP VỤ CỐT LÕI & GIAO DIỆN (2.5 phút) - Phàn Ngọc Anh",
         "• Đăng nhập & Seed Data 30 ngày: Thao tác đăng nhập tài khoản sinh viên đã nạp sẵn 30 ngày dữ liệu chi tiêu thực tế.\n"
         "• Trình diễn Bộ lọc & Tìm kiếm: Gõ từ khóa 'phở' lập tức lọc ra giao dịch ăn sáng; lọc khoảng ngày mượt mà qua Fetch API không reload trang.\n"
         "• Thao tác Chỉnh sửa & Quản lý Danh mục: Bấm nút Sửa mở Modal Popup cập nhật số tiền tức thì; mở Modal Thêm danh mục mới trong trang Cài đặt."),

        ("PHẦN 3: DEMO TÍCH HỢP AI, PROMPT & BỘ NHỚ TỰ HỌC (1.5 phút) - Nguyễn Tuấn Đạt",
         "• Demo Phân loại AI: Nhập mô tả 'Ăn bún chả 40k' không chọn danh mục -> AI ngầm tự động nhận diện và gán vào 'Ăn uống'.\n"
         "• Đột phá Agent Memory: Sửa danh mục giao dịch -> Hệ thống tự động ghi nhớ quy tắc L1 Fact Memory. Lần sau nhập lại nhận diện đúng ngay với 0ms và 0 token tiêu tốn.\n"
         "• Cơ chế Heuristic Fallback: Thử nghiệm ngắt kết nối API -> Hệ thống tự động kích hoạt bộ quy tắc nội bộ, bảo đảm không bao giờ lỗi."),

        ("PHẦN 4: MINH CHỨNG KIỂM THỬ 36/36 TEST & CI/CD GITHUB (1.0 phút) - Cả Nhóm",
         "• Minh chứng Pytest: Chạy pytest tại terminal chứng minh 36/36 test cases đạt kết quả xanh (PASS 100%).\n"
         "• Minh chứng CI/CD: Mở giao diện GitHub Actions chứng minh pipeline tự động chạy kiểm thử trên 3 phiên bản Python và quét bảo mật Trivy đạt tích xanh (Success)."),

        ("PHẦN 5: BỘ CÂU HỎI PHẢN BIỆN HỘI ĐỒNG & CÂU TRẢ LỜI MẪU",
         "1. Câu hỏi: Nếu mất kết nối Internet hoặc OpenAI lỗi thì hệ thống xử lý thế nào?\n"
         "   -> Trả lời: Hệ thống có cơ chế Fallback nội bộ kết hợp L1 Fact Memory hoạt động 100% offline không gián đoạn.\n"
         "2. Câu hỏi: Làm sao bảo vệ quyền riêng tư người dùng khi dùng AI?\n"
         "   -> Trả lời: Áp dụng Privacy-by-Design, chỉ gửi dữ liệu số tổng hợp vô danh lên OpenAI, không gửi lịch sử thô.\n"
         "3. Câu hỏi: AI có học được từ lỗi sai không?\n"
         "   -> Trả lời: Có, hệ thống ứng dụng TencentDB Agent Memory ghi nhận phản hồi của người dùng vào bảng user_memory_rules.")
    ]

    for title, content in sections:
        p_sec = doc.add_paragraph()
        p_sec.paragraph_format.space_before = Pt(14)
        p_sec.paragraph_format.space_after = Pt(4)
        p_sec.paragraph_format.keep_with_next = True
        r_s = p_sec.add_run(title)
        r_s.font.name = "Times New Roman"
        r_s.font.size = Pt(13)
        r_s.font.bold = True
        r_s.font.color.rgb = NAVY_BLUE

        p_c = doc.add_paragraph()
        p_c.paragraph_format.line_spacing = 1.3
        p_c.paragraph_format.space_after = Pt(6)
        p_c.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_c = p_c.add_run(content)
        r_c.font.name = "Times New Roman"
        r_c.font.size = Pt(11.5)
        r_c.font.color.rgb = DARK_TEXT

    doc.save("docs/Kich_Ban_Demo_Thuyet_Trinh_Nhom_02.docx")
    print("Exported docs/Kich_Ban_Demo_Thuyet_Trinh_Nhom_02.docx successfully!")

if __name__ == "__main__":
    build_script_docx()
