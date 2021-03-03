import json
import os
import sys
import csv
from glob import glob
import pandas

data_location = sys.argv[1]
data = []
for f_name in glob(os.path.join(data_location, "datasets/default", "*.json")):
    with open(f_name, encoding="utf-8") as json_file:
        data.append(json.load(json_file))
df = pandas.DataFrame.from_records(data)
df.to_csv("data.csv", index=False)
