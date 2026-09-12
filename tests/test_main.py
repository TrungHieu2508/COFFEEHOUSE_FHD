import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models  # Đảm bảo SQLAlchemy đăng ký đủ các ORM Models
from app.seed import seed_data

# Sử dụng StaticPool để giữ nguyên 1 database SQLite in-memory xuyên suốt các kết nối
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    # Tạo cấu trúc bảng
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    seed_data(db)  # Khởi tạo dữ liệu mẫu
    
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    # Dọn dẹp dữ liệu/bảng sau mỗi test
    Base.metadata.drop_all(bind=engine)

# 1. Test Healthcheck
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200

# 2. Test Đăng nhập thành công
def test_login_success(client):
    response = client.post(
        "/auth/dang-nhap",
        data={"username": "quanly", "password": "quanly123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

# 3. Test Đăng nhập thất bại
def test_login_failed(client):
    response = client.post(
        "/auth/dang-nhap",
        data={"username": "quanly", "password": "sai_mat_khau"}
    )
    assert response.status_code == 401

# 4. Test Phân quyền - Nhân viên không thể thêm món
def test_nhanvien_create_mon_forbidden(client):
    login_res = client.post("/auth/dang-nhap", data={"username": "nhanvien", "password": "nhanvien123"})
    token = login_res.json()["access_token"]
    
    res = client.post(
        "/mon",
        json={"ma_mon": "TEST01", "ten": "Tra Sua Test", "nhom": "Test", "gia": 20000},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403

# 5. Test Lỗi validation phân trang
def test_mon_pagination_invalid(client):
    response = client.get("/mon?gioi_han=9999")
    assert response.status_code == 422

# 6. Test Mở hóa đơn trùng bàn đang có khách
def test_mo_hoa_don_ban_dang_co_khach(client):
    login_res = client.post("/auth/dang-nhap", data={"username": "nhanvien", "password": "nhanvien123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    client.post("/hoa-don", json={"ban_id": 1}, headers=headers)
    res_2 = client.post("/hoa-don", json={"ban_id": 1}, headers=headers)
    assert res_2.status_code == 409

# 7. Test Thanh toán hóa đơn chưa gọi món
def test_thanh_toan_hoa_don_rong(client):
    login_res = client.post("/auth/dang-nhap", data={"username": "nhanvien", "password": "nhanvien123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    hd_res = client.post("/hoa-don", json={"ban_id": 2}, headers=headers)
    hd_id = hd_res.json()["id"]
    
    res = client.post(f"/hoa-don/{hd_id}/thanh-toan", headers=headers)
    assert res.status_code == 409

# 8. Test Import CSV lọc dòng lỗi
def test_import_csv_dirty_data(client):
    login_res = client.post("/auth/dang-nhap", data={"username": "quanly", "password": "quanly123"})
    token = login_res.json()["access_token"]
    
    csv_content = "ma_mon,ten,nhom,gia\nCF99,Ca phe Test,Ca phe,30000\nCF98,Gia am,Ca phe,-5000\n,Thieu ma,Ca phe,20000"
    files = {"file": ("thuc_don.csv", csv_content, "text/csv")}
    
    res = client.post(
        "/nhap-xuat/thuc-don.csv",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["so_dong_nhan"] == 1
    assert res.json()["so_dong_bo"] == 2