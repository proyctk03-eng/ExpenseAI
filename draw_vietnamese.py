import os
import base64
import zlib
import urllib.request

output_dir = r'C:\Users\dathao\Desktop\ExpenseAI_Diagrams_Pro'
os.makedirs(output_dir, exist_ok=True)

def gen(source, d_type, name):
    try:
        compressed = zlib.compress(source.encode('utf-8'), 9)
        b64 = base64.urlsafe_b64encode(compressed).decode('ascii')
        url = f'https://kroki.io/{d_type}/png/{b64}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            with open(os.path.join(output_dir, name), 'wb') as f:
                f.write(res.read())
        print(f'Generated: {name}')
    except Exception as e:
        print(f'Failed {name}: {e}')

uc_finance = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
left to right direction

actor "người dùng cá nhân" as user
actor "quản trị viên" as admin

package "phân hệ tài chính cá nhân" {
  usecase "đăng ký và đăng nhập" as UC1
  usecase "ghi nhận thu chi" as UC2
  usecase "quản lý danh mục" as UC3
  usecase "thiết lập ngân sách" as UC4
  usecase "xem báo cáo thống kê" as UC5
}

user --> UC1
user --> UC2
user --> UC3
user --> UC4
user --> UC5

admin --> UC1
admin --> UC3
@enduml"""

uc_ai = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
left to right direction

actor "người dùng cá nhân" as user
actor "Google Gemini-3.6-Flash" as ai

package "phân hệ trợ lý thông minh" {
  usecase "nhập liệu bằng câu thoại" as UC1
  usecase "trích xuất và phân loại dữ liệu" as UC2
  usecase "cảnh báo vượt ngân sách" as UC3
  usecase "cố vấn và đánh giá tài chính" as UC4
}

user --> UC1
UC1 .> UC2 : bao gồm
ai --> UC2
ai --> UC4
user --> UC3
user --> UC4
@enduml"""

erd_rbac = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
hide circle
hide empty methods

entity "nguoi_dung" as users {
  * ma_so_dinh_danh
  --
  ten_dang_nhap
  dia_chi_email
  mat_khau_ma_hoa
}

entity "vai_tro" as roles {
  * ma_so_dinh_danh
  --
  ten_vai_tro
}

entity "quyen_han" as perms {
  * ma_so_dinh_danh
  --
  tai_nguyen
  hanh_dong
}

entity "nguoi_dung_vai_tro" as ur {
  * nguoi_dung_id
  * vai_tro_id
}

entity "vai_tro_quyen_han" as rp {
  * vai_tro_id
  * quyen_han_id
}

users "1" -- "n" ur
roles "1" -- "n" ur
roles "1" -- "n" rp
perms "1" -- "n" rp

ur -[hidden]-> rp
@enduml"""

erd_tx = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
hide circle
hide empty methods

entity "nguoi_dung" as users {
  * ma_so_dinh_danh
  --
  ten_dang_nhap
}

entity "danh_muc" as categories {
  * ma_so_dinh_danh
  --
  ten_danh_muc
  loai_danh_muc
}

entity "giao_dich" as transactions {
  * ma_so_dinh_danh
  --
  so_tien
  ghi_chu
  ngay_giao_dich
}

entity "ngan_sach" as budgets {
  * ma_so_dinh_danh
  --
  han_muc
  thang
  nam
}

entity "du_doan_ai" as ai_preds {
  * ma_so_dinh_danh
  --
  cau_lenh_goc
  danh_muc_du_doan
  do_tin_cay
}

users "1" -- "n" categories
users "1" -- "n" transactions
users "1" -- "n" budgets
users "1" -- "n" ai_preds

categories "1" -- "n" transactions
categories "1" -- "n" budgets
@enduml"""

activity_ai = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none

|người dùng|
start
:nhập câu lệnh thu chi;
|hệ thống máy chủ|
:tiếp nhận yêu cầu;
:gửi dữ liệu tới AI;
|Google Gemini-3.6-Flash|
:phân tích ngữ nghĩa;
:trích xuất số tiền và danh mục;
:trả về dữ liệu định dạng JSON;
|hệ thống máy chủ|
if (độ tin cậy lớn hơn không phẩy sáu?) then (có)
  if (số tiền hợp lệ?) then (có)
    :lưu vào cơ sở dữ liệu;
    :tính toán lại tổng thu chi;
  else (không)
    :trả về thông báo lỗi;
    stop
  endif
else (không)
  :đánh dấu yêu cầu xác nhận thủ công;
endif
|người dùng|
:nhận thông báo thành công;
stop
@enduml"""

seq_ai = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
skinparam sequenceMessageAlign center

actor "ứng dụng khách" as client
participant "cổng giao tiếp" as api
participant "dịch vụ xác thực" as auth
participant "dịch vụ giao dịch" as tx
participant "Google Gemini-3.6-Flash" as ai
database "cơ sở dữ liệu" as db

client -> api: gửi yêu cầu phân tích
api -> auth: kiểm tra mã thông báo
alt mã thông báo hợp lệ
    auth --> api: xác nhận danh tính
    api -> tx: chuyển tiếp yêu cầu
    tx -> ai: gọi dịch vụ phân tích
    activate ai
    ai --> tx: trả về số tiền và danh mục
    deactivate ai
    tx -> db: tìm kiếm mã danh mục
    db --> tx: trả về kết quả
    tx -> db: lưu giao dịch mới
    activate db
    db --> tx: lưu thành công
    deactivate db
    tx --> api: báo cáo thành công
    api --> client: trả kết quả giao dịch
else mã thông báo sai
    auth --> api: từ chối truy cập
    api --> client: trả lỗi xác thực
end
@enduml"""

uc_tongquat = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
left to right direction

