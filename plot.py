import pandas as pd
import plotly.express as px
import plotly.io as pio


df = pd.read_json("test_outputs.json")
df.sort_values(by=["index_type", "compression", "object_count"], inplace=True)
df = df.assign(index_compression=lambda x: x["index_type"] + "_" + x["compression"])
print(df.head())

pio.templates.default = "simple_white"
px.defaults.template = "ggplot2"
fig = px.line(
    df,
    title="Example Weaviate memory usage by vector index type & config",
    x="object_count",
    y="memory_usage",
    color="index_compression",
    labels={
        "memory_usage": "Memory usage (MB)",
        "object_count": "Object count",
        "index_compression": "Index type & compression",
    },
    width=800,
    height=600,
    markers=True,
)
fig.show()
