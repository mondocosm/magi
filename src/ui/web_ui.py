"""
Web-based user interface for MAGI Pipeline
"""

import asyncio
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path
import shutil
import uuid

from ..core.config import Config
from ..pipeline.controller import MAGIPipeline
from .magi_viewer import viewer_router


# Get the static files directory
static_dir = Path(__file__).parent / "static"


class ProcessRequest(BaseModel):
    """Request model for video processing"""
    input_path: str
    output_path: str
    mode: str = "3d-projector"
    realtime: bool = False


class WebUI:
    """Web-based user interface for MAGI Pipeline"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize web UI
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.app = FastAPI(title="MAGI Pipeline", version="0.1.0")
        
        # Active pipelines
        self.active_pipelines: Dict[str, MAGIPipeline] = {}
        self.pipeline_status: Dict[str, Dict[str, Any]] = {}
        
        # Game capture
        self.game_pipeline = None
        self.game_capture_active = False
        
        # Camera capture
        self.camera_pipeline = None
        self.camera_capture_active = False
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Create directories
        self._create_directories()
    
    def _setup_middleware(self):
        """Setup middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        # Mount static files
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Include viewer router
        self.app.include_router(viewer_router)
        
        @self.app.get("/")
        async def root():
            """Root endpoint - serve the web interface"""
            if static_dir.exists():
                index_file = static_dir / "index.html"
                if index_file.exists():
                    return FileResponse(str(index_file))
            return {
                "name": "MAGI Pipeline",
                "version": "0.1.0",
                "status": "running",
                "message": "Web interface available at /static/index.html"
            }
        
        @self.app.get("/styles.css")
        async def get_styles():
            """Serve CSS file"""
            css_file = static_dir / "styles.css"
            if css_file.exists():
                return FileResponse(str(css_file), media_type="text/css")
            return {"error": "CSS file not found"}
        
        @self.app.get("/app.js")
        async def get_app_js():
            """Serve JavaScript file"""
            js_file = static_dir / "app.js"
            if js_file.exists():
                return FileResponse(str(js_file), media_type="application/javascript")
            return {"error": "JavaScript file not found"}
        
        @self.app.get("/magi-text.png")
        async def get_logo():
            """Serve MAGI logo"""
            logo_file = static_dir / "magi-text.png"
            if logo_file.exists():
                return FileResponse(str(logo_file), media_type="image/png")
            return {"error": "Logo file not found"}
        
        @self.app.get("/about.html")
        async def get_about():
            """Serve about page"""
            about_file = static_dir / "about.html"
            if about_file.exists():
                return FileResponse(str(about_file), media_type="text/html")
            return {"error": "About page not found"}
        
        @self.app.get("/api/config")
        async def get_config():
            """Get current configuration"""
            return {
                "processing": {
                    "target_resolution": self.config.processing.target_resolution,
                    "target_frame_rate": self.config.processing.target_frame_rate,
                    "interpolation_enabled": self.config.processing.interpolation_enabled,
                    "upscaling_enabled": self.config.processing.upscaling_enabled,
                },
                "output": {
                    "container": self.config.output.container,
                    "video_codec": self.config.output.video_codec,
                }
            }
        
        @self.app.post("/api/upload")
        async def upload_video(file: UploadFile = File(...)):
            """Upload video file"""
            try:
                # Generate unique filename
                file_id = str(uuid.uuid4())
                file_extension = Path(file.filename).suffix
                upload_path = Path("uploads") / f"{file_id}{file_extension}"
                
                # Save uploaded file
                upload_path.parent.mkdir(parents=True, exist_ok=True)
                with open(upload_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                return {
                    "file_id": file_id,
                    "filename": file.filename,
                    "path": str(upload_path),
                    "size": upload_path.stat().st_size
                }
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/analyze")
        async def analyze_video(request: ProcessRequest):
            """Analyze video file"""
            try:
                from ..input import VideoInput
                
                video_input = VideoInput()
                if not video_input.load(request.input_path):
                    raise HTTPException(status_code=400, detail="Could not load video")
                
                video_info = video_input.get_video_info()
                requirements = video_input.get_processing_requirements(
                    self.config.processing.target_frame_rate,
                    self.config.processing.target_resolution
                )
                
                video_input.close()
                
                return {
                    "video_info": video_info,
                    "requirements": requirements
                }
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/process")
        async def process_video(request: ProcessRequest, background_tasks: BackgroundTasks):
            """Process video to MAGI format"""
            try:
                # Generate job ID
                job_id = str(uuid.uuid4())
                
                # Create pipeline
                pipeline = MAGIPipeline(self.config)
                
                # Load input
                if not pipeline.load_input(request.input_path):
                    raise HTTPException(status_code=400, detail="Could not load input video")
                
                # Store pipeline
                self.active_pipelines[job_id] = pipeline
                self.pipeline_status[job_id] = {
                    "status": "processing",
                    "progress": 0,
                    "message": "Starting processing"
                }
                
                # Start processing in background
                background_tasks.add_task(
                    self._process_video_background,
                    job_id,
                    pipeline,
                    request.output_path,
                    request.realtime
                )
                
                return {
                    "job_id": job_id,
                    "status": "started"
                }
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/status/{job_id}")
        async def get_status(job_id: str):
            """Get processing status"""
            if job_id not in self.pipeline_status:
                raise HTTPException(status_code=404, detail="Job not found")
            
            return self.pipeline_status[job_id]
        
        @self.app.get("/api/jobs")
        async def list_jobs():
            """List all jobs"""
            return {
                "jobs": [
                    {
                        "job_id": job_id,
                        "status": status["status"],
                        "progress": status["progress"]
                    }
                    for job_id, status in self.pipeline_status.items()
                ]
            }
        
        @self.app.delete("/api/jobs/{job_id}")
        async def cancel_job(job_id: str):
            """Cancel processing job"""
            if job_id not in self.active_pipelines:
                raise HTTPException(status_code=404, detail="Job not found")
            
            pipeline = self.active_pipelines[job_id]
            pipeline.cancel()
            
            self.pipeline_status[job_id]["status"] = "cancelled"
            
            return {"status": "cancelled"}
        
        @self.app.get("/api/download/{job_id}")
        async def download_output(job_id: str):
            """Download processed video"""
            if job_id not in self.pipeline_status:
                raise HTTPException(status_code=404, detail="Job not found")
            
            status = self.pipeline_status[job_id]
            if status["status"] != "completed":
                raise HTTPException(status_code=400, detail="Processing not complete")
            
            output_path = status.get("output_path")
            if not output_path or not Path(output_path).exists():
                raise HTTPException(status_code=404, detail="Output file not found")
            
            return FileResponse(
                output_path,
                media_type="video/mp4",
                filename=Path(output_path).name
            )
        
        @self.app.get("/api/windows")
        async def list_windows():
            """List available windows for capture"""
            try:
                from ..input.game_capture import create_game_capture
                
                capture = create_game_capture(method="window_capture")
                windows = capture.list_windows()
                
                return {"windows": windows}
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/game/start")
        async def start_game_capture(request: dict):
            """Start game capture and MAGI conversion"""
            try:
                from ..input.game_capture import create_game_capture, CaptureMethod
                from ..pipeline.game_to_magi import create_game_to_magi_pipeline, PipelineMode
                
                capture_method_str = request.get("capture_method", "screen_capture")
                window_id = request.get("window_id")
                pipeline_mode_str = request.get("pipeline_mode", "balanced")
                
                # Create game capture
                try:
                    capture_method = CaptureMethod(capture_method_str)
                except ValueError:
                    capture_method = CaptureMethod.SCREEN_CAPTURE
                
                try:
                    pipeline_mode = PipelineMode(pipeline_mode_str)
                except ValueError:
                    pipeline_mode = PipelineMode.BALANCED
                
                # Create game-to-MAGI pipeline
                self.game_pipeline = create_game_to_magi_pipeline(
                    config=self.config,
                    capture_method=capture_method_str,
                    mode=pipeline_mode_str
                )
                
                # Set window if specified
                if window_id and capture_method == CaptureMethod.WINDOW_CAPTURE:
                    self.game_pipeline.game_capture.set_window(window_id)
                
                # Start pipeline
                if self.game_pipeline.start():
                    self.game_capture_active = True
                    return {"status": "started", "mode": pipeline_mode_str}
                else:
                    raise HTTPException(status_code=500, detail="Failed to start game capture")
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/game/stop")
        async def stop_game_capture():
            """Stop game capture"""
            try:
                if self.game_pipeline and self.game_capture_active:
                    self.game_pipeline.stop()
                    self.game_capture_active = False
                    return {"status": "stopped"}
                else:
                    raise HTTPException(status_code=400, detail="Game capture not active")
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/game/stats")
        async def get_game_stats():
            """Get game capture statistics"""
            try:
                if not self.game_pipeline or not self.game_capture_active:
                    raise HTTPException(status_code=400, detail="Game capture not active")
                
                stats = self.game_pipeline.get_stats()
                
                return {
                    "fps": stats.avg_fps,
                    "latency": stats.avg_latency_ms,
                    "frames_processed": stats.frames_processed,
                    "frames_output": stats.frames_output,
                    "frames_dropped": 0,  # Would need to track this
                    "capture_latency": stats.capture_latency_ms,
                    "conversion_3d_time": stats.conversion_3d_time_ms,
                    "interpolation_time": stats.interpolation_time_ms,
                    "upscaling_time": stats.upscaling_time_ms,
                    "cadence_time": stats.cadence_time_ms
                }
            
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/cameras")
        async def list_cameras():
            """List available cameras"""
            try:
                from ..input.camera_detector import CameraDetector
                
                detector = CameraDetector()
                cameras = detector.detect_all()
                
                return {
                    "cameras": [
                        {
                            "camera_id": cam.camera_id,
                            "camera_type": cam.camera_type.value,
                            "name": cam.name,
                            "width": cam.width,
                            "height": cam.height,
                            "fps": cam.fps,
                            "format": cam.format.value,
                            "backend": cam.backend.value,
                            "is_stereo": cam.is_stereo,
                            "has_depth": cam.has_depth,
                            "is_available": cam.is_available
                        }
                        for cam in cameras
                    ]
                }
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/camera/start")
        async def start_camera_capture(request: dict):
            """Start camera capture and MAGI conversion"""
            try:
                from ..input.camera_capture import CameraCapture, CameraType, CameraFormat
                from ..pipeline.camera_to_magi import CameraToMAGIPipeline, ProcessingMode, OutputMode
                
                camera_id = request.get("camera_id", 0)
                camera_type_str = request.get("camera_type", "generic_mono")
                width = request.get("width", 1920)
                height = request.get("height", 1080)
                fps = request.get("fps", 30.0)
                format_str = request.get("format", "mono")
                backend = request.get("backend", "opencv")
                processing_mode_str = request.get("processing_mode", "balanced")
                output_mode_str = request.get("output_mode", "both")
                output_path = request.get("output_path")
                
                # Parse camera type
                try:
                    camera_type = CameraType(camera_type_str)
                except ValueError:
                    camera_type = CameraType.GENERIC_MONO
                
                # Parse camera format
                try:
                    camera_format = CameraFormat(format_str)
                except ValueError:
                    camera_format = CameraFormat.MONO
                
                # Parse processing mode
                try:
                    processing_mode = ProcessingMode(processing_mode_str)
                except ValueError:
                    processing_mode = ProcessingMode.BALANCED
                
                # Parse output mode
                try:
                    output_mode = OutputMode(output_mode_str)
                except ValueError:
                    output_mode = OutputMode.BOTH
                
                # Create camera capture
                camera_capture = CameraCapture(
                    camera_id=camera_id,
                    camera_type=camera_type,
                    width=width,
                    height=height,
                    fps=fps,
                    format=camera_format,
                    backend=backend
                )
                
                # Create camera-to-MAGI pipeline
                self.camera_pipeline = CameraToMAGIPipeline(
                    camera_capture=camera_capture,
                    output_path=output_path,
                    config=self.config,
                    mode=processing_mode,
                    output_mode=output_mode
                )
                
                # Start pipeline
                if self.camera_pipeline.start():
                    self.camera_capture_active = True
                    return {
                        "status": "started",
                        "processing_mode": processing_mode_str,
                        "output_mode": output_mode_str,
                        "camera_type": camera_type_str
                    }
                else:
                    raise HTTPException(status_code=500, detail="Failed to start camera capture")
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/camera/stop")
        async def stop_camera_capture():
            """Stop camera capture"""
            try:
                if self.camera_pipeline and self.camera_capture_active:
                    self.camera_pipeline.stop()
                    self.camera_capture_active = False
                    return {"status": "stopped"}
                else:
                    raise HTTPException(status_code=400, detail="Camera capture not active")
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/camera/stats")
        async def get_camera_stats():
            """Get camera capture statistics"""
            try:
                if not self.camera_pipeline or not self.camera_capture_active:
                    raise HTTPException(status_code=400, detail="Camera capture not active")
                
                stats = self.camera_pipeline.get_stats()
                
                return {
                    "fps": stats["fps"],
                    "frames_processed": stats["frames_processed"],
                    "frames_dropped": stats["frames_dropped"],
                    "avg_latency": stats["avg_latency"],
                    "current_latency": stats["current_latency"],
                    "processing_times": stats["processing_times"],
                    "mode": stats["mode"],
                    "camera_type": stats["camera_type"],
                    "camera_fps": stats["camera_fps"]
                }
            
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _process_video_background(self, job_id: str, pipeline: MAGIPipeline, 
                                       output_path: str, realtime: bool):
        """Process video in background"""
        try:
            def progress_callback(progress, message):
                self.pipeline_status[job_id]["progress"] = progress
                self.pipeline_status[job_id]["message"] = message
            
            if realtime:
                success = pipeline.process_realtime(output_path)
            else:
                success = pipeline.process(output_path, progress_callback)
            
            if success:
                self.pipeline_status[job_id]["status"] = "completed"
                self.pipeline_status[job_id]["progress"] = 100
                self.pipeline_status[job_id]["message"] = "Processing complete"
                self.pipeline_status[job_id]["output_path"] = output_path
            else:
                self.pipeline_status[job_id]["status"] = "failed"
                self.pipeline_status[job_id]["message"] = "Processing failed"
        
        except Exception as e:
            self.pipeline_status[job_id]["status"] = "failed"
            self.pipeline_status[job_id]["message"] = str(e)
        
        finally:
            # Clean up pipeline
            if job_id in self.active_pipelines:
                del self.active_pipelines[job_id]
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = ["uploads", "output", "temp", "logs"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run web UI
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        uvicorn.run(self.app, host=host, port=port)


def create_web_ui(config: Optional[Config] = None) -> WebUI:
    """
    Create web UI instance
    
    Args:
        config: Configuration object
        
    Returns:
        WebUI instance
    """
    return WebUI(config)


if __name__ == "__main__":
    web_ui = create_web_ui()
    web_ui.run()