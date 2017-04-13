import json
import os

with open('data\\extensions.json')as f: DATA = json.load(f)

def get_file_extension_information(file):
    file_name, extension = os.path.splitext(file)

    for ext_info in DATA['data']:
        if ext_info[0] == extension:
            ext_info[1] = ext_info[1].replace('   ', '')
            return ext_info, file_name, extension
    return None, None, extension
