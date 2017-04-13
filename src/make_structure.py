import json
import pprint


def add_branch(tree, name, extensions, folder):
    tree[name] = {'extensions': extensions, 'folder': folder}
    return tree

def remove_branch(tree, branch):
    tree.pop(branch, None)
    return tree

def rename_branch(tree, branch_key, new_key):
    tree[branch_key] = tree[new_key]
    return tree

def get_leafs(tree, branch):
    return tree[branch]

def save_file(tree, file_name):
    with open(file_name, 'w')as f:
        json.dump(tree, f, ensure_ascii=False, sort_keys=True, indent=4)

def open_file(file_name):
    with open(file_name, 'w')as f:
        return json.load(f)

def print_tree(tree, indent=4):
    pprint.pprint(tree, indent=indent)

if __name__ == '__main__':
    tree = {}
    tree = add_branch(tree,
                     'data',
                     ['.rar', '.zip', '.tar','.gz', '.bz',
                      '.tar.gz', '.tar.gz', '.tar.bz', '.whl',
                      '.tar.bz2', '.bz2', '.7z'],
                     'Data')
    tree = add_branch(tree,
                      'python',
                      ['.py'],
                      'Python')
    tree = add_branch(tree,
                      'executable',
                      ['.exe', '.msi'],
                      'Executables')
    tree = add_branch(tree,
                      'excel',
                      ['.xlsx', '.csv', '.xls'],
                      'Excel')
    tree = add_branch(tree,
                      'video',
                      ['.flv'],
                      'Videos')
    tree = add_branch(tree,
                      'pictures',
                      ['.png', '.jpeg', '.jpg'],
                      'Pictues')
    tree = add_branch(tree,
                      'sound',
                      ['.wav', '.mp3', '.mid', '.midi'],
                      'Sound')
    tree = add_branch(tree,
                      'misc',
                      ['.json', '.ppt', '.dmg',
                       '.flp', '.html', '.xml', '.tmp',
                       '.deskthemepack', '.themepack',
                       '.lnk', '.url', '.pptx'],
                      'Misc')
    tree = add_branch(tree,
                      'text',
                      ['.doc', '.txt', '.docx', '.pdf', '.rtf'],
                      'Text')
    tree = add_branch(tree,
                      'torrent',
                      ['.torrent', '.iso'],
                      'Torrents')
    save_file(tree, 'downloads_structure.json')