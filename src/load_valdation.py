import json
import pandas as pd
from config import Settings
s=Settings()



#--------------Products-----------#

# load data and concat
def load_save_products():
    df1=pd.read_json(s.products_1_orginal)
    df2=pd.read_json(s.products_2_orginal)
    product=pd.concat([df1, df2], ignore_index=True)

# get "product_id" to data dose't have duplicates
    product['product_id']=product['metadata'].apply(lambda x: x.get('product_id') if isinstance(x, dict) else None)
    product.drop_duplicates(subset=['product_id',"content"], inplace=True)
    product.drop(columns=["product_id"],inplace=True)

# Preprocessing content and remove empty values
    product=product[product['content'].str.strip() !='']
    product["content"]=product["content"].str.replace("#"," ",regex=False)
    product["content"]=product["content"].str.replace("@"," ",regex=False)
    product["content"]=product["content"].str.replace("$"," ",regex=False)
    product["content"]=product["content"].str.strip()

# Save products data
    data=product.to_dict(orient="records")
    with open(s.products_pre, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



#--------------Users-----------#
def load_save_users():
    df_users=pd.read_json(s.users_orginal)

    # delete duplicates and null values
    df_users.drop_duplicates(inplace=True)
    df_users.dropna(inplace=True)

    # expand the events column , drop the score column and fillna values in the duration column with 0
    df_expanded = df_users.explode("events").reset_index(drop=True)
    events_df=pd.json_normalize(df_expanded["events"])
    df_users=pd.concat([df_expanded.drop(columns=["events"]), events_df], axis=1)
    df_users.drop(columns=["score"],inplace=True)
    df_users["duration"]=df_users["duration"].fillna(0)

    # map the event_type to an integer value and calculate the score for each user-product pair
    event={"product_open":1,"add_to_cart":3,"buy_click":5,"product_exit":0}
    df_users["event_int"]=df_users["event_type"].map(event).fillna(0)
    df_users["duration_norm"]=df_users["duration"]/df_users["duration"].max()
    df_users["score"]=df_users["event_int"]+df_users["duration_norm"]
    user_item_scores=df_users.groupby(["user_id","product_link"],as_index=False)["score"].sum()

    data=user_item_scores.to_dict(orient="records")
    with open(s.users_pre, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



#load_save_products()
#load_save_users()