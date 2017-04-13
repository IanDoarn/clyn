import json
import os

with open('data\\extensions.json')as f: DATA = json.load(f)

def get_file_extension_information(file):
    file_name, extension = os.path.splitext(file)

    for ext_info in DATA['data']:
        if ext_info[0] == extension:
            return ext_info, file_name, extension
    return None, None, extension

if __name__ == '__main__':
    extensions_list = ['.g', '.rtf', '.xlsx', '.bat', '.pyc', '.cs', '.h']
    for ext in extensions_list:
        ext_info, file_name, extension = get_file_extension_information('test.{}'.format(ext))
        if None not in [ext_info, file_name, extension]:
            print("{}[{}] {}".format(file_name, ext_info[0], ext_info[1]))
        else:
            print("[{}] is not a known file extension".format(extension))