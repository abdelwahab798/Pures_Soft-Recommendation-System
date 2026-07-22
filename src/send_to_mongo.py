import json
from config import Settings
from pymongo import MongoClient, UpdateOne

s = Settings()

client=MongoClient(s.mongo_data_base)
db=client["afaq_recommendation"]


# ----------------------------------------------------
# Upload/Update Users (Batch Upsert)
# ----------------------------------------------------
def upload_users(batch_size=500):
  with open(s.users_pre, "r", encoding="utf-8") as f:
    users_data = json.load(f)

  users_collection=db["user_interactions"]

  operations=[]
  for item in users_data:
    operations.append(
        UpdateOne(
            {
                "user_id": item["user_id"],
                "product_link": item["product_link"],
            },
            {"$set": item},
            upsert=True,
        )
    )

    
    if len(operations) >= batch_size:
      users_collection.bulk_write(operations)
      operations=[]

  
  if operations:
    users_collection.bulk_write(operations)

  print(f"Users processed successfully: {len(users_data)}")


# ----------------------------------------------------
# Upload/Update Products (Batch Upsert)
# ----------------------------------------------------
def upload_products(batch_size=500):
  with open(s.products_pre, "r", encoding="utf-8") as f:
    products_data = json.load(f)

  products_collection=db["products"]

  operations = []
  for item in products_data:
    prod_link =item.get("metadata", {}).get("product_link")
    if prod_link:
      operations.append(
          UpdateOne(
              {"metadata.product_link": prod_link}, {"$set": item}, upsert=True
          )
      )

    if len(operations) >= batch_size:
      products_collection.bulk_write(operations)
      operations = []

  if operations:
    products_collection.bulk_write(operations)

  print(f"Products processed successfully: {len(products_data)}")


upload_users()
upload_products()