import os
import joblib
import mlflow
import numpy as np
import logging
import pandas as pd
from pymongo import MongoClient
from xgboost import train
from config import Settings
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import mean_squared_error
import implicit
from scipy.sparse import csr_matrix

s=Settings()

def load_user_data_from_mongo():
    client=MongoClient(s.mongo_data_base) 
    db = client[s.mongo_db_name]
    ratings_collection=db[s.mongo_user_collection_name]
    data=list(ratings_collection.find({}))
    df=pd.DataFrame(data)
    print(df.columns)
    logging.info("load from mongo is done")
    df['user_code']=df['user_id'].astype('category').cat.codes
    df['product_code']=df['product_link'].astype('category').cat.codes
    logging.info("user_code and product_code are done")

    user_map=dict(enumerate(df['user_id'].astype('category').cat.categories))
    product_map=dict(enumerate(df['product_link'].astype('category').cat.categories))

    user_item_matrix=csr_matrix(( df["score"], (df["user_code"],df["product_code"]) ))
    return df,user_item_matrix,user_map,product_map

def train_evaluate():
    df,user_item_matrix,user_map,product_map=load_user_data_from_mongo()
    mlflow.set_experiment("Afaq_Hybrid_Recommendation")
    best_rsme=float("inf")
    best_model=None

    with mlflow.start_run(run_name="svd_model"):
        svd_model=TruncatedSVD(n_components=2, random_state=42)
        user_features=svd_model.fit_transform(user_item_matrix)
        preds_matrix =np.dot(user_features, svd_model.components_)
        actuals=df["score"].values
        preds=[preds_matrix[u, p] for u, p in zip(df["user_code"], df["product_code"])]
        svd_rmse=np.sqrt(mean_squared_error(actuals, preds))
        mlflow.log_metric("rmse", svd_rmse)

        if svd_rmse<best_rsme:
            best_rsme=svd_rmse
            best_model={
                "model_name": "SVD",
                "model": svd_model,
                "user_map": user_map,
                "product_map": product_map}


    with mlflow.start_run(run_name="als_model"):
        als_model=implicit.als.AlternatingLeastSquares(factors=8, random_state=42)
        als_model.fit(user_item_matrix.T)

        item_vecs = als_model.user_factors  
        user_vecs = als_model.item_factors  
        als_pred=[np.dot(user_vecs[u], item_vecs[p]) for u, p in zip(df["user_code"], df["product_code"])]
        
        als_rmse=np.sqrt(mean_squared_error(actuals, als_pred))
        mlflow.log_param("model_name", "ALS")
        mlflow.log_metric("rmse", als_rmse)

        if als_rmse<best_rsme:
            best_rsme=als_rmse
            best_model={
                "model_name": "ALS",
                "model": als_model,
                "user_map": user_map,
                "product_map": product_map}

        with open(s.best_CF_model_path, "wb") as f:
            joblib.dump(best_model, f)

#train_evaluate()




       
