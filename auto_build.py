import time
import os
import subprocess

WATCHED_FILE = r"C:\Users\omars\OneDrive\Documents\GitHub\draw-tink\main.py"
EXE_OUTPUT_PATH = r"C:\Users\omars\OneDrive\Documents\GitHub\draw-tink\dist\main.exe"
LOG_FILE = r"C:\Users\omars\OneDrive\Documents\GitHub\draw-tink\auto_build.log"

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def get_mod_time(path):
    try:
        return os.path.getmtime(path)
    except Exception as e:
        log(f"Error getting mod time: {e}")
        return 0

def build_exe():
    try:
        # You can adjust pyinstaller options here
        subprocess.run([
            "pyinstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--name", "main",
            WATCHED_FILE
        ], check=True)
        log("Build succeeded")
    except subprocess.CalledProcessError as e:
        log(f"Build failed: {e}")

def main():
    last_mod_time = get_mod_time(WATCHED_FILE)
    log("Watcher started")
    while True:
        time.sleep(1.5)
        current_mod_time = get_mod_time(WATCHED_FILE)
        if current_mod_time != last_mod_time:
            log("Change detected, rebuilding exe...")
            build_exe()
            last_mod_time = current_mod_time

if __name__ == "__main__":
    main()
