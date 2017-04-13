import json
import os
import getpass
import shutil
import create_default_structure

USER = getpass.getuser()
STRUCTURE = 'structure.json'
class Clean:

    def __init__(self, custom_structure=STRUCTURE, ignore_extensions=None):
        if ignore_extensions is None or type(ignore_extensions) is not list:
            raise ValueError('Argument: [{}] must be list not {}'.format('ignore_extensions', str(type(ignore_extensions))))
        if os.path.isfile(custom_structure):
            with open(custom_structure, 'r')as f: self.structure = json.load(f)
        else:
            try:
                create_default_structure.run()
                with open(custom_structure, 'r')as f:
                    self.structure = json.load(f)
            except Exception as ex:
                print('ERROR: [{}]'.format(str(ex)))
        print("Loading structure [{}]".format(custom_structure))

        self.home = os.path.expanduser("~")
        self.excluded_directories = [v['folder'] for _, v in self.structure.items()]
        self.excluded_extension = ignore_extensions

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

    @staticmethod
    def get_files_and_directories(directory, default_roots=None, exclude_files=None, exclude_dirs=None):
        if exclude_dirs is None or type(exclude_dirs) is not list:
            raise ValueError('Argument: [{}] must be list not {}'.format('exclude_dirs', str(type(exclude_dirs))))
        if exclude_files is None or type(exclude_files) is not list:
            raise ValueError('Argument: [{}] must be list not {}'.format('exclude_files', str(type(exclude_dirs))))
        files = []
        directories = []
        for root, dirs, dir_files in os.walk(directory, topdown=True):
            dirs = [d for d in dirs if d not in exclude_dirs]
            if root.split('\\')[len(root.split('\\'))-1] not in exclude_dirs:
                for file in dir_files:
                    if file in exclude_files:
                        print("Excluding: [{}]".format(os.path.join(root, file)))
                    else:
                        files.append({'file': file, 'path': root})

                for direct in dirs:
                    if any(map(lambda item: item in dirs, exclude_dirs)):
                        print("Excluding: [{}]".format(os.path.join(root, direct)))
                    else:
                        directories.append({'directory': direct, 'path': root})
        return files, directories

    def create_folders(self, directory, overwrite=False):
        for key, value in self.structure.items():
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


    def clean(self,
              directory,
              auto_create_folders=False,
              move_directories=False,
              walk=False,
              exclude_files=None,
              exclude_dirs=None):

        if walk is not True:
            files = [{'file': f, 'path': directory} for f in os.listdir(directory)
                     if os.path.isfile(os.path.join(directory, f))]
            directories = [{'directory': f, 'path': directory} for f in os.listdir(directory)
                           if os.path.exists(directory)]
        else:
            files, directories = self.get_files_and_directories(directory,
                                                                default_roots=[v['folder'] for k, v in self.structure.items()],
                                                                exclude_dirs=self.excluded_directories + exclude_dirs,
                                                                exclude_files=exclude_files)

        if auto_create_folders:
            self.create_folders(directory)

        for key, value in self.structure.items():
            for file in files:
                file_name, extension = os.path.splitext(file['file'])
                extension = extension.lower()
                if extension in self.excluded_extension:
                    print("Excluding: [{}]".format(os.path.join(file['path'], file['file'])))
                elif extension in value['extensions']:
                    self.move_file(file['file'],
                                   file['path'],
                                   os.path.join(directory, value['folder']))

        if move_directories:
            new_folder = self.create_folder(directory, "{}'s Files".format(USER))
            for folder in directories:
                self.move_directory(folder['directory'],
                                    folder['path'],
                                    new_folder)


def main(directory, custom=None, ignore_ext=None, use_home=True, exclude_dirs=None, exclude_files=None, move_dirs=False, walk=False):
    clean = Clean(ignore_extensions=ignore_ext,
                  custom_structure=custom)
    directory = clean.set_current_directory(directory, user_home_dir=use_home)
    clean.clean(directory,
                auto_create_folders=True,
                walk=walk,
                move_directories=move_dirs,
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files)

if __name__ == '__main__':
    dls = os.path.join(os.path.expanduser("~"), "Downloads")
    excluded_directories = [i for i in os.listdir(dls) if os.path.isdir(os.path.join(dls, i))]
    main('downloads',
         custom='downloads_structure.json',
         ignore_ext=[],
         walk=True,
         move_dirs=False,
         exclude_dirs=excluded_directories + ['Program Files', 'Program Files (x86)'],
         exclude_files=[])
