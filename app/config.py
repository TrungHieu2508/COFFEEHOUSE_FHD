from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    CHUOI_KET_NOI: str = "sqlite:///./quan_ca_phe.db"
    KHOA_BI_MAT: str = "bi-mat-sieucap-khong-duoc-lo-ra-ngoai-123456"
    SO_PHUT_HET_HAN: int = 60
    TAO_DU_LIEU_MAU: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()