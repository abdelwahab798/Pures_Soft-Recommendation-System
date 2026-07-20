from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    products_1_orginal:str
    products_2_orginal:str
    data_base:str
    products_pre:str
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
