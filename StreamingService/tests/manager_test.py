import pytest
import subprocess
from unittest.mock import MagicMock
from src.manager import StreamManager
from src.models import StreamSettings, CamType

@pytest.mark.parametrize("cam_type, expected_port, expected_proxy, expected_vdev", [
    (CamType.CAMR1, 8003, "/dev/video10", "/dev/video11"),
    (CamType.CAML1, 8004, "/dev/video10", "/dev/video12"),
    (CamType.CAMR2, 8005, "/dev/video14", "/dev/video15"),
    (CamType.CAML2, 8006, "/dev/video14", "/dev/video16"),
])
def test_stream_manager_initialization_success(cam_type, expected_port, expected_proxy, expected_vdev):
    """
    Tests that the StreamManager initializes correctly for each valid camera type.
    """
    settings = StreamSettings(cam=cam_type, cam_path="/dev/test_video", fps=30, width=3840, height=1080)
    manager = StreamManager(stream_settings=settings)
    
    assert manager.settings.cam == cam_type
    assert manager.port == expected_port
    assert manager.proxy_vdev == expected_proxy
    assert manager.vdev == expected_vdev
    assert manager.processes == []


class TestStreamManagerActions:

    @pytest.fixture
    def mock_process(self, mocker):
        """
        A pytest fixture to mock subprocess.Popen
        """
        mock_popen = mocker.patch('src.manager.subprocess.Popen')
        # Create a mock process object that Popen will return
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_popen.return_value = mock_process
        
        yield {
            "popen": mock_popen,
            "process": mock_process
        }

    def test_start_stream_left_cam_success(self, mock_process):
        """
        Verify that start_stream constructs the correct commands for cam1l.
        """
        settings = StreamSettings(
            cam=CamType.CAML1,
            cam_path="/dev/video0",
            fps=30,
            width=3840,
            height=1080
        )
        manager = StreamManager(stream_settings=settings)
        
        result_url = manager.start_stream()

        mock_popen = mock_process["popen"]
        assert mock_popen.call_count == 3, "Expected Popen to be called 3 times"
        assert len(manager.processes) == 3, "Manager should track 3 processes"
        
        calls = mock_popen.call_args_list
        
        # 1. Check the ffmpeg proxy command
        cmd_proxy = calls[0].args[0]
        assert cmd_proxy[0] == "ffmpeg"
        assert cmd_proxy[8] == "3840x1080"
        assert cmd_proxy[10] == "/dev/video0"      
        assert cmd_proxy[15] == "/dev/video10"

        # 2. Check the ffmpeg split command
        cmd_split = calls[1].args[0]
        assert cmd_split[0] == "ffmpeg"
        assert cmd_split[12] == "crop=1920:1080:0:0"  # <-- Left crop (x=0)

        # 3. Check the ustreamer command
        cmd_ustreamer = calls[2].args[0]
        assert cmd_ustreamer[0] == "ustreamer"
        assert cmd_ustreamer[2] == "/dev/video12"   
        assert cmd_ustreamer[12] == "8004"           
        
        # 4. Check return value
        assert result_url == f"http://rpicm5/stream/{manager.settings.cam}/stream"
        
        
    def test_start_stream_failure_and_cleanup(self, mock_process):
        """
        Verify that if a process fails to start, all previous processes are terminated.
        """
        mock_popen = mock_process["popen"]
        mock_proc1 = MagicMock()
        mock_proc2 = MagicMock()

        mock_popen.side_effect = [
            mock_proc1, 
            mock_proc2, 
            subprocess.SubprocessError("ustreamer failed to start")
        ]
        
        manager = StreamManager()
        with pytest.raises(RuntimeError, match=f"Failed to start stream for {manager.settings.cam}"):
            manager.start_stream()
            
        # Verify that the cleanup logic was called on the processes that did start
        mock_proc1.terminate.assert_called_once()
        mock_proc1.wait.assert_called_once()
        mock_proc2.terminate.assert_called_once()
        mock_proc2.wait.assert_called_once()


    def test_stop_stream_success(self, mock_process):
        """
        Verify that stop_stream terminates all running processes.
        """
        manager = StreamManager()
        manager.start_stream()
        assert len(manager.processes) == 3
        result_msg = manager.stop_stream()

        for p in manager.processes:
            p.terminate.assert_called_once()
            p.wait.assert_called_once()

        assert not manager.processes, "Processes list should be empty after stopping"
        assert result_msg == f"Stopped stream for {manager.settings.cam}"


    def test_stop_stream_no_processes_running(self):
        """
        Verify that stop_stream raises an error if no processes are running.
        """
        manager = StreamManager()
        
        with pytest.raises(RuntimeError, match="No running processes to stop."):
            manager.stop_stream()