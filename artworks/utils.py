import os
import shutil


def get_unique_filename(path):
    name = os.path.basename(path)
    directory = os.path.dirname(path)
    print(name, directory, path)
    if not os.path.exists(path):
        return path
    else:
        base, extension = os.path.splitext(name)
        i = 1
        while os.path.exists(os.path.join(directory, '{}_{}{}'.format(base, i, extension))):
            i += 1
        return os.path.join(directory, '{}_{}{}'.format(base, i, extension))
