# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NguoiDung
from app.auth import verify_password, create_access_token, get_current_user
from app.schemas import Token, NguoiDungResponse

router = APIRouter(prefix="/auth", tags=["Xác thực & Phân quyền"])

@router.post("/dang-nhap", response_model=Token)
def dang_nhap(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.ten_dang_nhap == form_data.username).first()
    if not user or not verify_password(form_data.password, user.mat_khau_bam):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.ten_dang_nhap, "vai_tro": user.vai_tro})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/toi", response_model=NguoiDungResponse)
def thong_tin_ca_nhan(current_user: NguoiDung = Depends(get_current_user)):
    return current_user