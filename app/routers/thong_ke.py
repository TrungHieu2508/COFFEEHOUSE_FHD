from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/thong-ke", tags=["Thống kê"])

@router.get("/top-mon-ban-chay", summary="Top món bán chạy (Chỉ Quản lý)")
def lay_top_mon_ban_chay(
    limit: int = Query(5, ge=1, le=20),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.vai_tro != "quanly":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Chỉ quản lý mới có quyền xem thống kê"
        )

    # Truy vấn viết tay bằng text() đáp ứng đủ: JOIN + GROUP BY + SUM + Tham số hóa :gioi_han
    sql_query = text("""
        SELECT 
            m.ma_mon,
            m.ten AS ten_mon,
            SUM(ct.so_luong) AS tong_so_luong,
            SUM(ct.so_luong * ct.don_gia) AS tong_doanh_thu
        FROM chi_tiet_hoa_don ct
        JOIN hoa_don hd ON ct.hoa_don_id = hd.id
        JOIN mon m ON ct.mon_id = m.id
        WHERE hd.da_thanh_toan = :trang_thai
        GROUP BY m.id, m.ma_mon, m.ten
        ORDER BY tong_so_luong DESC
        LIMIT :gioi_han
    """)

    result = db.execute(sql_query, {"trang_thai": True, "gioi_han": limit}).fetchall()

    return [
        {
            "ma_mon": row.ma_mon,
            "ten_mon": row.ten_mon,
            "tong_so_luong": row.tong_so_luong,
            "tong_doanh_thu": row.tong_doanh_thu
        }
        for row in result
    ]