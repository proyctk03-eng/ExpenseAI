import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

def create_pdf(output_path):
    # Register fonts for Vietnamese
    try:
        pdfmetrics.registerFont(TTFont('TimesNewRoman', 'C:\\Windows\\Fonts\\times.ttf'))
        pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', 'C:\\Windows\\Fonts\\timesbd.ttf'))
        pdfmetrics.registerFont(TTFont('TimesNewRoman-Italic', 'C:\\Windows\\Fonts\\timesi.ttf'))
    except Exception as e:
        print(f"Lỗi nạp font: {e}")
        return

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName='TimesNewRoman-Bold',
        fontSize=20,
        spaceAfter=30,
        textColor=HexColor('#8B0000')
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontName='TimesNewRoman-Bold',
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=HexColor('#003366')
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontName='TimesNewRoman-Bold',
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='TimesNewRoman',
        fontSize=12,
        spaceAfter=8,
        leading=16
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=normal_style,
        leftIndent=20
    )

    story = []

    # Title
    story.append(Paragraph("BÁO CÁO PHẢN BIỆN ĐỒ ÁN (GRILLING REPORT)", title_style))
    story.append(Paragraph("Dự án: Hệ thống Quản lý Thu Chi ExpenseAI - ICTU", h2_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Tài liệu này đóng vai trò như một Hội đồng bảo vệ đồ án, đưa ra các nhận xét và phản biện sắc bén nhất về dự án ExpenseAI.", normal_style))
    story.append(Spacer(1, 12))

    # Section 1
    story.append(Paragraph("1. Phản biện Đề tài & Logic Code (Web & Backend)", h1_style))
    
    story.append(Paragraph("Rủi ro về AI Hallucination (Ảo giác AI):", h2_style))
    story.append(Paragraph("Dự án lạm dụng LLM để nhận diện và tư vấn (ai_advice.py, ai_classifier.py). Tuy nhiên, Prompt hiện tại chưa có cơ chế rào cản pháp lý (Legal Disclaimer). Việc giao quyền tư vấn tài chính hoàn toàn cho AI mà không có risk mitigation (giảm thiểu rủi ro) là một điểm yếu lớn. Nếu AI khuyên người dùng đầu tư sai, hệ thống hoàn toàn không có cơ chế chặn.", normal_style))

    story.append(Paragraph("Cấu trúc Backend FastAPI:", h2_style))
    story.append(Paragraph("FastAPI mạnh về xử lý bất đồng bộ. Tuy nhiên, việc tích hợp logic sinh Text của AI có thể trở thành 'Nút thắt cổ chai' (Bottleneck) nếu nhiều request đổ vào cùng lúc. Thiết kế hiện tại cần được chuyển đổi sang message queue (như Celery/RabbitMQ) hoặc Background Tasks một cách triệt để thay vì chờ AI trả lời trực tiếp trong HTTP request.", normal_style))

    story.append(Paragraph("Bảo mật & Triển khai:", h2_style))
    story.append(Paragraph("Cấu hình Docker (docker-compose.yml) trước đó đã bộc lộ điểm yếu bảo mật khi public trực tiếp port của DB/Redis. Dù đã được vá lại, điều này cho thấy kiến trúc ban đầu thiếu tư duy 'Zero-Trust'. Việc lưu trữ API Keys trong .env mà không qua Secret Manager cũng là một rủi ro khi scale (mở rộng).", normal_style))

    # Section 2
    story.append(Paragraph("2. Phản biện Tài liệu Báo cáo", h1_style))
    story.append(Paragraph("Tính nhất quán & Tối ưu dung lượng:", h2_style))
    story.append(Paragraph("File Word báo cáo có dung lượng xấp xỉ 3MB cho khoảng 50 trang là không tối ưu. Điều này chứng tỏ hình ảnh minh họa đã được copy-paste thẳng từ clipboard vào tài liệu thay vì nén (compress) hoặc chèn (insert) file chuẩn. Hậu quả là làm phình to kích thước vô ích.", normal_style))

    story.append(Paragraph("Văn phong & Lạm dụng thuật ngữ:", h2_style))
    story.append(Paragraph("Sự phụ thuộc vào AI trong quá trình soạn báo cáo dẫn đến việc lạm dụng các từ nối sáo rỗng ('Nhìn chung', 'Tóm lại') và dịch word-by-word các thuật ngữ chuyên ngành. Cấu trúc câu bị đều đều (monotonous) và thiếu những trải nghiệm thực chiến ('Qua triển khai thực tế...').", normal_style))

    # Section 3
    story.append(Paragraph("3. Phản biện Hình ảnh & UI/UX", h1_style))
    story.append(Paragraph("Chất lượng ảnh báo cáo:", h2_style))
    story.append(Paragraph("Qua kiểm tra các file ảnh (.png, .jpg) trong thư mục, một số ảnh sơ đồ (UML/ERD) có nền trắng nhưng khi in ấn hoặc xuất PDF có thể gặp tình trạng nhòe chữ (pixelated). Lẽ ra nên dùng định dạng SVG hoặc xuất với độ phân giải cao hơn (300 DPI).", normal_style))

    story.append(Paragraph("Tính đồng bộ Giao diện:", h2_style))
    story.append(Paragraph("Giao diện UI (hiển thị qua các Screenshot) còn phụ thuộc nhiều vào Bootstrap/Tailwind cơ bản. Bảng màu chưa thực sự bứt phá và mang lại cảm giác 'Premium' như một sản phẩm FinTech chuyên nghiệp.", normal_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph("--- KẾT THÚC BÁO CÁO PHẢN BIỆN ---", ParagraphStyle('Center', parent=normal_style, alignment=1)))

    doc.build(story)
    print(f"Đã tạo thành công {output_path}")

if __name__ == "__main__":
    create_pdf(r"C:\Users\dathao\Desktop\Bao_Cao_Phan_Bien_ExpenseAI.pdf")
