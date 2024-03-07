import weaviate.classes.config as wc
import weaviate.classes.data as wd
import weaviate.classes.query as wq
from tqdm import tqdm
from weaviate.util import generate_uuid5
import weaviate
import h5py
from pathlib import Path
from config import COLL_NAME, N_MAX_IMPORT
from utils import measure_mem_usage


# Load data
sift_file = Path("data/dbpedia-openai-1000k-angular.hdf5")
f = h5py.File(sift_file)
train_vectors = f["train"]


# Connect to Weaviate
client = weaviate.connect_to_local()

client.collections.delete(COLL_NAME)

# Create collection
collection = client.collections.create(
    name=COLL_NAME,
    properties=[
        wc.Property(name="name", data_type=wc.DataType.TEXT),
    ],
)

# Add objects
output_prefix = "hnsw_uncompressed_import"
with collection.batch.dynamic() as batch:
    for i, vector in enumerate(tqdm(train_vectors[:N_MAX_IMPORT])):
        if i % 100000 == 0 and i != 0:
            measure_mem_usage(f"{output_prefix}_{i}")

        padding = "0" * (7 - len(str(i)))
        properties = {"name": f"DBPedia_{padding}{i}"}
        batch.add_object(
            properties=properties,
            uuid=generate_uuid5(i),
            vector=list(vector)
        )

measure_mem_usage(f"{output_prefix}_{i}")
