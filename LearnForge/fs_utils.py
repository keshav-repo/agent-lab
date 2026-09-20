import os


def list_files(directory="."):
    return os.listdir(directory)

def readFile(base_path, file_name):
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'r') as file:
        content = file.read()
    return content

