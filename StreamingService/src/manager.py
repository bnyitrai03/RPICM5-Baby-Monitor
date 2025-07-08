import logging
import subprocess
import time
from typing import Dict, Any, List
from .models import StreamSettings, CamType

logger = logging.getLogger("StreamManager")

class StreamManager:
    def __init__(self, stream_settings: StreamSettings = StreamSettings(
        cam=CamType.CAML1,
        cam_path="/dev/v4l/by-id/usb-3D_USB_Camera_3D_USB_Camera_01.00.00-video-index0",
        fps=30,
        width=3840,
        height=1080
    )):
        self.settings: StreamSettings = stream_settings
        self.processes: List[subprocess.Popen] = []
        
        if CamType(self.settings.cam) is CamType.CAMR1:
            self.proxy_vdev = "/dev/video10"   # Virtual device for the full stereo feed
            self.vdev = "/dev/video11"         # Virtual device for the right eye
            self.port = 8003                   # Nginx proxies /stream/camr1/ to this port
            
        elif CamType(self.settings.cam) is CamType.CAML1:
            self.proxy_vdev = "/dev/video10"
            self.vdev = "/dev/video12"
            self.port = 8004
        
        elif CamType(self.settings.cam) is CamType.CAMR2:
            self.proxy_vdev = "/dev/video14"
            self.vdev = "/dev/video15"
            self.port = 8005
        
        elif CamType(self.settings.cam) is CamType.CAML2:
            self.proxy_vdev = "/dev/video14"
            self.vdev = "/dev/video16"
            self.port = 8006

        else:
            raise ValueError(f"Cannot determine camera type: {self.settings.cam}")
    

    def start_stream(self) -> str:
        """Starts streaming processes for the cam in settings.
            Returns the stream url."""
        # Check if stream is already running!!!    

        logger.info(f"Starting stream for {self.settings.cam} on internal port {self.port}")
        try:
            # --- Command 1: ffmpeg to proxy the raw camera to a virtual device ---
            cmd_proxy = [
                "ffmpeg", "-f", "v4l2", "-input_format", "mjpeg",
                "-framerate", str(self.settings.fps), "-video_size", str(f"{self.settings.width}x{self.settings.height}"),
                "-i", self.settings.cam_path,
                "-c:v", "copy", "-f", "v4l2", self.proxy_vdev
            ]
            logger.info(cmd_proxy)
            proc_proxy = subprocess.Popen(cmd_proxy, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(proc_proxy)
            logger.info(f"Started ffmpeg proxy: PID {proc_proxy.pid}")
            time.sleep(0.4)

            # --- Command 2: ffmpeg to split the stereo feed into mono feed ---
            mono_width = int(self.settings.width / 2)
            if 'L' in self.settings.cam.name:
                # Crop the left half of the video (x=0)
                crop_filter = f"crop={mono_width}:{self.settings.height}:0:0"
            elif 'R' in self.settings.cam.name:
                # Crop the right half of the video (x=mono_width)
                crop_filter = f"crop={mono_width}:{self.settings.height}:{mono_width}:0"
            else:
                raise ValueError(f"Cannot determine crop side from camera name: {self.settings.cam.name}")
            
            cmd_split = [
                "ffmpeg", "-f", "v4l2", "-input_format", "mjpeg",
                "-framerate", str(self.settings.fps), "-video_size", str(f"{self.settings.width}x{self.settings.height}"),
                "-i", self.proxy_vdev, "-vf", crop_filter, "-c:v", "mjpeg", "-q:v", "1",      
                "-f", "v4l2", self.vdev
            ]
            logger.info(cmd_split)
            proc_split = subprocess.Popen(cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(proc_split)
            logger.info(f"Started ffmpeg split: PID {proc_split.pid}")
            time.sleep(0.4)

            # --- Commands 3: ustreamer for remote stream ---
            cmd_ustreamer = [
                "ustreamer", "-d", self.vdev, "-r", str(f"{mono_width}x{self.settings.height}"),
                "-m", "MJPEG", "-f", str(self.settings.fps),
                "--host", "127.0.0.1", "--port", str(self.port), "--tcp-nodelay", "--slowdown"
            ]
            logger.info(cmd_ustreamer)
            proc_ustreamer = subprocess.Popen(cmd_ustreamer, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(proc_ustreamer)
            logger.info(f"Started ustreamer on port {self.port}: PID {proc_ustreamer.pid}")

            return f"http://rpicm5/stream/{self.settings.cam}/stream"

        except Exception as e:
            logger.error(f"FAILED to start stream. Cleaning up processes. Error: {e}")
            # If anything fails, terminate all processes
            for p in self.processes:
                p.terminate()
                p.wait()
            raise RuntimeError(f"Failed to start stream for {self.settings.cam}")


    def stop_stream(self) -> str:
        """Stops all the processes related to the stream."""
        if not self.processes:
            raise RuntimeError("No running processes to stop.")

        logger.info(f"Stopping stream for {self.settings.cam}")

        for p in self.processes:
            try:
                p.terminate()
                p.wait()
                logger.info(f"Terminated process PID: {p.pid}")
            except Exception as e:
                logger.warning(f"Failed to terminate process: {e}")
        
        self.processes.clear()
        return f"Stopped stream for {self.settings.cam}"