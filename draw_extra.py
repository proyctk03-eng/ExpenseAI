import os
import base64
import zlib
import urllib.request

output_dir = r'C:\Users\dathao\Desktop\ExpenseAI_Diagrams_Pro'

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

uc_tongquat = """@startuml
skinparam monochrome true
left to right direction
actor "Người dùng" as user
actor "Quản trị viên" as admin
actor "Google Gemini" as ai

rectangle "Hệ thống ExpenseAI" {
  usecase "Quản lý Tài khoản" as UC1
  usecase "Quản lý Giao dịch" as UC2
  usecase "Quản lý Danh mục & Ngân sách" as UC3
  usecase "Báo cáo Thống kê" as UC4
  usecase "Trợ lý Cố vấn AI" as UC5
}

user --> UC1
user --> UC2
user --> UC3
user --> UC4
user --> UC5

admin --> UC1
admin --> UC3

UC2 ..> ai : Gọi API phân tích
UC5 ..> ai : Gọi API cố vấn
@enduml"""

domain_model = """@startuml
skinparam monochrome true
hide circle
hide empty methods

class "Người dùng" as User {
  Họ tên
  Email
}
class "Tài khoản" as Account {
  Số dư
}
class "Giao dịch" as Transaction {
  Số tiền
  Ngày tháng
  Ghi chú
}
class "Danh mục" as Category {
  Tên danh mục
  Loại (Thu/Chi)
}
class "Ngân sách" as Budget {
  Hạn mức
  Tháng/Năm
}
class "Dữ liệu AI" as AIPrediction {
  Độ tin cậy
}

User "1" -- "1" Account : sở hữu
User "1" -- "*" Transaction : thực hiện
User "1" -- "*" Category : tạo
User "1" -- "*" Budget : thiết lập
Transaction "*" -- "1" Category : thuộc về
Budget "*" -- "1" Category : áp dụng cho
Transaction "1" -- "0..1" AIPrediction : được phân loại bởi
@enduml"""

architecture = """@startuml
skinparam monochrome true
node "Client Tier" {
  [Web Browser / Mobile App] as Client
}

node "Application Tier (FastAPI)" {
  [API Gateway] as Gateway
  [Auth Service] as Auth
  [Transaction Service] as Tx
  [AI Integration Service] as AIService
  [Report Service] as Report
}

node "Data Tier" {
  database "PostgreSQL" as DB
  database "Redis Cache" as Cache
}

cloud "External Services" {
  [Google Gemini API] as Gemini
}

Client --> Gateway : HTTP/REST
Gateway --> Auth
Gateway --> Tx
Gateway --> Report
Tx --> AIService
AIService --> Gemini : HTTPS
Tx --> DB
Report --> DB
Auth --> Cache
@enduml"""

class_diagram = """classDiagram
    class User {
        +int id
        +string username
        +string email
        +login()
        +logout()
    }
    class Transaction {
        +int id
        +float amount
        +string description
        +datetime date
        +create()
        +update()
        +delete()
    }
    class Category {
        +int id
        +string name
        +string type
        +addCategory()
    }
    class AIProcessor {
        +parse_prompt(text)
        +get_financial_advice(user_data)
    }
    User "1" *-- "*" Transaction
    User "1" *-- "*" Category
    Category "1" o-- "*" Transaction
    Transaction ..> AIProcessor : uses"""

deployment = """@startuml
skinparam monochrome true
node "User Device" <<Device>> {
  node "Web Browser" {
    artifact "VueJS/React Frontend" as FE
  }
}

node "Cloud Server (AWS/GCP)" <<Server>> {
  node "Docker Container: Nginx" {
    [Reverse Proxy]
  }
  node "Docker Container: Backend" {
    artifact "FastAPI Application" as BE
  }
  node "Docker Container: Database" {
    database "PostgreSQL 15" as DB
  }
}

cloud "Google Cloud AI" {
  [Gemini 1.5 Flash Model] as AI
}

FE --> [Reverse Proxy] : HTTPS (443)
[Reverse Proxy] --> BE : HTTP (8000)
BE --> DB : TCP (5432)
BE --> AI : HTTPS API
@enduml"""

component = """@startuml
skinparam monochrome true
package "Frontend" {
  [UI Components]
  [State Management]
  [API Client (Axios)]
}

package "Backend (FastAPI)" {
  [Router / Controllers]
  [Services (Business Logic)]
  [Repositories (DAL)]
  [Pydantic Schemas]
}

database "PostgreSQL" as DB

[UI Components] --> [State Management]
[State Management] --> [API Client (Axios)]
[API Client (Axios)] --> [Router / Controllers] : REST
[Router / Controllers] --> [Pydantic Schemas] : Validate
[Router / Controllers] --> [Services (Business Logic)]
[Services (Business Logic)] --> [Repositories (DAL)]
[Repositories (DAL)] --> DB : SQLAlchemy 2.0
@enduml"""

gen(uc_tongquat, 'plantuml', '7_UseCase_TongQuat.png')
gen(domain_model, 'plantuml', '8_Domain_Model.png')
gen(architecture, 'plantuml', '9_Architecture_3Tier.png')
gen(class_diagram, 'mermaid', '10_Class_Diagram.png')
gen(deployment, 'plantuml', '11_Deployment.png')
gen(component, 'plantuml', '12_Component_Diagram.png')