actor "người dùng" as user
actor "quản trị viên" as admin
actor "Google Gemini-3.6-Flash" as ai

rectangle "hệ thống quản lý tài chính" {
  usecase "quản lý tài khoản" as UC1
  usecase "quản lý giao dịch" as UC2
  usecase "quản lý danh mục và ngân sách" as UC3
  usecase "báo cáo thống kê" as UC4
  usecase "trợ lý cố vấn" as UC5
}

user --> UC1
user --> UC2
user --> UC3
user --> UC4
user --> UC5

admin --> UC1
admin --> UC3

UC2 ..> ai : gửi yêu cầu
UC5 ..> ai : gửi yêu cầu
@enduml"""

domain_model = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
hide circle
hide empty methods

class "người dùng" as User {
  họ tên
  địa chỉ thư điện tử
}
class "tài khoản" as Account {
  số dư hiện tại
}
class "giao dịch" as Transaction {
  số tiền
  ngày giao dịch
  ghi chú
}
class "danh mục" as Category {
  tên danh mục
  loại thu chi
}
class "ngân sách" as Budget {
  hạn mức
  tháng năm
}
class "dự đoán từ AI" as AIPrediction {
  độ tin cậy
}

User "1" -- "1" Account : sở hữu
User "1" -- "n" Transaction : thực hiện
User "1" -- "n" Category : tạo
User "1" -- "n" Budget : thiết lập
Transaction "n" -- "1" Category : thuộc về
Budget "n" -- "1" Category : áp dụng cho
Transaction "1" -- "1" AIPrediction : được phân loại bởi
@enduml"""

architecture = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none

node "tầng trình diễn" {
  [trình duyệt ứng dụng] as client
}

node "tầng ứng dụng" {
  [cổng giao tiếp] as gateway
  [dịch vụ xác thực] as auth
  [dịch vụ giao dịch] as tx
  [dịch vụ AI] as aiservice
  [dịch vụ báo cáo] as report
}

node "tầng dữ liệu" {
  database "cơ sở dữ liệu chính" as db
  database "bộ nhớ đệm" as cache
}

cloud "dịch vụ bên ngoài" {
  [Google Gemini-3.6-Flash] as gemini
}

client --> gateway : giao thức mạng
gateway --> auth
gateway --> tx
gateway --> report

tx --> aiservice
aiservice --> gemini : đường truyền bảo mật

tx --> db
report --> db
auth --> cache
@enduml"""

class_diagram = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none
hide circle

class "LopNguoiDung" as User {
  + ma_so_dinh_danh
  + ten_dang_nhap
  + dia_chi_thu_dien_tu
  + dang_nhap()
  + dang_xuat()
}
class "LopGiaoDich" as Transaction {
  + ma_so_dinh_danh
  + luong_tien
  + mo_ta_chi_tiet
  + thoi_gian
  + tao_moi()
  + cap_nhat()
  + xoa_bo()
}
class "LopDanhMuc" as Category {
  + ma_so_dinh_danh
  + ten_goi
  + phan_loai
  + them_danh_muc()
}
class "LopXuLyAI" as AIProcessor {
  + phan_tich_cau_lenh()
  + nhan_loi_khuyen_tai_chinh()
}

User "1" *-- "n" Transaction
User "1" *-- "n" Category
Category "1" o-- "n" Transaction
Transaction ..> AIProcessor : gọi hàm
@enduml"""

deployment = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none

node "thiết bị người dùng" {
  node "trình duyệt" {
    artifact "giao diện trực quan" as fe
  }
}

node "máy chủ đám mây" {
  node "máy chủ điều phối" {
    [bộ định tuyến đảo ngược] as proxy
  }
  node "máy chủ xử lý" {
    artifact "mã nguồn phần mềm" as be
  }
  node "máy chủ lưu trữ" {
    database "hệ quản trị cơ sở dữ liệu" as db
  }
}

cloud "đám mây AI" {
  [Google Gemini-3.6-Flash] as ai
}

fe --> proxy : giao thức bảo mật
proxy --> be : mạng nội bộ
be --> db : kết nối dữ liệu
be --> ai : kết nối dịch vụ
@enduml"""

component = """@startuml
skinparam monochrome true
skinparam linetype ortho
skinparam textTransform none

package "thành phần giao diện" {
  [các khối hiển thị] as ui
  [bộ quản lý trạng thái] as state
  [trình gọi dịch vụ] as api
}

package "thành phần máy chủ" {
  [bộ định tuyến yêu cầu] as router
  [bộ xử lý nghiệp vụ] as service
  [bộ tương tác dữ liệu] as repo
  [bộ kiểm tra cấu trúc] as schema
}

database "hệ quản trị dữ liệu" as db

ui --> state
state --> api
api --> router : trao đổi thông tin
router --> schema : xác thực
router --> service
service --> repo
repo --> db : truy vấn
@enduml"""

gen(uc_finance, 'plantuml', '1_UseCase_TaiChinh.png')
gen(uc_ai, 'plantuml', '2_UseCase_AI.png')
gen(erd_rbac, 'plantuml', '3_ERD_RBAC.png')
gen(erd_tx, 'plantuml', '4_ERD_GiaoDich.png')
gen(activity_ai, 'plantuml', '5_Activity_AI_Flow.png')
gen(seq_ai, 'plantuml', '6_Sequence_Auth_AI.png')
gen(uc_tongquat, 'plantuml', '7_UseCase_TongQuat.png')
gen(domain_model, 'plantuml', '8_Domain_Model.png')
gen(architecture, 'plantuml', '9_Architecture_3Tier.png')
gen(class_diagram, 'plantuml', '10_Class_Diagram.png')
gen(deployment, 'plantuml', '11_Deployment.png')
gen(component, 'plantuml', '12_Component_Diagram.png')
