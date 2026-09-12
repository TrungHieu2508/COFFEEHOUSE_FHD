# app/routers/nhap_xuat.py
import csv
import io
from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mon, NguoiDung, HoaDon
from app.auth import require_role
from app.nhap_xuat import doc_thuc_don

router = APIRouter(prefix="/nhap-xuat", tags=["Nhập xuất File"])

@router.post("/thuc-don.csv")
async def nhap_thuc_don_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role("quanly"))
):
    noi_dung_bytes = await file.read()
    try:
        noi_dung_chuoi = noi_dung_bytes.decode("utf-8")
    except UnicodeDecodeError:
        noi_dung_chuoi = noi_dung_bytes.decode("latin-1")  # Chịu được mã hóa file không phải UTF-8

    danh_sach_mon, ly_do_bo = doc_thuc_don(noi_dung_chuoi)
    
    so_dong_nhan = 0
    for mon_dict in danh_sach_mon:
        mon_cu = db.query(Mon).filter(Mon.ma_mon == mon_dict["ma_mon"]).first()
        if mon_cu:
            # Nếu đã có thì cập nhật
            mon_cu.ten = mon_dict["ten"]
            mon_cu.nhom = mon_dict["nhom"]
            mon_cu.gia = mon_dict["gia"]
        else:
            db.add(Mon(**mon_dict))
        so_dong_nhan += 1
        
    db.commit()
    return {
        "thong_bao": f"Nhập thành công {so_dong_nhan} dòng",
        "so_dong_nhan": so_dong_nhan,
        "so_dong_bo": len(ly_do_bo),
        "ly_do_bo": ly_do_bo
    }

@router.get("/doanh-thu.csv")
def xuat_doanh_thu_csv(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role("quanly"))
):
    hoa_dons = db.query(HoaDon).filter(HoaDon.da_thanh_toan == True).all()
    
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["Mã Hóa Đơn", "Bàn", "Giờ Mở", "Giờ Đóng", "Tổng Tiền"])
    
    for hd in hoa_dons:
        writer.writerow([hd.id, hd.ban_id, hd.gio_mo, hd.gio_dong, hd.tong_tien])
        
    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=doanh-thu.csv"
    return response