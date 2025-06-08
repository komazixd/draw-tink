import requests
import os
import sys
import shutil
import zipfile

REPO_URL = "https://github.com/komazixd/draw-tink"
ZIP_URL = "https://github.com/komazixd/draw-tink/archive/refs/heads/main.zip"
APP_FILENAME = "drawing_app"

def update_app():
    print("hmm tink for updates...")
    r = requests.get(ZIP_URL)
    zip_path = "update.zip"
    
    with open(zip_path, "wb") as f:
        f.write(r.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("update")

    extracted_dir = os.path.join("update", os.listdir("update")[0])

    updated_file_path = os.path.join(extracted_dir, APP_FILENAME)

    if os.path.exists(updated_file_path):
        shutil.copy(updated_file_path, APP_FILENAME)
        print("Updated tinker is corect!")
    else:
        print("Update is not hear.")

    shutil.rmtree("update")
    os.remove(zip_path)

if __name__ == "__main__":
    update_app()
    os.system(f"{sys.executable} {APP_FILENAME}")
