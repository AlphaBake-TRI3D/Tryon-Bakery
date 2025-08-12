import json
import os
import io
from PIL import Image
import boto3
from dotenv import load_dotenv
import shutil

load_dotenv()
from_json_path = 'outputs/200pairs-v3-comparision.json'
to_json_path = '../samples/200pairs-v3-comparision.json'

if not os.path.exists(to_json_path):
    shutil.copy(from_json_path, to_json_path)
    print(f'{to_json_path} created')
    exit()

from_json = json.load(open(from_json_path))
to_json = json.load(open(to_json_path))




# update the urls alone in the samples/
for cur_folder in to_json:
    # add a new key to the json
    to_json[cur_folder]['garment_type'] = None
    for model_name in to_json[cur_folder]:
        print(model_name)


        if model_name in from_json[cur_folder]:
            print(model_name)
            to_json[cur_folder][model_name] = from_json[cur_folder][model_name]
with open(to_json_path, 'w') as f:
    json.dump(to_json, f, indent=4)











