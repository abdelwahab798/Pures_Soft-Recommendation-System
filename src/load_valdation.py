import json
import pandas as pd
from config import Settings
s=Settings()

# load data and concat
df1=pd.read_json(s.products_1_orginal)
df2=pd.read_json(s.products_2_orginal)
product=pd.concat([df1, df2], ignore_index=True)

# get "product_id" to data dose't have duplicates
product['product_id']=product['metadata'].apply(lambda x: x.get('product_id') if isinstance(x, dict) else None)
product.drop_duplicates(subset=['product_id',"content"], inplace=True)
product.drop(columns=["product_id"],inplace=True)

# Preprocessing content and remove empty values
product=product[product['content'].str.strip() !='']
product["content"]=product["content"].str.replace("#"," ")
product["content"]=product["content"].str.replace("@"," ")
product["content"]=product["content"].str.replace("$"," ")
product["content"]=product["content"].str.strip()

# Save products data
data=product.to_dict(orient="records")
with open(s.products_pre, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)