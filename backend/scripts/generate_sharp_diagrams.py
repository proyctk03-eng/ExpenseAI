"""
Script vẽ sơ đồ tuần tự (Sequence Diagram) chuẩn Publication-Grade:
- Hình 2.3: Phân loại danh mục tự động với AI
- Hình 2.4: Cố vấn tài chính thông minh
Đảm bảo phông chữ TO, RÕ RÀNG, ĐẬM NÉT, màu sắc chuẩn học thuật (Navy, Indigo, Violet, Emerald).
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# Cấu hình font hệ thống
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Helvetica']

def draw_sequence_2_3(output_path):
    fig, ax = plt.subplots(figsize=(16, 11.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 118)
    ax.axis('off')
    
    # 6 Lifelines X-positions
    x_pos = [10, 28, 47, 66, 85, 100]
    lifelines = [
        ("Người dùng\n(User)", "#1E293B", "#F8FAFC"),
        ("Giao diện Web\n(Frontend)", "#2563EB", "#EFF6FF"),
        ("FastAPI Router\n(/api/transactions)", "#0F766E", "#F0FDFA"),
        ("Service AI\n(Classifier)", "#7C3AED", "#F5F3FF"),
        ("PostgreSQL\n(Database)", "#0284C7", "#F0F9FF"),
        ("Cloud AI\n(OpenAI / Gemini)", "#9333EA", "#FAF5FF")
    ]
    
    y_top = 108
    y_bottom = 6
    
    # Vẽ Header Lifelines
    for x, (name, border_col, bg_col) in zip(x_pos, lifelines):
        # Header Box
        box = patches.FancyBboxPatch((x - 6.5, y_top - 4), 13, 8,
                                     boxstyle="round,pad=0.5",
                                     ec=border_col, fc=bg_col, lw=2.2)
        ax.add_patch(box)
        ax.text(x, y_top, name, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color=border_col)
        
        # Đường thẳng đứng (Dotted Lifeline)
        ax.plot([x, x], [y_top - 4.5, y_bottom + 4.5],
                linestyle='--', color="#94A3B8", lw=1.8, zorder=1)
        
        # Footer Box
        fbox = patches.FancyBboxPatch((x - 6.5, y_bottom - 4), 13, 8,
                                      boxstyle="round,pad=0.5",
                                      ec=border_col, fc=bg_col, lw=2.2)
        ax.add_patch(fbox)
        ax.text(x, y_bottom, name, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color=border_col)

    # Danh sách các bước thông điệp (Steps)
    steps = [
        (98, 0, 1, '1. Nhập mô tả ("Ăn bún chả 35k"), số tiền', False, "#1E293B"),
        (91, 1, 2, '2. POST /api/transactions/ (danh mục để trống)', False, "#2563EB"),
        (84, 2, 2, '3. Kiểm tra category_id == None', 'self', "#0F766E"),
        (77, 2, 3, '4. classify("Ăn bún chả 35k")', False, "#0F766E"),
        (70, 3, 5, '5. Gọi API AI (response_format="json_object")', False, "#7C3AED"),
        (63, 5, 3, '6. Trả JSON: {"category": "Ăn uống", "confidence": 0.96}', True, "#9333EA"),
        (56, 3, 2, '7. Trả kết quả phân tích AI', True, "#7C3AED"),
        (49, 2, 4, '8. Truy vấn Category khớp "Ăn uống"', False, "#0F766E"),
        (42, 4, 2, '9. Trả về Category ID = 1', True, "#0284C7"),
        (35, 2, 4, '10. INSERT INTO transactions & ai_predictions', False, "#0F766E"),
        (28, 4, 2, '11. Commit thành công (Atomic Transaction)', True, "#0284C7"),
        (21, 2, 1, '12. HTTP 201 Created (Kèm danh mục tự động)', True, "#059669"),
        (14, 1, 0, '13. Hiển thị Toast thông báo & Cập nhật Dashboard', True, "#059669"),
    ]
    
    for y, src, dst, text, is_return, col in steps:
        if dst == 'self':
            x_self = x_pos[src]
            ax.annotate('', xy=(x_self, y - 2.5), xytext=(x_self + 4.5, y - 2.5),
                        arrowprops=dict(arrowstyle="->", lw=2.0, color=col))
            ax.plot([x_self, x_self + 4.5, x_self + 4.5], [y, y, y - 2.5], color=col, lw=2.0)
            ax.text(x_self + 5.5, y - 1.2, text, ha='left', va='center',
                    fontsize=11.2, fontweight='bold', color=col,
                    bbox=dict(boxstyle="round,pad=0.25", fc="#F8FAFC", ec="#CBD5E1", lw=1))
        else:
            x1 = x_pos[src]
            x2 = x_pos[dst]
            linestyle = '--' if is_return else '-'
            arrowstyle = "-|>" if not is_return else "->"
            
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle=arrowstyle,
                                        linestyle=linestyle,
                                        lw=2.2, color=col))
            # Text label
            x_mid = (x1 + x2) / 2
            ax.text(x_mid, y + 1.6, text, ha='center', va='bottom',
                    fontsize=11.5, fontweight='bold', color=col,
                    bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#CBD5E1", lw=1.2, alpha=0.95))
            
            # Activation bar trên lifeline
            ax.plot([x2, x2], [y + 1.2, y - 1.2], lw=7, color=col, solid_capstyle='round', zorder=3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print(f"Generated {output_path} successfully!")

def draw_sequence_2_4(output_path):
    fig, ax = plt.subplots(figsize=(16, 10.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 105)
    ax.axis('off')
    
    x_pos = [10, 28, 47, 66, 85, 100]
    lifelines = [
        ("Người dùng\n(User)", "#1E293B", "#F8FAFC"),
        ("Giao diện Web\n(Dashboard)", "#2563EB", "#EFF6FF"),
        ("FastAPI Router\n(/api/advice)", "#0F766E", "#F0FDFA"),
        ("Service AI\n(Financial Advisor)", "#7C3AED", "#F5F3FF"),
        ("PostgreSQL\n(Database)", "#0284C7", "#F0F9FF"),
        ("Cloud AI\n(OpenAI / Gemini)", "#9333EA", "#FAF5FF")
    ]
    
    y_top = 96
    y_bottom = 6
    
    # Vẽ Header Lifelines
    for x, (name, border_col, bg_col) in zip(x_pos, lifelines):
        box = patches.FancyBboxPatch((x - 6.5, y_top - 4), 13, 8,
                                     boxstyle="round,pad=0.5",
                                     ec=border_col, fc=bg_col, lw=2.2)
        ax.add_patch(box)
        ax.text(x, y_top, name, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color=border_col)
        
        ax.plot([x, x], [y_top - 4.5, y_bottom + 4.5],
                linestyle='--', color="#94A3B8", lw=1.8, zorder=1)
        
        fbox = patches.FancyBboxPatch((x - 6.5, y_bottom - 4), 13, 8,
                                      boxstyle="round,pad=0.5",
                                      ec=border_col, fc=bg_col, lw=2.2)
        ax.add_patch(fbox)
        ax.text(x, y_bottom, name, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color=border_col)

    # Danh sách các bước
    steps = [
        (86, 0, 1, '1. Nhấn nút "Nhận lời khuyên tài chính"', False, "#1E293B"),
        (79, 1, 2, '2. POST /api/advice/generate', False, "#2563EB"),
        (72, 2, 4, '3. Truy vấn tổng hợp thu chi 90 ngày của User', False, "#0F766E"),
        (65, 4, 2, '4. Trả Dataset tổng hợp: {"Ăn uống": 3.8M, "Phòng trọ": 2.5M}', True, "#0284C7"),
        (58, 2, 3, '5. get_financial_advice(summary_data)', False, "#0F766E"),
        (51, 3, 3, '6. Tạo Prompt theo quy tắc tài chính 50/30/20', 'self', "#7C3AED"),
        (44, 3, 5, '7. Gọi API AI (max_tokens=300, system context)', False, "#7C3AED"),
        (37, 5, 3, '8. Trả văn bản tư vấn cá nhân hóa (3 phần súc tích)', True, "#9333EA"),
        (30, 3, 2, '9. Trả kết quả tư vấn hoàn chỉnh', True, "#7C3AED"),
        (23, 2, 1, '10. HTTP 200 OK (Nội dung lời khuyên)', True, "#059669"),
        (16, 1, 0, '11. Hiển thị Card Lời khuyên nổi bật trên Dashboard', True, "#059669"),
    ]
    
    for y, src, dst, text, is_return, col in steps:
        if dst == 'self':
            x_self = x_pos[src]
            ax.annotate('', xy=(x_self, y - 2.5), xytext=(x_self + 4.5, y - 2.5),
                        arrowprops=dict(arrowstyle="->", lw=2.0, color=col))
            ax.plot([x_self, x_self + 4.5, x_self + 4.5], [y, y, y - 2.5], color=col, lw=2.0)
            ax.text(x_self + 5.5, y - 1.2, text, ha='left', va='center',
                    fontsize=11.2, fontweight='bold', color=col,
                    bbox=dict(boxstyle="round,pad=0.25", fc="#F8FAFC", ec="#CBD5E1", lw=1))
        else:
            x1 = x_pos[src]
            x2 = x_pos[dst]
            linestyle = '--' if is_return else '-'
            arrowstyle = "-|>" if not is_return else "->"
            
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle=arrowstyle,
                                        linestyle=linestyle,
                                        lw=2.2, color=col))
            x_mid = (x1 + x2) / 2
            ax.text(x_mid, y + 1.6, text, ha='center', va='bottom',
                    fontsize=11.5, fontweight='bold', color=col,
                    bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#CBD5E1", lw=1.2, alpha=0.95))
            ax.plot([x2, x2], [y + 1.2, y - 1.2], lw=7, color=col, solid_capstyle='round', zorder=3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print(f"Generated {output_path} successfully!")

if __name__ == "__main__":
    draw_sequence_2_3("c:/Users/dathao/Downloads/AI/ExpenseAI/scratch/sharp_hinh_2_3.png")
    draw_sequence_2_4("c:/Users/dathao/Downloads/AI/ExpenseAI/scratch/sharp_hinh_2_4.png")
