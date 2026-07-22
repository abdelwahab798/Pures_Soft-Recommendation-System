import pandas as pd
from config import Settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

s=Settings()


def embedding_send_Qdrant():
  model = SentenceTransformer(s.embedding_model)
  client = QdrantClient(url=s.Qdrant_end_point, api_key=s.Qdrant_api_key, timeout=120)

  df=pd.read_json(s.products_pre)
  products_data=df.to_dict(orient="records")

  if not client.collection_exists(collection_name=s.COLLECTION_NAME):
    client.create_collection(
        collection_name=s.COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

  BATCH_SIZE=256
  total_products=len(products_data)

  print(f"embeddings and uploading {total_products} products")

  for i in tqdm(range(0, total_products, BATCH_SIZE)):
    batch = products_data[i : i + BATCH_SIZE]

    texts = [prod.get("content", "") for prod in batch]
    vectors = model.encode(texts, show_progress_bar=False).tolist()

    points = []
    for idx, (prod, vector) in enumerate(zip(batch, vectors)):
      point_id = i + idx
      metadata = prod.get("metadata", {})
      points.append(
          PointStruct(
              id=point_id,
              vector=vector,
              payload={
                  "product_id": metadata.get("product_id"),
                  "content": prod.get("content", ""),
                  "category": metadata.get("category"),
                  "price": metadata.get("price"),
                  "product_link": metadata.get("product_link"),
              },
          )
      )

    client.upsert(collection_name=s.COLLECTION_NAME, points=points)

  print(f"Uploaded {total_products} products")

embedding_send_Qdrant()