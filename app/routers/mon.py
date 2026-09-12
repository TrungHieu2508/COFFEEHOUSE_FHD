# app/routers/mon.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mon, NguoiDung
from app.schemas import MonResponse, MonCreate
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/mon", tags=["Quản lý Thực đơn"])

@router.get("", response_model=List[MonResponse])
def ds_mon(
    tim: Optional[str] = Query(None, description="Tìm kiếm theo tên món"),
    bo_qua: int = Query(0, ge=0),
    gioi_han: int = Query(10, ge=1, le=100), # Truyền >100 hoặc <1 sẽ tự trả 422
    db: Session = Depends(get_db)
):
    query = db.query(Mon)
    if tim:
        query = query.filter(Mon.ten.icontains(tim))
    return query.offset(bo_qua).limit(gioi_han).all()

@router.post("", response_model=MonResponse, status_code=status.HTTP_201_CREATED)
def tao_mon(
    mon_in: MonCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role("quanly"))
):
    # Kiểm tra trùng mã món
    if db.query(Mon).filter(Mon.ma_mon == mon_in.ma_mon).first():
        raise HTTPException(status_code=400, detail="Mã món đã tồn tại")
    
    mon_moi = Mon(**mon_in.model_dump())
    db.add(mon_moi)
    db.commit()
    db.refresh(mon_moi)
    return mon_moi

@router.put("/{id}", response_model=MonResponse)
def cap_nhat_mon(
    id: int,
    mon_in: MonCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(require_role("quanly"))
):
    mon = db.query(Mon).filter(Mon.id == id).first()
    if not mon:
        raise HTTPException(status_code=404, detail="Không tìm thấy món")
    
    for key, val in mon_in.model_dump().items():
        setattr(mon, key, val)
    db.commit()
    db.refresh(mon)
    return mon