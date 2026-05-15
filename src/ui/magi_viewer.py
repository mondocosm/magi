"""
MAGI Viewer - Display MAGI format videos with proper cadence
Similar to Blur Busters for high-frame-rate display testing
"""

import asyncio
import json
import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi import APIRouter

from ..core.logger import LoggerMixin


class MAGIViewer(LoggerMixin):
    """MAGI video viewer with proper cadence display"""
    
    def __init__(self):
        """Initialize MAGI viewer"""
        self.active_connections: List[WebSocket] = []
        self.current_video: Optional[str] = None
        self.is_playing = False
        self.current_frame = 0
        self.frame_rate = 120
        self.playback_speed = 1.0
        
        # MAGI-specific settings
        self.eye_separation = 180  # degrees
        self.cadence_mode = "alternating"  # L-R-L-R...
        
        # Display settings
        self.show_frame_info = True
        self.show_cadence_indicator = True
        self.show_fps_counter = True
        
        # Test patterns
        self.test_patterns = {
            "motion_blur": self._create_motion_blur_pattern,
            "pursuit_camera": self._create_pursuit_camera_pattern,
            "ufo_test": self._create_ufo_test_pattern,
            "frame_pacing": self._create_frame_pacing_pattern,
            "eye_separation": self._create_eye_separation_pattern,
        }
        
        self.logger.info("MAGIViewer initialized")
    
    async def connect(self, websocket: WebSocket):
        """Connect a WebSocket client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                self.logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_frame(self, frame_data: bytes, frame_info: Dict[str, Any]):
        """Send a frame to all connected clients"""
        message = {
            "type": "frame",
            "data": frame_data,
            "info": frame_info,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message)
    
    async def send_test_pattern(self, pattern_name: str, pattern_data: bytes):
        """Send a test pattern to all connected clients"""
        message = {
            "type": "test_pattern",
            "pattern": pattern_name,
            "data": pattern_data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message)
    
    def load_video(self, video_path: str):
        """Load a MAGI video file"""
        self.current_video = video_path
        self.current_frame = 0
        self.is_playing = False
        self.logger.info(f"Loaded video: {video_path}")
    
    def play(self):
        """Start video playback"""
        if self.current_video:
            self.is_playing = True
            self.logger.info("Playback started")
    
    def pause(self):
        """Pause video playback"""
        self.is_playing = False
        self.logger.info("Playback paused")
    
    def stop(self):
        """Stop video playback"""
        self.is_playing = False
        self.current_frame = 0
        self.logger.info("Playback stopped")
    
    def seek(self, frame_number: int):
        """Seek to a specific frame"""
        self.current_frame = frame_number
        self.logger.info(f"Seeked to frame {frame_number}")
    
    def set_playback_speed(self, speed: float):
        """Set playback speed"""
        self.playback_speed = speed
        self.logger.info(f"Playback speed set to {speed}x")
    
    def get_frame_info(self) -> Dict[str, Any]:
        """Get current frame information"""
        return {
            "current_frame": self.current_frame,
            "frame_rate": self.frame_rate,
            "playback_speed": self.playback_speed,
            "is_playing": self.is_playing,
            "current_video": self.current_video,
            "cadence_mode": self.cadence_mode,
            "eye_separation": self.eye_separation,
        }
    
    def _create_motion_blur_pattern(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """Create motion blur test pattern"""
        # Create a pattern with moving objects to test motion blur
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add moving bars
        bar_width = 50
        num_bars = 10
        for i in range(num_bars):
            x = int((i / num_bars) * width)
            color = 255 if i % 2 == 0 else 0
            pattern[:, x:x+bar_width] = color
        
        return pattern
    
    def _create_pursuit_camera_pattern(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """Create pursuit camera test pattern"""
        # Create a pattern with a moving object to test pursuit camera
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add a moving circle
        center_x = width // 2
        center_y = height // 2
        radius = 100
        
        y, x = np.ogrid[:height, :width]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        pattern[mask] = 255
        
        return pattern
    
    def _create_ufo_test_pattern(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """Create UFO test pattern (similar to Blur Busters)"""
        # Create a pattern with UFOs moving across the screen
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add background
        pattern[:, :] = [50, 50, 50]
        
        # Add UFOs
        ufo_size = 50
        num_ufos = 5
        for i in range(num_ufos):
            x = int((i / num_ufos) * width)
            y = height // 2
            
            # Draw UFO
            pattern[y-ufo_size:y+ufo_size, x-ufo_size:x+ufo_size] = [255, 255, 255]
        
        return pattern
    
    def _create_frame_pacing_pattern(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """Create frame pacing test pattern"""
        # Create a pattern to test frame pacing
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add alternating colors to test frame pacing
        for i in range(height):
            color = 255 if i % 2 == 0 else 0
            pattern[i, :] = color
        
        return pattern
    
    def _create_eye_separation_pattern(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """Create eye separation test pattern"""
        # Create a pattern to test eye separation
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add left eye pattern (red)
        pattern[:, :width//2] = [255, 0, 0]
        
        # Add right eye pattern (blue)
        pattern[:, width//2:] = [0, 0, 255]
        
        return pattern
    
    def get_test_pattern(self, pattern_name: str, width: int = 1920, height: int = 1080) -> np.ndarray:
        """Get a test pattern"""
        if pattern_name in self.test_patterns:
            return self.test_patterns[pattern_name](width, height)
        else:
            raise ValueError(f"Unknown test pattern: {pattern_name}")
    
    def get_available_test_patterns(self) -> List[str]:
        """Get list of available test patterns"""
        return list(self.test_patterns.keys())


# Create router for MAGI viewer API
viewer_router = APIRouter(prefix="/viewer", tags=["viewer"])
viewer_instance = MAGIViewer()


@viewer_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time video streaming"""
    await viewer_instance.connect(websocket)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "play":
                viewer_instance.play()
            elif data.get("type") == "pause":
                viewer_instance.pause()
            elif data.get("type") == "stop":
                viewer_instance.stop()
            elif data.get("type") == "seek":
                viewer_instance.seek(data.get("frame", 0))
            elif data.get("type") == "speed":
                viewer_instance.set_playback_speed(data.get("speed", 1.0))
            elif data.get("type") == "load":
                viewer_instance.load_video(data.get("video_path", ""))
            
            # Send frame info back
            await websocket.send_json({
                "type": "frame_info",
                "info": viewer_instance.get_frame_info(),
            })
    
    except WebSocketDisconnect:
        viewer_instance.disconnect(websocket)


