import os

def delete_Recording(savedDirectory):
    # ファイルが存在するか確認
    if os.path.exists(savedDirectory):
        os.remove(savedDirectory)