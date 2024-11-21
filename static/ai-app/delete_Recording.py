import os

def delete_Recording(savedDirectory):
    # ファイルが存在するか確認
    if os.path.exists(savedDirectory):
        os.remove(savedDirectory)
        print(f"File {savedDirectory} deleted")
    else:
        print(f"File {savedDirectory} does not exist")