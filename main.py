import os
import subprocess
import threading
import time
from flask import Flask

app = Flask(__name__)

APP_SCRIPT = "app.py"          # The script to monitor
CHECK_INTERVAL = 300           # 5 minutes (300 seconds)
process = None                 # Store Popen process if needed

def is_process_running(script_name):
    """Check if a process is running using pgrep."""
    try:
        output = subprocess.check_output(["pgrep", "-f", script_name])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def start_app():
    """Start the target app.py script."""
    global process
    if os.path.exists(APP_SCRIPT):
        print(f"▶️ Starting {APP_SCRIPT}...")
        process = subprocess.Popen(["python3", APP_SCRIPT], start_new_session=True)
    else:
        print(f"❌ ERROR: {APP_SCRIPT} not found!")

def monitor_loop():
    """Background monitor loop that checks the app."""
    while True:
        if not is_process_running(APP_SCRIPT):
            print(f"🔁 {APP_SCRIPT} is not running. Restarting...")
            start_app()
        else:
            print(f"✅ {APP_SCRIPT} is running.")
        time.sleep(CHECK_INTERVAL)

@app.route("/")
def status_page():
    running = is_process_running(APP_SCRIPT)
    return f"""
    <html>
      <head><title>App Monitor Status</title></head>
      <body style='font-family:sans-serif;text-align:center;margin-top:50px;'>
        <h1>🖥️ Monitor Status</h1>
        <h2>{APP_SCRIPT} is {'<span style="color:green;">Running ✅</span>' if running else '<span style="color:red;">Not Running ❌</span>'}</h2>
        <p>Checked every {CHECK_INTERVAL} seconds.</p>
      </body>
    </html>
    """

if __name__ == "__main__":
    # Start the monitoring loop in a background thread
    threading.Thread(target=monitor_loop, daemon=True).start()

    # Run the Flask server
    app.run(host="0.0.0.0", port=8000)
