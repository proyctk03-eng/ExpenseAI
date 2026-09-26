import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.database import init_db

if __name__ == "__main__":
    print("Khởi tạo database...")
    init_db()
    print("Đã khởi tạo xong.")
