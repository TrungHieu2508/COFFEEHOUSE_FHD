# ☕ FastAPI CoffeeHouse Management System

> **Dành cho:** Chủ quán và nhân viên phục vụ quán cà phê sử dụng trực tiếp trên điện thoại/máy tính bảng trong ca làm việc.
> **Mục đích:** Thay thế quyển sổ ghi món bằng API tự động: mở hóa đơn cho bàn, gọi món, bỏ món, thanh toán, quản lý thực đơn và xem báo cáo doanh thu cuối ngày.

---

## 🎬 Kịch bản dùng thật (Real-world Scenario)

Một buổi làm việc thực tế của nhân viên phục vụ và quản lý:

> **Sáng sớm:** Nhân viên mở `/docs`, bấm Authorize và đăng nhập bằng tài khoản `nhanvien`.
> 1. Khách ngồi bàn 5 $\rightarrow$ `POST /hoa-don` với `{"ban_id": 5}`.
> 2. Khách gọi 2 Cà phê sữa đá $\rightarrow$ `POST /hoa-don/1/mon` với `{"mon_id": 2, "so_luong": 2}`.
> 3. Khách gọi thêm 1 Bánh flan $\rightarrow$ `POST /hoa-don/1/mon` với `{"mon_id": 16, "so_luong": 1}`.
> 4. Khách đổi ý bỏ Bánh flan $\rightarrow$ `DELETE /hoa-don/1/mon/2`.
> 5. Khách thanh toán $\rightarrow$ `POST /hoa-don/1/thanh-toan` $\rightarrow$ Trả về tổng tiền, bàn 5 về trạng thái trống.
> 6. Cuối ngày Quản lý xem doanh thu $\rightarrow$ `GET /thong-ke/doanh-thu`.
> 7. Quản lý xuất file báo cáo kế toán $\rightarrow$ `GET /nhap-xuat/doanh-thu.csv`.

*Lưu ý khi sử dụng online: Lần gọi API đầu tiên trên dịch vụ Hosting miễn phí (Render) có thể mất 30–60 giây để hệ thống khởi động.*

---

## 🚀 Hướng dẫn khởi chạy dự án

### 1. Cài đặt môi trường
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

alembic upgrade head
python -m uvicorn app.main:app --reload