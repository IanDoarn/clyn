import pprint
import json
import os
import getpass
import shutil
import collections
import create_default_structure

# TODO: Fix get_directory_tree, stop from re entering directories
# TODO: Fix get_files_and_directories, does not properly exclude directories,
# TODO: and moves files from sub-dirs when it should not.

USER = getpass.getuser()
STRUCTURE = 'structure.json'


def join(path, *paths):
    return os.path.join(path, *paths)

def print_tree(tree, indent=0):
    ordered_tree = collections.OrderedDict(sorted(tree.items(), key=lambda t: len(t[0])))
    pprint.pprint(ordered_tree, indent=indent)
    return ordered_tree

def write_json_file(tree, file_name):
    with open(file_name, 'w') as f:
        json.dump(tree, f, ensure_ascii=True, sort_keys=False, indent=4)
    f.close()

class Clean:

    def __init__(self, custom_structure=STRUCTURE, ignore_extensions=None, exclude_dirs=None, exclude_files=None):
        if ignore_extensions is None or type(ignore_extensions) is not list:
            raise ValueError('Argument: [{}] must be list not {}'.format('ignore_extensions', str(type(ignore_extensions))))
        if exclude_dirs is None or type(exclude_dirs) is not list:
                raise ValueError('Argument: [{}] must be list not {}'.format('exclude_dirs', str(type(exclude_dirs))))
        if exclude_files is None or type(exclude_files) is not list:
            raise ValueError('Argument: [{}] must be list not {}'.format('exclude_files', str(type(exclude_dirs))))

        if os.path.isfile(custom_structure):
            with open(custom_structure, 'r')as f: self.structure = json.load(f)
        else:
            try:
                create_default_structure.run()
                with open(custom_structure, 'r')as f:
                    self.structure = json.load(f)
            except Exception as ex:
                print('ERROR: [{}]'.format(str(ex)))

        self.home = os.path.expanduser("~")
        self.excluded_directories = [v['folder'] for _, v in self.structure.items()] + exclude_dirs
        self.excluded_extension = ignore_extensions
        self.excluded_files = exclude_files


    @staticmethod
    def set_current_directory(directory, user_home_dir=False, expand_with="~"):
        try:
            if user_home_dir is False:
                if os.path.exists(directory):
                    os.chdir(directory)
                return os.getcwd()
            else:
                path = os.path.join(os.path.expanduser(expand_with), directory)
                if os.path.exists(path):
                    os.chdir(path)
                return os.getcwd()
        except Exception as ex:
            print('ERROR: [{}]'.format(str(ex)))
            return None

    # @staticmethod
    # def get_files_and_directories(directory, default_roots=None, exclude_files=None, exclude_dirs=None):
    #     if exclude_dirs is None or type(exclude_dirs) is not list:
    #         raise ValueError('Argument: [{}] must be list not {}'.format('exclude_dirs', str(type(exclude_dirs))))
    #     if exclude_files is None or type(exclude_files) is not list:
    #         raise ValueError('Argument: [{}] must be list not {}'.format('exclude_files', str(type(exclude_dirs))))
    #     files = []
    #     directories = []
    #     for root, dirs, dir_files in os.walk(directory, topdown=True):
    #         dirs = [d for d in dirs if d not in exclude_dirs]
    #         if root.split('\\')[len(root.split('\\'))-1] not in exclude_dirs:
    #             for file in dir_files:
    #                 if file in exclude_files:
    #                     print("Excluding: [{}]".format(os.path.join(root, file)))
    #                 else:
    #                     files.append({'file': file, 'path': root})
    #
    #             for direct in dirs:
    #                 if any(map(lambda item: item in dirs, exclude_dirs)):
    #                     print("Excluding: [{}]".format(os.path.join(root, direct)))
    #                 else:
    #                     directories.append({'directory': direct, 'path': root})
    #     return files, directories

    def get_directory_tree(self, directory, exclude_dirs=None):
        if exclude_dirs is None or type(exclude_dirs) is not list:
            raise ValueError('Argument: [{}] must be list not {}'.format('exclude_dirs', str(type(exclude_dirs))))
        directory_tree = {'head': '', 'directories': []}
        for root, dirs, files in os.walk(directory, topdown=True):
            directory_tree['head'] = root
            for directories in dirs:
                if directories not in exclude_dirs:
                    path = join(root, directories)
                    if os.path.isdir(path):
                        contents = [i for i in os.listdir(path) if i not in exclude_dirs]
                        for i in range(len(contents)):
                            c_path = join(path, contents[i])
                            if os.path.isdir(c_path):
                                contents[i] = {'type': 'directory',
                                               'name': contents[i],
                                               'extension': None}
                            elif os.path.isfile(c_path):
                                contents[i] = {'type': 'file',
                                               'name': contents[i],
                                               'extension': os.path.splitext(contents[i])[1]}
                            else:
                                contents[i] = {'type': os.path.splitext(contents[i])[0],
                                               'name': os.path.splitext(contents[i])[0],
                                               'extension': os.path.splitext(contents[i])[1]}
                        sub_directory_tree = []
                        if len(contents) is not []:
                            data = {'directory': directories,
                                    'path': path,
                                    'root': root,
                                    'contents': contents}
                            directory_tree['directories'].append(data)
                            for item in contents:
                                sub_path = join(item['name'], path)
                                if os.path.isdir(sub_path):
                                    sub_directory_tree = self.get_directory_tree(sub_path,
                                                                                 exclude_dirs=exclude_dirs)
                            if sub_directory_tree['directories'] != []:
                                directory_tree['directories'].append(sub_directory_tree)
            return directory_tree

    def create_folders(self, directory, use_default_structure=True, overwrite=False, custom_structure=None):
        struct = self.structure if use_default_structure is True else custom_structure
        for key, value in struct.items():
            folder = os.path.join(directory, value['folder'])
            if os.path.exists(folder) and overwrite is False:
                print("Folder: [{}] already exists: [{}]".format(value['folder'], directory))
            elif os.path.exists(folder) and overwrite is True:
                print("Overwriting: [{}]".format(folder))
                os.removedirs(folder)
                os.mkdir(folder)
            else:
                os.mkdir(folder)

    @staticmethod
    def create_folder(root, directory, overwrite=False):
        folder = os.path.join(root, directory)
        if os.path.exists(folder) and overwrite is False:
            print("Folder: [{}] already exists: [{}]".format(directory, folder))
            return folder
        elif os.path.exists(folder) and overwrite is True:
            contents = os.listdir(folder)
            if len(contents) > 0:
                print("Folder: [{}] is not empty: [{}] files".format(folder, str(contents)))
                if input("Remove {}? [Y/N]".format(folder)).upper() is "Y":
                    print("Overwriting: [{}]".format(folder))
                    os.removedirs(folder)
                    os.mkdir(folder)
                    return folder
        else:
            os.mkdir(folder)
            return folder

    @staticmethod
    def move_file(file, from_directory, to_directory):
        try:
            print("Moving: [{}] [{} -> {}]".format(file,
                                                   os.path.join(from_directory, file),
                                                   os.path.join(to_directory, file)))
            shutil.move(os.path.join(from_directory, file),
                        os.path.join(to_directory, file))
        except Exception as ex:
            print('ERROR: {}'.format(str(ex)))

    @staticmethod
    def move_directory(directory, from_directory, to_directory):
        from_d = os.path.join(from_directory, directory)

        if os.path.exists(from_d) is False:
            raise NotADirectoryError('{} is not a directory'.format(from_d))
        if os.path.exists(to_directory):
            try:
                print("Moving: [{} -> {}]".format(os.path.join(from_directory, directory),
                                                  to_directory))
                shutil.move(os.path.join(from_directory, directory),
                            to_directory)
            except Exception as ex:
                print('ERROR: {}'.format(str(ex)))




if __name__ == '__main__':
    cl = Clean(ignore_extensions=[],
               exclude_dirs=['.git', '.idea', '__pycache__'],
               exclude_files=[])

    head = 'desktop'

    directory = cl.set_current_directory(head, user_home_dir=True)
    directory_tree = cl.get_directory_tree(directory, exclude_dirs=cl.excluded_directories)
    tree = {'head': head, 'tree': directory_tree}

    file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'desktop_tree.json')
    write_json_file(tree, file_name)
