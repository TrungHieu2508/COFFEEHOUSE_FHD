# app/seed.py
from sqlalchemy.orm import Session
from app.models import NguoiDung, Mon, Ban
from app.auth import get_password_hash

def seed_data(db: Session):
    # 1. Seed NguoiDung (Tài khoản theo đúng thong-tin-nop.json)
    if db.query(NguoiDung).count() == 0:
        users = [
            NguoiDung(
                ten_dang_nhap="quanly", 
                mat_khau_bam=get_password_hash("quanly123"), 
                vai_tro="quanly"
            ),
            NguoiDung(
                ten_dang_nhap="nhanvien", 
                mat_khau_bam=get_password_hash("nhanvien123"), 
                vai_tro="nhanvien"
            )
        ]
        db.add_all(users)

    # 2. Seed Ban
    if db.query(Ban).count() == 0:
        bans = [Ban(so_ban=i, suc_chua=4, dang_co_khach=False) for i in range(1, 11)]
        db.add_all(bans)

    # 3. Seed Menu Món (Dữ liệu thực tế, 15-20 món)
    if db.query(Mon).count() == 0:
        thuc_don = [
            Mon(ma_mon="CF01", ten="Cà phê đen đá", nhom="Cà phê", gia=22000, con_ban=True),
            Mon(ma_mon="CF02", ten="Cà phê sữa đá", nhom="Cà phê", gia=25000, con_ban=True),
            Mon(ma_mon="CF03", ten="Bạc xỉu", nhom="Cà phê", gia=28000, con_ban=True),
            Mon(ma_mon="TS01", ten="Trà sữa truyền thống", nhom="Trà sữa", gia=32000, con_ban=True),
            Mon(ma_mon="TS02", ten="Trà sữa ô long", nhom="Trà sữa", gia=35000, con_ban=True),
            Mon(ma_mon="TR01", ten="Trà đào cam sả", nhom="Trà trái cây", gia=35000, con_ban=True),
            Mon(ma_mon="TR02", ten="Trà vải quế hoa", nhom="Trà trái cây", gia=38000, con_ban=True),
            Mon(ma_mon="AN01", ten="Bánh Flan", nhom="Ăn kèm", gia=15000, con_ban=True),
            Mon(ma_mon="AN02", ten="Hướng dương", nhom="Ăn kèm", gia=12000, con_ban=True),
        ]
        db.add_all(thuc_don)

    db.commit()