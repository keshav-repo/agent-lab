from fs_utils import list_files, readFile

base_path = '/Users/keshavkumar/learn26/agent-lab/LearnForge/jsons'

files = list_files(base_path)


content = readFile(base_path, files[0])
