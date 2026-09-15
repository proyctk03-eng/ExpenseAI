# ExpenseAI Design System Specification (DESIGN.md)
*OpenDesign Brand Contract & UI Guidelines*

> **Phiên bản:** 1.2.0  
> **Áp dụng:** Toàn bộ giao diện Web, Dashboard, Modal, Forms và Báo cáo trực quan của ExpenseAI.  
> **Triết lý thiết kế:** *Local-First, Fintech Glassmorphism, Tactile Micro-Interactions, WCAG 2.1 AA Compliant*.

---

## 1. Bảng Màu Thương Hiệu & Tokens Semantic (OKLCH / HSL)

Hệ thống màu sắc được chuẩn hóa theo ngữ nghĩa tài chính, đảm bảo độ tương phản cao trên cả nền sáng và nền tối:

```css
:root {
  /* Surface & Background (Deep Fintech Navy) */
  --color-bg-canvas: #F8FAFC;          /* Canvas sáng thanh lịch */
  --color-bg-surface: #FFFFFF;         /* Thẻ card trắng tinh khiết */
  --color-bg-surface-elevated: #FFFFFF;
  --color-sidebar-bg: #0B192C;         /* Navy tối cao cấp */
  --color-sidebar-hover: #1E3E62;
  --color-sidebar-active: #008170;

  /* Primary Accent & Brand */
  --color-primary: #0F67B1;            /* Xanh dương tài chính tin cậy */
  --color-primary-hover: #084c8d;
  --color-primary-subtle: #EBF5FF;
  --color-cyan-glow: #00D4FF;          /* Highlight công nghệ AI */

  /* Semantic Financial Colors */
  --color-income: #10B981;             /* Xanh ngọc lục bảo: Tiền vào (+ Thu) */
  --color-income-subtle: #ECFDF5;
  --color-income-border: #A7F3D0;

  --color-expense: #F43F5E;            /* Đỏ san hô rực rỡ: Tiền ra (- Chi) */
  --color-expense-subtle: #FFF1F2;
  --color-expense-border: #FECDD3;

  --color-warning: #F59E0B;            /* Hổ phách: Cảnh báo ngân sách */
  --color-warning-subtle: #FFFBEB;

  /* Neutral Typography */
  --color-text-title: #0F172A;         /* Slate 900 */
  --color-text-body: #334155;          /* Slate 700 */
  --color-text-muted: #64748B;         /* Slate 500 */
  --color-text-light: #94A3B8;         /* Slate 400 */
  --color-border: #E2E8F0;             /* Slate 200 */
  --color-border-subtle: #F1F5F9;

  /* Elevation Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(15, 23, 42, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
  --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
  --shadow-glow-ai: 0 0 16px rgba(0, 212, 255, 0.25);

  /* Radius Tokens */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```

---

## 2. Hệ Thống Typography (Phân Cấp Google Fonts)

1. **Font giao diện chính:** `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`
   - Tiêu đề Trang (H1): `24px` / `1.4` (Weight: 700)
   - Tiêu đề Khối (H2): `18px` / `1.4` (Weight: 600)
   - Văn bản thân (Body): `14px` / `1.5` (Weight: 400 & 500)
   - Chú thích & Nhãn (Caption): `12px` / `1.4` (Weight: 500, Tracking: +0.2px)
2. **Font Dữ liệu & Số tiền:** `'JetBrains Mono', 'SF Mono', Consolas, monospace`
   - Số tiền thu/chi, mã giao dịch, phần trăm: `15px` / Weight: 600. Đảm bảo các con số thẳng hàng khi hiển thị trên bảng.

---

## 3. Quy Chuẩn Chuyển Động & Phản Hồi Xúc Giác (Emil Kowalski Motion)

- **Nguyên lý:** *Chuyển động có mục đích, không lạm dụng, tôn trọng hiệu năng.*
- **Thời lượng & Easing chuẩn:**
  - `transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);` (Spring physics tự nhiên).
- **Quy định tương tác:**
  - **Nút bấm (Buttons):** Khi hover nhấc nhẹ `-1px` kèm đổ bóng tăng; khi active thu nhỏ nhẹ `scale(0.98)`.
  - **Modal (Hộp thoại):** Mở ra bằng animation `scale(0.96) -> scale(1)` kết hợp `opacity: 0 -> 1` trong `180ms`.
  - **Dòng giao dịch:** Hover làm sáng nền và hiển thị nhanh cụm thao tác (Sửa/Xóa).
  - **Skeleton Shimmer:** Hiệu ứng sóng gradient lướt qua khi đang chờ AI phân loại hoặc tải dữ liệu báo cáo.

---

## 4. Thành Phần Giao Diện Cốt Lõi (Core Components)

### 4.1. Financial Metric Card (Thẻ Chỉ Số)
- Bo góc `14px`, viền nhẹ `1px solid var(--color-border)`.
- Icon nằm trong khung tròn có màu nền subtle tương ứng (Ví dụ: Thẻ Thu nhập có icon mũi tên lên với nền xanh lá nhạt `#ECFDF5`).
- Hiển thị tỷ lệ tăng/giảm phần trăm dạng pill badge.

### 4.2. Interactive Transaction Table (Bảng Giao Dịch)
- Cột số tiền căn phải (Right-align) và dùng font JetBrains Mono.
- Phân biệt màu tuyệt đối: `+ X.XXX.XXX ₫` (Màu xanh lục `#10B981`) và `- X.XXX.XXX ₫` (Màu đỏ `#F43F5E`).
- Cột AI Prediction hiển thị biểu tượng lấp lánh (Sparkle ✨) kèm độ tin cậy.

### 4.3. AI Advice Widget (Khối Tư Vấn Thông Minh)
- Viền gradient tinh tế `linear-gradient(135deg, rgba(0,212,255,0.4), rgba(15,103,177,0.2))`.
- Có huy hiệu *"Powered by Invisible AI"* và hỗ trợ bộ nhớ người dùng (User Memory Enabled).

---

## 5. Tiêu Chuẩn Tiếp Cận & Khả Dụng (Accessibility / WCAG)
- Mọi cặp màu chữ và nền đều đảm bảo tỷ lệ tương phản tối thiểu **4.5:1** (tiêu chuẩn WCAG 2.1 AA).
- Mọi nút bấm và trường nhập liệu đều có trạng thái `:focus-visible` với vòng hào quang xanh `outline: 2px solid var(--color-primary); outline-offset: 2px;`.