@viewer_router.get("/test-patterns")
async def get_test_patterns():
    """Get available test patterns"""
    return {
        "patterns": viewer_instance.get_available_test_patterns(),
        "description": "Test patterns for evaluating MAGI display performance",
    }


@viewer_router.get("/frame-info")
async def get_frame_info():
    """Get current frame information"""
    return viewer_instance.get_frame_info()


@viewer_router.post("/load-video")
async def load_video(video_path: str):
    """Load a video file"""
    viewer_instance.load_video(video_path)
    return {"status": "success", "message": f"Loaded video: {video_path}"}


@viewer_router.post("/play")
async def play_video():
    """Start video playback"""
    viewer_instance.play()
    return {"status": "success", "message": "Playback started"}


@viewer_router.post("/pause")
async def pause_video():
    """Pause video playback"""
    viewer_instance.pause()
    return {"status": "success", "message": "Playback paused"}


@viewer_router.post("/stop")
async def stop_video():
    """Stop video playback"""
    viewer_instance.stop()
    return {"status": "success", "message": "Playback stopped"}


@viewer_router.post("/seek")
async def seek_video(frame: int):
    """Seek to a specific frame"""
    viewer_instance.seek(frame)
    return {"status": "success", "message": f"Seeked to frame {frame}"}


@viewer_router.post("/speed")
async def set_speed(speed: float):
    """Set playback speed"""
    viewer_instance.set_playback_speed(speed)
    return {"status": "success", "message": f"Playback speed set to {speed}x"}


