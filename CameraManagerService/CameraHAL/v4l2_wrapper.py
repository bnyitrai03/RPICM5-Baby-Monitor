import os
import logging
import json
from typing import Dict, Any, List, Tuple
from linuxpy.video.device import Device, MenuControl, IntegerControl

V4L_BY_PATH = "/dev/v4l/by-path/"
logger = logging.getLogger("V4L2Commands")

def get_device_paths_and_names() -> Tuple[List[str], List[str]]:
    """Returns a list of camera device paths and a list of camera names."""
    device_paths: List[str] = []
    if not os.path.exists(V4L_BY_PATH):
        logger.warning(f"Camera path {V4L_BY_PATH} not found.")
        return [],[]
    
    # Device names are dependant on USB port!
    device_names = [p for p in os.listdir(V4L_BY_PATH) if 'video-index0' in p and p.startswith('platform-xhci-hcd.1-usb-')]
    device_paths = sorted([os.path.join(V4L_BY_PATH, f) for f in device_names])
    return device_paths, device_names



def get_controls(device_path: str) -> Dict[str, Any]:
    """Reads all camera controls and returns them as a dictionary."""
    control_dict = {}
    with Device(device_path) as cam:
        for control in cam.controls.values():
            # Create a dictionary for the current control's properties
            current_control = {
                "value": control.value,
                "default": control.default,
                "type": control.__class__.__name__,
                "flags": _get_flag_names(control.flags)
            }
            
            if isinstance(control, IntegerControl):
                current_control['min'] = control.minimum
                current_control['max'] = control.maximum
                current_control['step'] = control.step
                
            elif isinstance(control, MenuControl):
                menu_options = {}
                for index, option_name in control.items():
                    menu_options[index] = option_name
                current_control['menu'] = menu_options

            control_dict[control.name] = current_control
    return control_dict


def get_supported_formats(device_path: str) -> Dict[str, Dict[str, List[int]]]:
    """
    Returns a structured dictionary of all supported pixel formats, their available resolutions,
    and the unique frame rates for each resolution.
    """
    formats_data = {}
    with Device(device_path) as cam:
        for frame_info in cam.info.frame_sizes:
            format_name = frame_info.pixel_format.name
            resolution_key = f"{frame_info.width}x{frame_info.height}"
            fps = int(frame_info.max_fps)

            # If we haven't seen this format before, add it
            if format_name not in formats_data:
                formats_data[format_name] = {}
            
            # If we haven't seen this resolution for this format, add it
            if resolution_key not in formats_data[format_name]:
                formats_data[format_name][resolution_key] = []

            # Add the FPS to the list only if it's not already there
            if fps not in formats_data[format_name][resolution_key]:
                formats_data[format_name][resolution_key].append(fps)
                formats_data[format_name][resolution_key].sort(reverse=True)
                
    return formats_data
    
    
# ---------- Helper Functions ---------------------

# These values are from the official Linux V4L2 API (videodev2.h: https://gist.github.com/JulesThuillier/bc7d1a852a7dd070af2072d946e20eed)
FLAG_MAP = {
    1:  "disabled",    # 0x0001
    2:  "grabbed",     # 0x0002
    4:  "read-only",   # 0x0004
    8:  "update",      # 0x0008
    16: "inactive",    # 0x0010
    32: "slider",      # 0x0020
    64: "write-only",  # 0x0040
    128:"volatile",    # 0x0080
}

def _get_flag_names(flag_value: int) -> List[str]:
    active_flags = []
    if not flag_value:
        return []

    for map_value, name in FLAG_MAP.items():
        if flag_value & map_value:
            active_flags.append(name)
    return active_flags

""" if __name__ == "__main__":
    camera_device = "/dev/v4l/by-id/usb-USB_Live_CAMERA_USB_Live_CAMERA_20211101016-video-index0"
    output_filename = "camera1_formats.json"
    
    try:
        data = get_supported_formats(camera_device)
        print(data)
        with open(output_filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"An unexpected error occurred: {e}") """