from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class QuyTac(ABC):
    @abstractmethod
    def kiem_tra(self, boi_canh: Dict[str, Any]) -> Optional[str]:
        pass

class BanDangCoKhach(QuyTac):
    def kiem_tra(self, boi_canh: Dict[str, Any])-> Optional[str]:
        if boi_canh.get("ban_dang_co_khach", False):
            return "Bàn đang có hóa đơn chưa thanh toán, không thể mở thêm hóa đơn mới."
        return None

class HoaDonDaThanhToan(QuyTac):
    def kiem_tra(self, boi_canh: Dict[str, Any])-> Optional[str]:
        if boi_canh.get("trang_thai_hoa_don") == "DA_THANH_TOAN":
                return "Hóa đơn đã thanh toán, không thể thao tác thêm món."
        return None

class MonDaTatConBan(QuyTac):
    def kiem_tra(self, boi_canh: Dict[str, Any])-> Optional[str]:
        if not boi_canh.get("con_ban", True):
            return "Món ăn/đồ uống này hiện đã hết (tắt còn bán), không thể gọi."
        return None

class HoaDonRong(QuyTac):
    def kiem_tra(self, boi_canh: Dict[str, Any]) -> Optional[str]:
        so_luong_mon = boi_canh.get("so_luong_mon_chi_tiet", 0)
        if so_luong_mon <= 0:
            return "Hóa đơn chưa có món nào, không thể thanh toán."
        return None

DANH_SACH_QUY_TAC: List[QuyTac] = [
    BanDangCoKhach(),
    HoaDonDaThanhToan(),
    MonDaTatConBan(),
    HoaDonRong()
]

def kiem_tra_quy_tac(ten_quy_tac: str, boi_canh: Dict[str, Any]) -> Optional[str]:
    map_quy_tac = {
        "MO_HOA_DON": BanDangCoKhach(),
        "THEM_MON": HoaDonDaThanhToan(),
        "GOI_MON_CON_BAN": MonDaTatConBan(),
        "THANH_TOAN_RONG": HoaDonRong()
    }
    rule = map_quy_tac.get(ten_quy_tac)
    if rule:
        return rule.kiem_tra(boi_canh)
    return None

class CachTinhGia(ABC):
    @abstractmethod
    def tinh(self, don_gia: int, so_luong: int) -> int:
        pass

class GiaThuong(CachTinhGia):
    def tinh(self, don_gia: int, so_luong: int) -> int:
        return don_gia * so_luong

class GiamTheoPhanTram(CachTinhGia):
    def __init__(self, phan_tram: int = 10):
        self.phan_tram = phan_tram

    def tinh(self, don_gia: int, so_luong: int) -> int:
        tong = don_gia * so_luong
        return int(tong * (1 - self.phan_tram / 100))

class MuaHaiTangMot(CachTinhGia):
    def tinh(self, don_gia: int, so_luong: int) -> int:
        so_luong_tinh_tien = so_luong - (so_luong // 3)
        return don_gia * so_luong_tinh_tien