import os
import json

directory = r"C:\Users\Admin\Documents\GitHub\MovieGenius\PyMovieDb-master\PyMovieDb-master\movies\2017"

def check_json_file(file_path, content):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data == content
    except UnicodeDecodeError:
        print(f"{ct1}. Deleted file at: {file_path}")
        os.remove(file_path)
        return False
    except json.JSONDecodeError:
        print(f"{ct1}. Deleted file at: {file_path}")
        os.remove(file_path)
        return False

ct1 = 0
for filename in os.listdir(directory):
    ct1 += 1
    if filename.endswith('.json'):
        file_path = os.path.join(directory, filename)
        if check_json_file(file_path, {
            "status": 404,
            "message": "No Result Found!",
            "result_count": 0,
            "results": []
        }):
            print(f"{ct1}. Deleted file at: {file_path}")
            os.remove(file_path)
