import weaviate.classes.config as wc
import weaviate.classes.data as wd
import weaviate.classes.query as wq
from weaviate.collections import Collection
from tqdm import tqdm
from weaviate.util import generate_uuid5
import weaviate
import h5py
from pathlib import Path
from utils import measure_mem_usage, parse_results_text, restart_weaviate


N_MAX_IMPORT = 1000000
COLL_NAME = "DBPedia"


def reconfigure_pq(tgt_collection: Collection):
    tgt_collection.config.update(
        vector_index_config=wc.Reconfigure.VectorIndex.hnsw(
            quantizer=wc.Reconfigure.VectorIndex.Quantizer.pq()
        )
    )


def do_nothing(*args, **kwargs):
    pass


# Load data
sift_file = Path("data/dbpedia-openai-1000k-angular.hdf5")
f = h5py.File(sift_file)
train_vectors = f["train"]


# Connect to Weaviate


for output_prefix, reconfigure_function, vector_index_config in [
    ("hnsw_uncompressed", do_nothing, wc.Configure.VectorIndex.hnsw()),
    ("hnsw_pq", reconfigure_pq, wc.Configure.VectorIndex.hnsw()),
    (
        "hnsw_bq",
        do_nothing,
        wc.Configure.VectorIndex.hnsw(
            quantizer=wc.Configure.VectorIndex.Quantizer.bq()
        ),
    ),
    (
        "flat_bq",
        do_nothing,
        wc.Configure.VectorIndex.flat(
            quantizer=wc.Configure.VectorIndex.Quantizer.bq()
        ),
    ),
    ("flat_uncompressed", do_nothing, wc.Configure.VectorIndex.flat()),
]:
    client = weaviate.connect_to_local()
    client.collections.delete(COLL_NAME)
    client.close()

    restart_weaviate()

    client = weaviate.connect_to_local()

    # Create collection
    collection = client.collections.create(
        name=COLL_NAME,
        properties=[
            wc.Property(name="name", data_type=wc.DataType.TEXT),
        ],
        vector_index_config=vector_index_config,
    )

    # Add objects
    with collection.batch.dynamic() as batch:
        for i, vector in enumerate(tqdm(train_vectors[:N_MAX_IMPORT])):
            real_i = i + 1  # 1-based index

            padding = "0" * (7 - len(str(real_i)))
            properties = {"name": f"DBPedia_{padding}{real_i}"}
            batch.add_object(
                properties=properties, uuid=generate_uuid5(real_i), vector=list(vector)
            )

            if real_i == 100000:
                reconfigure_function(collection)

            if real_i % 100000 == 0:
                measure_mem_usage(f"{output_prefix}_{real_i}")


parse_results_text()

client.close()
