# streaming_service.py
import subprocess
import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = Path(__file__).parent / "camera_config.json"
MEDIAMTX_URL = "rtsp://localhost:8554"

# This dictionary will hold our running ffmpeg processes
active_streams = {}

def build_ffmpeg_command(camera_config):
    """Constructs the ffmpeg command from camera settings."""
    device_path = camera_config['device_path']
    resolution = camera_config.get('resolution', '1280x720')
    cam_id = camera_config['id']
    
    # NOTE: -s {resolution} is an INPUT option here!
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-input_format', 'h264',
        '-s', resolution, # Set resolution BEFORE the input device
        '-i', device_path,
        '-c:v', 'copy',
        '-an',
        '-f', 'rtsp',
        '-rtsp_transport', 'tcp',
        f'{MEDIAMTX_URL}/{cam_id}'
    ]
    return command

def start_or_restart_all_streams():
    """
    Reads the config file and ensures the ffmpeg processes match the config.
    Stops old streams, starts new ones, and restarts modified ones.
    """
    global active_streams
    print("Configuration changed or initial start. Syncing streams...")
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Config file not found or invalid. Stopping all streams.")
        config = {}

    current_cam_ids = {cam['id'] for cam in config.values()}
    running_cam_ids = set(active_streams.keys())

    # Stop streams for cameras that were removed from config
    for cam_id in running_cam_ids - current_cam_ids:
        print(f"Stopping stream for removed camera: {cam_id}")
        active_streams[cam_id].terminate()
        active_streams.pop(cam_id)

    # Start or restart streams for cameras in the config
    for cam_config in config.values():
        cam_id = cam_config['id']
        command = build_ffmpeg_command(cam_config)
        
        # If stream is already running, terminate it before restarting
        if cam_id in active_streams:
            print(f"Restarting stream for {cam_id} with new settings...")
            active_streams[cam_id].terminate()
            time.sleep(1) # Give it a moment to release the device

        print(f"Starting stream for {cam_id}: {' '.join(command)}")
        # Start the new ffmpeg process
        process = subprocess.Popen(command)
        active_streams[cam_id] = process

class ConfigHandler(FileSystemEventHandler):
    """Handler for when the config file is modified."""
    def on_modified(self, event):
        if event.src_path == str(CONFIG_FILE):
            start_or_restart_all_streams()

if __name__ == "__main__":
    # Initial start
    start_or_restart_all_streams()

    # Set up the watchdog observer
    event_handler = ConfigHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(CONFIG_FILE.parent), recursive=False)
    
    print(f"Watching {CONFIG_FILE} for changes...")
    observer.start()

    try:
        while True:
            # Keep the main thread alive, checking on subprocesses
            time.sleep(5)
            for cam_id, process in list(active_streams.items()):
                if process.poll() is not None: # Check if process has terminated
                    print(f"Stream for {cam_id} has stopped unexpectedly. Removing from active list.")
                    active_streams.pop(cam_id)
                    # You could add logic here to automatically restart it
    except KeyboardInterrupt:
        observer.stop()
        print("Stopping all streams...")
        for process in active_streams.values():
            process.terminate()
    observer.join()