from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    products_1_orginal:str
    products_2_orginal:str
    mongo_data_base:str
    products_pre:str
    users_orginal:str
    users_pre:str
    embedding_model:str
    Qdrant_end_point:str
    Qdrant_api_key:str
    COLLECTION_NAME:str
    mongo_db_name:str
    mongo_user_collection_name:str
    best_CF_model_path:str
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
