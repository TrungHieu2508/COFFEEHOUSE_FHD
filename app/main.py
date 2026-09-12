# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db, engine
from app.seed import seed_data
from app.routers import auth, mon, hoa_don, nhap_xuat, thong_ke
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tự động nạp dữ liệu mẫu khi khởi động nếu cấu hình bật
    if settings.TAO_DU_LIEU_MAU:
        db = next(get_db())
        try:
            seed_data(db)
        finally:
            db.close()
    yield

app = FastAPI(
    title="API Quản Lý Quán Cà Phê",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn truy cập (cho mục đích demo/test)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def serve_dashboard():
    return FileResponse("index.html")

# Đăng ký Router Auth
app.include_router(auth.router)

# Endpoint kiểm tra sức khỏe bắt buộc (Tiêu chí 5)
@app.get("/health", tags=["Hệ thống"])
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

app.include_router(auth.router)
app.include_router(mon.router)
app.include_router(hoa_don.router)
app.include_router(nhap_xuat.router)
app.include_router(thong_ke.router)
