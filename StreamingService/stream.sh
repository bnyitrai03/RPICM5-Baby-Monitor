#!/bin/bash

# --- Configuration ---
# Make sure these paths are correct for your system.
CAM1_PATH="/dev/v4l/by-id/usb-USB_Live_CAMERA_USB_Live_CAMERA_20211101016-video-index0"
CAM2_PATH="/dev/v4l/by-id/usb-webcamvendor_webcamproduct_00000000-video-index0"

# --- Start the Streams ---
# Each ffmpeg command runs in the background (&)

echo "Starting stream for Camera 1 (Live Camera)"
ffmpeg \
    -f v4l2 -input_format h264 -i "$CAM1_PATH" \
    -c:v copy -an -f rtsp -rtsp_transport tcp \
    rtsp://localhost:8554/cam1 &

echo "Starting stream for Camera 2 (Webcam Product)"
ffmpeg \
    -f v4l2 -input_format h264 -i "$CAM2_PATH" \
    -c:v copy -an -f rtsp -rtsp_transport tcp \
    rtsp://localhost:8554/cam2 &

# Keep the script running
echo "Both streams started. Script will wait for them to finish."
wait
