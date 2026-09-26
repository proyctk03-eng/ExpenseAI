import os
import base64
import zlib
import urllib.request
from urllib.error import HTTPError

output_dir = r'C:\Users\dathao\Desktop\ExpenseAI_Diagrams_Pro'
os.makedirs(output_dir, exist_ok=True)

def generate_diagram(source, diagram_type, filename):
    try:
        compressed = zlib.compress(source.encode('utf-8'), 9)
        b64 = base64.urlsafe_b64encode(compressed).decode('ascii')
        url = f'https://kroki.io/{diagram_type}/png/{b64}'
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
            
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(img_data)
        print(f'Generated: {filename}')
    except Exception as e:
        print(f'Failed to generate {filename}: {e}')

uc_finance = """@startuml
skinparam handwritten false
skinparam monochrome true
skinparam packageStyle rectangle
left to right direction
actor "Người dùng cá nhân" as user
actor "Quản trị viên" as admin

package "Phân hệ Tài chính cá nhân" {
  usecase "Đăng ký/Đăng nhập" as UC1
  usecase "Ghi nhận thu chi" as UC2
  usecase "Quản lý danh mục" as UC3
  usecase "Thiết lập ngân sách" as UC4
  usecase "Xem báo cáo thống kê" as UC5
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
left to right direction
actor "Người dùng cá nhân" as user
actor "Google Gemini AI" as ai

package "Phân hệ Trợ lý thông minh" {
  usecase "Nhập liệu bằng câu thoại" as UC1
  usecase "Trích xuất & Phân loại dữ liệu" as UC2
  usecase "Cảnh báo vượt ngân sách" as UC3
  usecase "Cố vấn & Đánh giá tài chính" as UC4
}

user --> UC1
UC1 .> UC2 : <<include>>
ai --> UC2
ai --> UC4
user --> UC3
user --> UC4
@enduml"""

erd_rbac = """erDiagram
    USERS ||--o{ USER_ROLES : has
    ROLES ||--o{ USER_ROLES : contains
    ROLES ||--o{ ROLE_PERMISSIONS : has
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : contains

    USERS {
        int id PK
        string username
        string email
        string hashed_password
    }
    ROLES {
        int id PK
        string name
    }
    PERMISSIONS {
        int id PK
        string resource
        string action
    }"""

erd_tx = """erDiagram
    USERS ||--o{ CATEGORIES : creates
    USERS ||--o{ TRANSACTIONS : makes
    USERS ||--o{ BUDGETS : sets
    USERS ||--o{ AI_PREDICTIONS : triggers
    CATEGORIES ||--o{ TRANSACTIONS : classifies
    CATEGORIES ||--o{ BUDGETS : tracks

    CATEGORIES {
        int id PK
        string name
        string type
    }
    TRANSACTIONS {
        int id PK
        float amount
        string description
        date transaction_date
    }
    BUDGETS {
        int id PK
        float amount_limit
        int month
        int year
    }
    AI_PREDICTIONS {
        int id PK
        string raw_prompt
        string predicted_category
        float confidence
    }"""

activity_ai = """@startuml
skinparam monochrome true
|Người dùng|
start
:Nhập câu lệnh thu chi\n(VD: Ăn phở 40k);
|Hệ thống Backend|
:Tiếp nhận Request HTTP;
:Gửi Prompt tới AI;
|Google Gemini 1.5|
:Phân tích sắc thái ngôn ngữ (NLP);
:Trích xuất số tiền & danh mục;
:Trả về định dạng JSON;
|Hệ thống Backend|
if (Độ tin cậy > 0.6?) then (Có)
  if (Số tiền > 0?) then (Hợp lệ)
    :Lưu vào Database (Transactions);
    :Tính toán lại tổng thu chi;
  else (Không hợp lệ)
    :Trả về lỗi 422 Unprocessable Entity;
    stop
  endif
else (Dưới 0.6)
  :Đánh dấu yêu cầu xác nhận thủ công;
endif
|Người dùng|
:Nhận thông báo ghi chú thành công;
stop
@enduml"""

seq_ai = """@startuml
skinparam monochrome true
actor Client
participant "API Gateway" as API
participant "Auth Middleware" as Auth
participant "Transaction Service" as Tx
participant "Gemini AI API" as AI
database "PostgreSQL" as DB

Client -> API: POST /api/transactions/ai\n(Prompt, Token)
API -> Auth: Validate JWT Token
alt Token hợp lệ
    Auth --> API: Token Valid (User ID)
    API -> Tx: Forward Request
    Tx -> AI: Gọi API phân tích ngữ nghĩa
    activate AI
    AI --> Tx: Trả về JSON (Amount, Category)
    deactivate AI
    Tx -> DB: SELECT Category ID
    DB --> Tx: Result
    Tx -> DB: INSERT INTO Transactions
    activate DB
    DB --> Tx: Lưu thành công
    deactivate DB
    Tx --> API: HTTP 201 Created
    API --> Client: Trả kết quả giao dịch
else Token hết hạn/Sai
    Auth --> API: HTTP 401 Unauthorized
    API --> Client: Trả lỗi xác thực
end
@enduml"""

generate_diagram(uc_finance, 'plantuml', '1_UseCase_TaiChinh.png')
generate_diagram(uc_ai, 'plantuml', '2_UseCase_AI.png')
generate_diagram(erd_rbac, 'mermaid', '3_ERD_RBAC.png')
generate_diagram(erd_tx, 'mermaid', '4_ERD_GiaoDich.png')
generate_diagram(activity_ai, 'plantuml', '5_Activity_AI_Flow.png')
generate_diagram(seq_ai, 'plantuml', '6_Sequence_Auth_AI.png')
