import requests, zipfile, os, sys, shutil

REPO_URL = "https://github.com/komazixd/draw-tink"
REPO_RAW_URL = "https://raw.githubusercontent.com/komazixd/draw-tink/main"
FILENAME = "main.py"  # your main drawing app file name

def update():
    try:
        print("[UPDATER] Checking for updates...")
        r = requests.get(f"{REPO_RAW_URL}/{FILENAME}")
        if r.status_code == 200:
            with open("main_updated.py", "w", encoding="utf-8") as f:
                f.write(r.text)
            print("[UPDATER] Update downloaded. Launching new version.")
            os.system(f"python main_updated.py")
        else:
            print("[UPDATER] No update found.")
    except Exception as e:
        print(f"[UPDATER] Failed to update: {e}")

if __name__ == "__main__":
    update()
