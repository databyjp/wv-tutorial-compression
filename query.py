import weaviate
from config import COLL_NAME, N_MAX_IMPORT

client = weaviate.connect_to_local()

collection = client.collections.get(COLL_NAME)

print(collection.aggregate.over_all(total_count=True).total_count)

client.close()
