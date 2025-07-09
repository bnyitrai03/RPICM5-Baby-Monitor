import os
import logging
from typing import Dict, Any, List, Tuple
from enum import IntFlag
from linuxpy.video.device import(
    Device,
    MenuControl, 
    IntegerControl,
    BooleanControl
)

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

            snake_case_name = control.name.lower().replace(' ', '_').replace(',', '')
            control_dict[snake_case_name] = current_control
    return control_dict


def set_control(device_path: str, control_name: str, value: Any) -> bool:
    """Set a specific control value of the camera device."""
    with Device(device_path) as cam:
        try:
            control = cam.controls[control_name]
            
            if V4L2ControlFlags.INACTIVE in V4L2ControlFlags(control.flags):
                logger.warning(f"{control.name} couldn't be set because it has inactive flag")
            elif isinstance(control, (MenuControl, BooleanControl)) or (control.minimum <= value <= control.maximum):
                control.value = value
                return True
            else:
                logger.error(f"{control_name} can not be set to {value}, range: {control.minimum}...{control.maximum}")
            
            return False
            
        except KeyError:
            logger.error(f"Control '{control_name}' not found.")
            return False
        except Exception as e:
            logger.error(f"{control_name} could not be set to {value}: {e}")
            return False

def default_all_controls(device_path: str) -> List[str]:
    """Sets all controls to default values"""
    failed_to_set : List[str] = []
    with Device(device_path) as cam:
        for control in cam.controls.values():
            try:
                if V4L2ControlFlags.INACTIVE in V4L2ControlFlags(control.flags):
                    logger.warning(f"{control.name} didn't change due to inactive flag")
                    continue
                else:
                    control.set_to_default()
            except Exception as err:
                logger.error(f"{control.name} didn't default: {str(err)}")
                failed_to_set.append(control.name)
    return failed_to_set
    
    
# ---------- Helper Functions ---------------------

class V4L2ControlFlags(IntFlag):
    """These values are from the official Linux V4L2 API (videodev2.h: https://gist.github.com/JulesThuillier/bc7d1a852a7dd070af2072d946e20eed)"""
    DISABLED = 0x0001
    GRABBED = 0x0002
    READ_ONLY = 0x0004
    UPDATE = 0x0008
    INACTIVE = 0x0010
    SLIDER = 0x0020
    WRITE_ONLY = 0x0040
    VOLATILE = 0x0080


def _get_flag_names(flag_value: int) -> List[str]:
    """Convert the int flag value to human readable strings."""
    active_flags = []
    if not flag_value:
        return []

    for flag in V4L2ControlFlags:
        if flag in V4L2ControlFlags(flag_value):
            active_flags.append(flag.name.lower())
    return active_flags