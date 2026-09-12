# app/routers/hoa_don.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HoaDon, ChiTietHoaDon, Ban, Mon, NguoiDung
from app.schemas import HoaDonResponse, HoaDonCreate, ChiTietHoaDonCreate, ChiTietHoaDonResponse
from app.auth import get_current_user
from app.nghiep_vu import kiem_tra_quy_tac

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas



router = APIRouter(prefix="/hoa-don", tags=["Quản lý Hóa đơn & Bán hàng"])

# Đường dẫn /ban
@router.get("/ban", summary="Lấy danh sách bàn")
def lay_danh_sach_ban(db: Session = Depends(get_db)):
    danh_sach_ban = db.query(models.Ban).all()
    return danh_sach_ban

@router.post("", response_model=HoaDonResponse, status_code=status.HTTP_201_CREATED)
def mo_hoa_don(
    data: HoaDonCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    ban = db.query(Ban).filter(Ban.id == data.ban_id).first()
    if not ban:
        raise HTTPException(status_code=404, detail="Bàn không tồn tại")
    
    # Quy tắc 1: Bàn đang có khách không được mở thêm hóa đơn (Trả 409)
    ly_do = kiem_tra_quy_tac("MO_HOA_DON", {"ban_dang_co_khach": ban.dang_co_khach})
    if ly_do:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ly_do)

    hoa_don_moi = HoaDon(ban_id=data.ban_id, gio_mo=datetime.now(), da_thanh_toan=False)
    ban.dang_co_khach = True  # Chuyển bàn sang đang có khách
    
    db.add(hoa_don_moi)
    db.commit()
    db.refresh(hoa_don_moi)
    return hoa_don_moi

@router.post("/{id}/mon", response_model=ChiTietHoaDonResponse, status_code=status.HTTP_201_CREATED)
def goi_mon(
    id: int,
    data: ChiTietHoaDonCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    hoa_don = db.query(HoaDon).filter(HoaDon.id == id).first()
    if not hoa_don:
        raise HTTPException(status_code=404, detail="Hóa đơn không tồn tại")
    
    # Quy tắc 2: Hóa đơn đã thanh toán không được thêm món
    ly_do_hd = kiem_tra_quy_tac("THEM_MON", {"trang_thai_hoa_don": "DA_THANH_TOAN" if hoa_don.da_thanh_toan else "CHUA_THANH_TOAN"})
    if ly_do_hd:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ly_do_hd)

    mon = db.query(Mon).filter(Mon.id == data.mon_id).first()
    if not mon:
        raise HTTPException(status_code=404, detail="Món không tồn tại")
    
    # Quy tắc 3: Món tắt con_ban không được bán
    ly_do_mon = kiem_tra_quy_tac("GOI_MON_CON_BAN", {"con_ban": mon.con_ban})
    if ly_do_mon:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ly_do_mon)

    # TRÁNH BẪY DỰ ÁN: Copy đơn giá tại thời điểm đặt món vào bảng chi tiết
    ct_hd = ChiTietHoaDon(
        hoa_don_id=hoa_don.id,
        mon_id=mon.id,
        so_luong=data.so_luong,
        don_gia=mon.gia
    )
    db.add(ct_hd)
    db.commit()
    db.refresh(ct_hd)
    return ct_hd

@router.delete("/{id}/mon/{ct_id}", status_code=status.HTTP_204_NO_CONTENT)
def bo_mon(
    id: int,
    ct_id: int,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    ct = db.query(ChiTietHoaDon).filter(ChiTietHoaDon.id == ct_id, ChiTietHoaDon.hoa_don_id == id).first()
    if not ct:
        raise HTTPException(status_code=404, detail="Không tìm thấy món trong hóa đơn")
    
    db.delete(ct)
    db.commit()
    return None

@router.post("/{id}/thanh-toan", response_model=HoaDonResponse)
def thanh_toan(
    id: int,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    hoa_don = db.query(HoaDon).filter(HoaDon.id == id).first()
    if not hoa_don:
        raise HTTPException(status_code=404, detail="Hóa đơn không tồn tại")
    
    if hoa_don.da_thanh_toan:
        raise HTTPException(status_code=409, detail="Hóa đơn này đã được thanh toán trước đó")

    # Quy tắc 4: Hóa đơn rỗng không cho thanh toán
    ly_do_rong = kiem_tra_quy_tac("THANH_TOAN_RONG", {"so_luong_mon_chi_tiet": len(hoa_don.chi_tiet)})
    if ly_do_rong:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ly_do_rong)

    # Dùng Transaction đảm bảo an toàn 3 việc trong 1 lần commit
    try:
        # 1. Tính tổng tiền từ cột don_gia trong chi tiết (TRÁNH BẪY DỰ ÁN)
        tong_tien = sum(ct.so_luong * ct.don_gia for ct in hoa_don.chi_tiet)
        hoa_don.tong_tien = tong_tien
        hoa_don.da_thanh_toan = True
        hoa_don.gio_dong = datetime.now()

        # 2. Đổi trạng thái bàn về trống
        ban = db.query(Ban).filter(Ban.id == hoa_don.ban_id).first()
        if ban:
            ban.dang_co_khach = False

        db.commit()
        db.refresh(hoa_don)
        return hoa_don
    except Exception as e:
        db.rollback() # Tránh kẹt trạng thái bàn khi có lỗi
        raise HTTPException(status_code=500, detail="Thanh toán thất bại")