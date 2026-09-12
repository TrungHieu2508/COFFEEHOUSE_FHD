from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class NguoiDung(Base):
    __tablename__ = "nguoi_dung"
    id: Mapped[int] = mapped_column(Integer, primary_key= True, index = True)
    ten_dang_nhap : Mapped[str] = mapped_column(String(50), unique= True, index = True, nullable= False )
    mat_khau_bam: Mapped[str] = mapped_column(String(255), nullable= False)
    vai_tro: Mapped[str] = mapped_column(String(20), nullable= False, default= "nhanvien")

class Mon(Base):
    __tablename__ = 'mon'

    id: Mapped[int] = mapped_column(Integer, primary_key= True, index = True)
    ma_mon : Mapped[str] = mapped_column(String(20), unique= True, index = True, nullable= False)
    ten: Mapped[str] = mapped_column(String(100), nullable= False)
    nhom: Mapped[str] = mapped_column(String(50), nullable= False)
    gia: Mapped[ int] = mapped_column(Integer, nullable= False)
    con_ban: Mapped[bool] = mapped_column(Boolean, default= True)

    chi_tiet_hoa_don: Mapped[List['ChiTietHoaDon']] = relationship(back_populates= "mon")

class Ban(Base):
    __tablename__ = 'ban'

    id: Mapped[int] = mapped_column(Integer, primary_key= True, index = True)
    so_ban: Mapped[int] = mapped_column(Integer, unique= True, index = True, nullable=False)
    suc_chua: Mapped[int] = mapped_column(Integer, default= 4)
    dang_co_khach: Mapped[int] = mapped_column(Boolean, default= False)

    hoa_don: Mapped[List["HoaDon"]] = relationship(back_populates="ban")


class HoaDon(Base):
    __tablename__ = 'hoa_don'

    id: Mapped[int] = mapped_column(Integer, primary_key= True, index = True)
    ban_id: Mapped[int] = mapped_column(ForeignKey("ban.id"), nullable= False)
    gio_mo: Mapped[datetime] = mapped_column(DateTime, default= datetime.now)
    gio_dong: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable= True)
    tong_tien: Mapped[int] = mapped_column(Integer, default= 0)
    da_thanh_toan: Mapped[bool] = mapped_column(Boolean, default= False)

    ban: Mapped["Ban"] = relationship(back_populates="hoa_don")
    chi_tiet: Mapped[List["ChiTietHoaDon"]] = relationship(
        back_populates="hoa_don",
        cascade= "all, delete-orphan",
        lazy = "selectin"
    )

class ChiTietHoaDon(Base):
    __tablename__ = "chi_tiet_hoa_don"
    id: Mapped[int] = mapped_column(Integer, primary_key= True, index = True)
    hoa_don_id: Mapped[int] = mapped_column(ForeignKey("hoa_don.id"), nullable= False)
    mon_id: Mapped[int] = mapped_column(ForeignKey("mon.id"), nullable= False)
    so_luong: Mapped[int] = mapped_column(Integer, nullable= False)
    don_gia: Mapped[int] = mapped_column(Integer, nullable= False)

    hoa_don: Mapped["HoaDon"] = relationship(back_populates="chi_tiet")
    mon: Mapped["Mon"] = relationship(back_populates= "chi_tiet_hoa_don")