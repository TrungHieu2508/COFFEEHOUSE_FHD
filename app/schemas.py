# app/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class NguoiDungResponse(BaseModel):
    id: int
    ten_dang_nhap: str
    vai_tro: str

    model_config = ConfigDict(from_attributes=True)

# --- Mon Schemas ---
class MonBase(BaseModel):
    ma_mon: str
    ten: str
    nhom: str
    gia: int
    con_ban: bool = True

class MonCreate(MonBase):
    pass

class MonResponse(MonBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Ban Schemas ---
class BanResponse(BaseModel):
    id: int
    so_ban: int
    suc_chua: int
    dang_co_khach: bool

    model_config = ConfigDict(from_attributes=True)

# --- Hoa Don & Chi Tiet Schemas ---
class ChiTietHoaDonCreate(BaseModel):
    mon_id: int
    so_luong: int

class ChiTietHoaDonResponse(BaseModel):
    id: int
    hoa_don_id: int
    mon_id: int
    so_luong: int
    don_gia: int
    mon: Optional[MonResponse] = None

    model_config = ConfigDict(from_attributes=True)

class HoaDonCreate(BaseModel):
    ban_id: int

class HoaDonResponse(BaseModel):
    id: int
    ban_id: int
    gio_mo: datetime
    gio_dong: Optional[datetime] = None
    tong_tien: int
    da_thanh_toan: bool
    chi_tiet: List[ChiTietHoaDonResponse] = []

    model_config = ConfigDict(from_attributes=True)