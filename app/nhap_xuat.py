# app/nhap_xuat.py
import csv
import io
from typing import Tuple, List, Dict, Any

def doc_thuc_don(noi_dung_csv: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    danh_sach_mon = []
    ly_do_bo = []
    
    stream = io.StringIO(noi_dung_csv)
    reader = csv.reader(stream)
    
    da_gap_ma_mon = set()
    dong_so = 0
    
    for row in reader:
        dong_so += 1
        
        # 1. Bỏ qua dòng trống
        if not row or not any(field.strip() for field in row):
            continue
            
        # Kiểm tra tiêu đề header nếu dòng 1 chứa từ khóa
        if dong_so == 1 and ("ma_mon" in row[0].lower() or "mã" in row[0].lower()):
            continue

        # 2. Thiếu cột (cần ít nhất 4 cột: ma_mon, ten, nhom, gia)
        if len(row) < 4:
            ly_do_bo.append(f"Dòng {dong_so}: Thiếu cột thông tin.")
            continue
            
        ma_mon = row[0].strip()
        ten = row[1].strip()
        nhom = row[2].strip()
        gia_str = row[3].strip().replace(".", "").replace(",", "")  # Xử lý 25.000 -> 25000
        
        if not ma_mon or not ten:
            ly_do_bo.append(f"Dòng {dong_so}: Mã món hoặc tên món bị trống.")
            continue
            
        # 3. Trùng mã món trong cùng file
        if ma_mon in da_gap_ma_mon:
            ly_do_bo.append(f"Dòng {dong_so}: Trùng mã món '{ma_mon}' trong cùng file.")
            continue
            
        # 4. Ép kiểu giá tiền
        try:
            gia = int(gia_str)
            if gia < 0:
                ly_do_bo.append(f"Dòng {dong_so}: Giá món không được âm ({gia}).")
                continue
        except ValueError:
            ly_do_bo.append(f"Dòng {dong_so}: Giá món không phải số hợp lệ ('{row[3]}').")
            continue
            
        da_gap_ma_mon.add(ma_mon)
        danh_sach_mon.append({
            "ma_mon": ma_mon,
            "ten": ten,
            "nhom": nhom,
            "gia": gia,
            "con_ban": True
        })
        
    return danh_sach_mon, ly_do_bo