@viewer_router.get("/viewer")
async def get_viewer_page():
    """Get the MAGI viewer HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MAGI Viewer</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0a0a0a;
                color: #ffffff;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            .header {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                padding: 20px;
                text-align: center;
                border-bottom: 2px solid #0f3460;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #00d4ff, #7b2cbf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header p {
                color: #a0a0a0;
                font-size: 1.1em;
            }
            
            .main-content {
                flex: 1;
                display: flex;
                padding: 20px;
                gap: 20px;
            }
            
            .viewer-container {
                flex: 1;
                background: #1a1a1a;
                border-radius: 10px;
                padding: 20px;
                display: flex;
                flex-direction: column;
            }
            
            .video-display {
                flex: 1;
                background: #000;
                border-radius: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                min-height: 400px;
            }
            
            .video-display canvas {
                max-width: 100%;
                max-height: 100%;
            }
            
            .frame-info {
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0, 0, 0, 0.7);
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 14px;
            }
            
            .cadence-indicator {
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(0, 0, 0, 0.7);
                padding: 10px;
                border-radius: 5px;
                font-size: 24px;
                font-weight: bold;
            }
            
            .cadence-indicator.left {
                color: #00ff00;
            }
            
            .cadence-indicator.right {
                color: #ff0000;
            }
            
            .controls {
                margin-top: 20px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .control-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            
            .control-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .control-btn:active {
                transform: translateY(0);
            }
            
            .control-btn:disabled {
                background: #555;
                cursor: not-allowed;
                transform: none;
            }
            
            .sidebar {
                width: 300px;
                background: #1a1a1a;
                border-radius: 10px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .sidebar h2 {
                font-size: 1.5em;
                margin-bottom: 10px;
                color: #00d4ff;
            }
            
            .test-patterns {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .pattern-btn {
                background: #2d2d2d;
                color: white;
                border: 1px solid #444;
                padding: 10px;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .pattern-btn:hover {
                background: #3d3d3d;
                border-color: #667eea;
            }
            
            .settings {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .setting-item {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .setting-item label {
                font-size: 14px;
                color: #a0a0a0;
            }
            
            .setting-item input,
            .setting-item select {
                background: #2d2d2d;
                color: white;
                border: 1px solid #444;
                padding: 8px;
                border-radius: 5px;
            }
            
            .stats {
                background: #2d2d2d;
                padding: 15px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 14px;
            }
            
            .stats h3 {
                margin-bottom: 10px;
                color: #00d4ff;
            }
            
            .stat-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }
            
            .stat-label {
                color: #a0a0a0;
            }
            
            .stat-value {
                color: #00ff00;
            }
            
            .footer {
                background: #1a1a1a;
                padding: 20px;
                text-align: center;
                border-top: 2px solid #0f3460;
            }
            
            .footer p {
                color: #a0a0a0;
            }
            
            @media (max-width: 768px) {
                .main-content {
                    flex-direction: column;
                }
                
                .sidebar {
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>MAGI Viewer</h1>
            <p>High-Frame-Rate 3D Cinema Display - Similar to Blur Busters</p>
        </div>
        
        <div class="main-content">
            <div class="viewer-container">
                <div class="video-display">
                    <canvas id="videoCanvas"></canvas>
                    <div class="frame-info" id="frameInfo">
                        Frame: 0 | FPS: 120 | Eye: Left
                    </div>
                    <div class="cadence-indicator left" id="cadenceIndicator">L</div>
                </div>
                
                <div class="controls">
                    <button class="control-btn" id="playBtn">▶ Play</button>
                    <button class="control-btn" id="pauseBtn">⏸ Pause</button>
                    <button class="control-btn" id="stopBtn">⏹ Stop</button>
                    <button class="control-btn" id="loadBtn">📁 Load Video</button>
                    <input type="file" id="videoInput" accept=".mp4,.mkv,.magi" style="display: none;">
                </div>
            </div>
            
            <div class="sidebar">
                <div>
                    <h2>Test Patterns</h2>
                    <div class="test-patterns">
                        <button class="pattern-btn" data-pattern="motion_blur">Motion Blur Test</button>
                        <button class="pattern-btn" data-pattern="pursuit_camera">Pursuit Camera</button>
                        <button class="pattern-btn" data-pattern="ufo_test">UFO Test</button>
                        <button class="pattern-btn" data-pattern="frame_pacing">Frame Pacing</button>
                        <button class="pattern-btn" data-pattern="eye_separation">Eye Separation</button>
                    </div>
                </div>
                
                <div>
                    <h2>Settings</h2>
                    <div class="settings">
                        <div class="setting-item">
                            <label>Playback Speed</label>
                            <select id="speedSelect">
                                <option value="0.5">0.5x</option>
                                <option value="1.0" selected>1.0x</option>
                                <option value="2.0">2.0x</option>
                            </select>
                        </div>
                        
                        <div class="setting-item">
                            <label>Show Frame Info</label>
                            <input type="checkbox" id="showFrameInfo" checked>
                        </div>
                        
                        <div class="setting-item">
                            <label>Show Cadence Indicator</label>
                            <input type="checkbox" id="showCadence" checked>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h2>Statistics</h2>
                    <div class="stats">
                        <h3>Display Stats</h3>
                        <div class="stat-item">
                            <span class="stat-label">Frame Rate:</span>
                            <span class="stat-value" id="fpsValue">120 FPS</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Current Frame:</span>
                            <span class="stat-value" id="frameValue">0</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Current Eye:</span>
                            <span class="stat-value" id="eyeValue">Left</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Playback Speed:</span>
                            <span class="stat-value" id="speedValue">1.0x</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>MAGI Viewer - High-Frame-Rate 3D Cinema Display System</p>
        </div>
        
        <script>
            // WebSocket connection
            const ws = new WebSocket('ws://localhost:8000/viewer/ws');
            
            // Canvas setup
            const canvas = document.getElementById('videoCanvas');
            const ctx = canvas.getContext('2d');
            
            // UI elements
            const frameInfo = document.getElementById('frameInfo');
            const cadenceIndicator = document.getElementById('cadenceIndicator');
            const playBtn = document.getElementById('playBtn');
            const pauseBtn = document.getElementById('pauseBtn');
            const stopBtn = document.getElementById('stopBtn');
            const loadBtn = document.getElementById('loadBtn');
            const videoInput = document.getElementById('videoInput');
            const speedSelect = document.getElementById('speedSelect');
            const showFrameInfo = document.getElementById('showFrameInfo');
            const showCadence = document.getElementById('showCadence');
            
            // Stats elements
            const fpsValue = document.getElementById('fpsValue');
            const frameValue = document.getElementById('frameValue');
            const eyeValue = document.getElementById('eyeValue');
            const speedValue = document.getElementById('speedValue');
            
            // State
            let currentFrame = 0;
            let currentEye = 'left';
            let isPlaying = false;
            let playbackSpeed = 1.0;
            
            // WebSocket message handling
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'frame') {
                    // Display frame
                    const img = new Image();
                    img.onload = () => {
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    };
                    img.src = 'data:image/jpeg;base64,' + data.data;
                    
                    // Update frame info
                    currentFrame = data.info.frame;
                    currentEye = data.info.eye;
                    updateFrameInfo();
                } else if (data.type === 'test_pattern') {
                    // Display test pattern
                    const img = new Image();
                    img.onload = () => {
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    };
                    img.src = 'data:image/jpeg;base64,' + data.data;
                } else if (data.type === 'frame_info') {
                    // Update frame info
                    currentFrame = data.info.current_frame;
                    isPlaying = data.info.is_playing;
                    playbackSpeed = data.info.playback_speed;
                    updateStats();
                }
            };
            
            // Control button handlers
            playBtn.addEventListener('click', () => {
                ws.send(JSON.stringify({ type: 'play' }));
            });
            
            pauseBtn.addEventListener('click', () => {
                ws.send(JSON.stringify({ type: 'pause' }));
            });
            
            stopBtn.addEventListener('click', () => {
                ws.send(JSON.stringify({ type: 'stop' }));
            });
            
            loadBtn.addEventListener('click', () => {
                videoInput.click();
            });
            
            videoInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    ws.send(JSON.stringify({ type: 'load', video_path: file.name }));
                }
            });
            
            speedSelect.addEventListener('change', (e) => {
                const speed = parseFloat(e.target.value);
                ws.send(JSON.stringify({ type: 'speed', speed: speed }));
            });
            
            // Test pattern buttons
            document.querySelectorAll('.pattern-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const pattern = btn.dataset.pattern;
                    ws.send(JSON.stringify({ type: 'test_pattern', pattern: pattern }));
                });
            });
            
            // Display settings
            showFrameInfo.addEventListener('change', (e) => {
                frameInfo.style.display = e.target.checked ? 'block' : 'none';
            });
            
            showCadence.addEventListener('change', (e) => {
                cadenceIndicator.style.display = e.target.checked ? 'block' : 'none';
            });
            
            // Update functions
            function updateFrameInfo() {
                frameInfo.textContent = `Frame: ${currentFrame} | FPS: 120 | Eye: ${currentEye}`;
                cadenceIndicator.textContent = currentEye === 'left' ? 'L' : 'R';
                cadenceIndicator.className = `cadence-indicator ${currentEye}`;
            }
            
            function updateStats() {
                fpsValue.textContent = '120 FPS';
                frameValue.textContent = currentFrame;
                eyeValue.textContent = currentEye.charAt(0).toUpperCase() + currentEye.slice(1);
                speedValue.textContent = playbackSpeed.toFixed(1) + 'x';
            }
            
            // Initialize canvas size
            function resizeCanvas() {
                const container = canvas.parentElement;
                canvas.width = container.clientWidth;
                canvas.height = container.clientHeight;
            }
            
            window.addEventListener('resize', resizeCanvas);
            resizeCanvas();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)