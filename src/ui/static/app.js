// MAGI Pipeline Web Interface

class MAGIPipelineUI {
    constructor() {
        this.currentFile = null;
        this.currentJobId = null;
        this.progressInterval = null;
        this.gameStatsInterval = null;
        this.cameraStatsInterval = null;
        this.currentMode = 'video';
        this.gameCaptureActive = false;
        this.cameraCaptureActive = false;
        this.availableCameras = [];
        
        this.initializeElements();
        this.attachEventListeners();
    }
    
    initializeElements() {
        // Mode selection elements
        this.videoModeBtn = document.getElementById('videoModeBtn');
        this.gameModeBtn = document.getElementById('gameModeBtn');
        this.cameraModeBtn = document.getElementById('cameraModeBtn');
        this.videoSection = document.getElementById('videoSection');
        this.gameSection = document.getElementById('gameSection');
        this.cameraSection = document.getElementById('cameraSection');
        
        // Upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.videoInput = document.getElementById('videoInput');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        
        // Game capture elements
        this.captureMethod = document.getElementById('captureMethod');
        this.windowSelectGroup = document.getElementById('windowSelectGroup');
        this.windowSelect = document.getElementById('windowSelect');
        this.refreshWindowsBtn = document.getElementById('refreshWindowsBtn');
        this.pipelineMode = document.getElementById('pipelineMode');
        this.startCaptureBtn = document.getElementById('startCaptureBtn');
        this.stopCaptureBtn = document.getElementById('stopCaptureBtn');
        this.gameStats = document.getElementById('gameStats');
        
        // Game statistics elements
        this.gameFps = document.getElementById('gameFps');
        this.gameLatency = document.getElementById('gameLatency');
        this.gameFrames = document.getElementById('gameFrames');
        this.gameDropped = document.getElementById('gameDropped');
        this.captureTime = document.getElementById('captureTime');
        this.conversionTime = document.getElementById('conversionTime');
        this.interpolationTime = document.getElementById('interpolationTime');
        this.upscalingTime = document.getElementById('upscalingTime');
        this.cadenceTime = document.getElementById('cadenceTime');
        
        // Camera elements
        this.cameraSelect = document.getElementById('cameraSelect');
        this.refreshCamerasBtn = document.getElementById('refreshCamerasBtn');
        this.cameraProcessingMode = document.getElementById('cameraProcessingMode');
        this.cameraOutputMode = document.getElementById('cameraOutputMode');
        this.cameraOutputPathGroup = document.getElementById('cameraOutputPathGroup');
        this.cameraOutputPath = document.getElementById('cameraOutputPath');
        this.startCameraBtn = document.getElementById('startCameraBtn');
        this.stopCameraBtn = document.getElementById('stopCameraBtn');
        this.cameraStats = document.getElementById('cameraStats');
        
        // Camera statistics elements
        this.cameraFps = document.getElementById('cameraFps');
        this.cameraLatency = document.getElementById('cameraLatency');
        this.cameraFrames = document.getElementById('cameraFrames');
        this.cameraDropped = document.getElementById('cameraDropped');
        this.stereoExtractionTime = document.getElementById('stereoExtractionTime');
        this.cameraInterpolationTime = document.getElementById('cameraInterpolationTime');
        this.cameraUpscalingTime = document.getElementById('cameraUpscalingTime');
        this.cameraCadenceTime = document.getElementById('cameraCadenceTime');
        this.cameraEncodingTime = document.getElementById('cameraEncodingTime');
        
        // Configuration elements
        this.outputMode = document.getElementById('outputMode');
        this.targetResolution = document.getElementById('targetResolution');
        this.targetFrameRate = document.getElementById('targetFrameRate');
        this.enableInterpolation = document.getElementById('enableInterpolation');
        this.enableUpscaling = document.getElementById('enableUpscaling');
        this.enableStereoCrafter = document.getElementById('enableStereoCrafter');
        this.interpolationMethod = document.getElementById('interpolationMethod');
        this.upscalingMethod = document.getElementById('upscalingMethod');
        
        // Action elements
        this.processBtn = document.getElementById('processBtn');
        this.btnText = this.processBtn.querySelector('.btn-text');
        this.btnLoader = this.processBtn.querySelector('.btn-loader');
        
        // Progress elements
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressPercent = document.getElementById('progressPercent');
        this.progressStatus = document.getElementById('progressStatus');
        this.detailInput = document.getElementById('detailInput');
        this.detailOutput = document.getElementById('detailOutput');
        this.detailMode = document.getElementById('detailMode');
        this.currentStep = document.getElementById('currentStep');
        
        // Pipeline step elements
        this.stepInput = document.getElementById('step-input');
        this.stepAnalyze = document.getElementById('step-analyze');
        this.step3d = document.getElementById('step-3d');
        this.stepInterpolate = document.getElementById('step-interpolate');
        this.stepUpscale = document.getElementById('step-upscale');
        this.stepCadence = document.getElementById('step-cadence');
        this.stepEncode = document.getElementById('step-encode');
        this.stepOutput = document.getElementById('step-output');
        
        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.resultResolution = document.getElementById('resultResolution');
        this.resultFrameRate = document.getElementById('resultFrameRate');
        this.resultTime = document.getElementById('resultTime');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.resetBtn = document.getElementById('resetBtn');
    }
    
    attachEventListeners() {
        // Mode selection
        this.videoModeBtn.addEventListener('click', () => this.switchMode('video'));
        this.gameModeBtn.addEventListener('click', () => this.switchMode('game'));
        this.cameraModeBtn.addEventListener('click', () => this.switchMode('camera'));
        
        // Upload events
        this.uploadArea.addEventListener('click', () => this.videoInput.click());
        this.videoInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Game capture events
        this.captureMethod.addEventListener('change', () => this.handleCaptureMethodChange());
        this.refreshWindowsBtn.addEventListener('click', () => this.refreshWindows());
        this.startCaptureBtn.addEventListener('click', () => this.startGameCapture());
        this.stopCaptureBtn.addEventListener('click', () => this.stopGameCapture());
        
        // Camera events
        this.refreshCamerasBtn.addEventListener('click', () => this.refreshCameras());
        this.cameraOutputMode.addEventListener('change', () => this.handleCameraOutputModeChange());
        this.startCameraBtn.addEventListener('click', () => this.startCameraCapture());
        this.stopCameraBtn.addEventListener('click', () => this.stopCameraCapture());
        
        // Process button
        this.processBtn.addEventListener('click', () => this.startProcessing());
        
        // Download and reset buttons
        this.downloadBtn.addEventListener('click', () => this.downloadVideo());
        this.resetBtn.addEventListener('click', () => this.resetUI());
    }
    
    switchMode(mode) {
        this.currentMode = mode;
        
        // Update mode buttons
        this.videoModeBtn.classList.toggle('active', mode === 'video');
        this.gameModeBtn.classList.toggle('active', mode === 'game');
        this.cameraModeBtn.classList.toggle('active', mode === 'camera');
        
        // Show/hide sections
        this.videoSection.style.display = mode === 'video' ? 'block' : 'none';
        this.gameSection.style.display = mode === 'game' ? 'block' : 'none';
        this.cameraSection.style.display = mode === 'camera' ? 'block' : 'none';
        
        // Update process button text
        if (mode === 'video') {
            this.btnText.textContent = 'Process Video';
        } else if (mode === 'game') {
            this.btnText.textContent = 'Start Processing';
        } else if (mode === 'camera') {
            this.btnText.textContent = 'Start Processing';
            // Load cameras when switching to camera mode
            this.refreshCameras();
        }
    }
    
    handleCaptureMethodChange() {
        const method = this.captureMethod.value;
        
        // Show/hide window selection based on method
        if (method === 'window_capture') {
            this.windowSelectGroup.style.display = 'block';
            this.refreshWindows();
        } else {
            this.windowSelectGroup.style.display = 'none';
        }
    }
    
    async refreshWindows() {
        try {
            const response = await fetch('/api/windows');
            
            if (!response.ok) {
                throw new Error('Failed to get windows');
            }
            
            const windows = await response.json();
            
            // Update window select
            this.windowSelect.innerHTML = '<option value="">Select a window...</option>';
            windows.forEach(window => {
                const option = document.createElement('option');
                option.value = window.id;
                option.textContent = window.title;
                this.windowSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error refreshing windows:', error);
            alert('Failed to get window list');
        }
    }
    
    async startGameCapture() {
        try {
            const response = await fetch('/api/game/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    capture_method: this.captureMethod.value,
                    window_id: this.windowSelect.value,
                    pipeline_mode: this.pipelineMode.value
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to start game capture');
            }
            
            const result = await response.json();
            
            // Update UI
            this.gameCaptureActive = true;
            this.startCaptureBtn.disabled = true;
            this.stopCaptureBtn.disabled = false;
            this.gameStats.style.display = 'block';
            
            // Start statistics monitoring
            this.monitorGameStats();
            
        } catch (error) {
            console.error('Error starting game capture:', error);
            alert('Failed to start game capture: ' + error.message);
        }
    }
    
    async stopGameCapture() {
        try {
            const response = await fetch('/api/game/stop', {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Failed to stop game capture');
            }
            
            // Update UI
            this.gameCaptureActive = false;
            this.startCaptureBtn.disabled = false;
            this.stopCaptureBtn.disabled = true;
            
            // Stop statistics monitoring
            if (this.gameStatsInterval) {
                clearInterval(this.gameStatsInterval);
                this.gameStatsInterval = null;
            }
            
        } catch (error) {
            console.error('Error stopping game capture:', error);
            alert('Failed to stop game capture: ' + error.message);
        }
    }
    
    monitorGameStats() {
        this.gameStatsInterval = setInterval(async () => {
            if (!this.gameCaptureActive) return;
            
            try {
                const response = await fetch('/api/game/stats');
                
                if (!response.ok) {
                    throw new Error('Failed to get game stats');
                }
                
                const stats = await response.json();
                
                // Update statistics display
                this.gameFps.textContent = stats.fps.toFixed(1);
                this.gameLatency.textContent = stats.latency.toFixed(1) + 'ms';
                this.gameFrames.textContent = stats.frames_processed;
                this.gameDropped.textContent = stats.frames_dropped;
                this.captureTime.textContent = stats.capture_latency.toFixed(1) + 'ms';
                this.conversionTime.textContent = stats.conversion_3d_time.toFixed(1) + 'ms';
                this.interpolationTime.textContent = stats.interpolation_time.toFixed(1) + 'ms';
                this.upscalingTime.textContent = stats.upscaling_time.toFixed(1) + 'ms';
                this.cadenceTime.textContent = stats.cadence_time.toFixed(1) + 'ms';
                
            } catch (error) {
                console.error('Error getting game stats:', error);
            }
        }, 1000);
    }
    
    handleCameraOutputModeChange() {
        const mode = this.cameraOutputMode.value;
        
        // Show/hide output path based on mode
        if (mode === 'file_only' || mode === 'both') {
            this.cameraOutputPathGroup.style.display = 'block';
        } else {
            this.cameraOutputPathGroup.style.display = 'none';
        }
    }
    
    async refreshCameras() {
        try {
            const response = await fetch('/api/cameras');
            
            if (!response.ok) {
                throw new Error('Failed to get cameras');
            }
            
            const data = await response.json();
            this.availableCameras = data.cameras;
            
            // Update camera select
            this.cameraSelect.innerHTML = '<option value="">Select a camera...</option>';
            this.availableCameras.forEach(camera => {
                const option = document.createElement('option');
                option.value = camera.camera_id;
                option.textContent = `${camera.name} (${camera.width}x${camera.height} @ ${camera.fps}fps)`;
                option.dataset.cameraType = camera.camera_type;
                option.dataset.cameraFormat = camera.format;
                option.dataset.cameraBackend = camera.backend;
                option.dataset.isStereo = camera.is_stereo;
                option.dataset.hasDepth = camera.has_depth;
                this.cameraSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error refreshing cameras:', error);
            alert('Failed to get camera list');
        }
    }
    
    async startCameraCapture() {
        try {
            const selectedCamera = this.cameraSelect.value;
            if (!selectedCamera) {
                alert('Please select a camera first');
                return;
            }
            
            const selectedOption = this.cameraSelect.options[this.cameraSelect.selectedIndex];
            
            const response = await fetch('/api/camera/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    camera_id: parseInt(selectedCamera),
                    camera_type: selectedOption.dataset.cameraType,
                    width: parseInt(selectedOption.dataset.width) || 1920,
                    height: parseInt(selectedOption.dataset.height) || 1080,
                    fps: parseFloat(selectedOption.dataset.fps) || 30.0,
                    format: selectedOption.dataset.cameraFormat,
                    backend: selectedOption.dataset.cameraBackend,
                    processing_mode: this.cameraProcessingMode.value,
                    output_mode: this.cameraOutputMode.value,
                    output_path: this.cameraOutputPath.value
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to start camera capture');
            }
            
            const result = await response.json();
            
            // Update UI
            this.cameraCaptureActive = true;
            this.startCameraBtn.disabled = true;
            this.stopCameraBtn.disabled = false;
            this.cameraStats.style.display = 'block';
            
            // Start statistics monitoring
            this.monitorCameraStats();
            
        } catch (error) {
            console.error('Error starting camera capture:', error);
            alert('Failed to start camera capture: ' + error.message);
        }
    }
    
    async stopCameraCapture() {
        try {
            const response = await fetch('/api/camera/stop', {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Failed to stop camera capture');
            }
            
            // Update UI
            this.cameraCaptureActive = false;
            this.startCameraBtn.disabled = false;
            this.stopCameraBtn.disabled = true;
            
            // Stop statistics monitoring
            if (this.cameraStatsInterval) {
                clearInterval(this.cameraStatsInterval);
                this.cameraStatsInterval = null;
            }
            
        } catch (error) {
            console.error('Error stopping camera capture:', error);
            alert('Failed to stop camera capture: ' + error.message);
        }
    }
    
    monitorCameraStats() {
        this.cameraStatsInterval = setInterval(async () => {
            if (!this.cameraCaptureActive) return;
            
            try {
                const response = await fetch('/api/camera/stats');
                
                if (!response.ok) {
                    throw new Error('Failed to get camera stats');
                }
                
                const stats = await response.json();
                
                // Update statistics display
                this.cameraFps.textContent = stats.fps.toFixed(1);
                this.cameraLatency.textContent = stats.avg_latency.toFixed(1) + 'ms';
                this.cameraFrames.textContent = stats.frames_processed;
                this.cameraDropped.textContent = stats.frames_dropped;
                
                // Update processing times
                if (stats.processing_times) {
                    this.stereoExtractionTime.textContent =
                        (stats.processing_times.stereo_extraction || 0).toFixed(1) + 'ms';
                    this.cameraInterpolationTime.textContent =
                        (stats.processing_times.interpolation || 0).toFixed(1) + 'ms';
                    this.cameraUpscalingTime.textContent =
                        (stats.processing_times.upscaling || 0).toFixed(1) + 'ms';
                    this.cameraCadenceTime.textContent =
                        (stats.processing_times.cadence || 0).toFixed(1) + 'ms';
                    this.cameraEncodingTime.textContent =
                        (stats.processing_times.encoding || 0).toFixed(1) + 'ms';
                }
                
            } catch (error) {
                console.error('Error getting camera stats:', error);
            }
        }, 1000);
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFile(file) {
        if (!file.type.startsWith('video/')) {
            alert('Please select a video file');
            return;
        }
        
        this.currentFile = file;
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.fileInfo.style.display = 'flex';
        this.processBtn.disabled = false;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    async startProcessing() {
        if (!this.currentFile) {
            alert('Please select a video file first');
            return;
        }
        
        try {
            // Update UI
            this.processBtn.disabled = true;
            this.btnText.style.display = 'none';
            this.btnLoader.style.display = 'block';
            
            // Upload file
            const uploadResult = await this.uploadFile(this.currentFile);
            
            // Get video info
            const videoInfo = await this.analyzeVideo(uploadResult.path);
            
            // Start processing
            const processResult = await this.processVideo(uploadResult.path, uploadResult.filename);
            
            // Start progress monitoring
            this.currentJobId = processResult.job_id;
            this.monitorProgress();
            
        } catch (error) {
            console.error('Error starting processing:', error);
            alert('Error starting processing: ' + error.message);
            this.resetProcessButton();
        }
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to upload file');
        }
        
        return await response.json();
    }
    
    async analyzeVideo(filePath) {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                input_path: filePath,
                output_path: '',
                mode: this.outputMode.value
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze video');
        }
        
        return await response.json();
    }
    
    async processVideo(inputPath, filename) {
        const outputPath = `output/${filename.replace(/\.[^/.]+$/, '')}_magi.mp4`;
        
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                input_path: inputPath,
                output_path: outputPath,
                mode: this.outputMode.value,
                realtime: false
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to start processing');
        }
        
        return await response.json();
    }
    
    monitorProgress() {
        // Show progress section
        this.progressSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        
        // Reset pipeline steps
        this.resetPipelineSteps();
        
        // Update details
        this.detailInput.textContent = this.currentFile.name;
        this.detailOutput.textContent = 'Processing...';
        this.detailMode.textContent = this.outputMode.value;
        
        // Start polling
        this.progressInterval = setInterval(() => this.checkProgress(), 1000);
    }
    
    resetPipelineSteps() {
        // Reset all pipeline steps to pending
        const steps = [
            this.stepInput,
            this.stepAnalyze,
            this.step3d,
            this.stepInterpolate,
            this.stepUpscale,
            this.stepCadence,
            this.stepEncode,
            this.stepOutput
        ];
        
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
            step.querySelector('.step-status').textContent = 'Pending';
        });
    }
    
    updatePipelineStep(stepElement, status, message) {
        // Update step status
        stepElement.classList.remove('active', 'completed');
        stepElement.classList.add(status);
        stepElement.querySelector('.step-status').textContent = message;
        
        // Update current step display
        this.currentStep.textContent = stepElement.querySelector('.step-title').textContent;
    }
    
    async checkProgress() {
        if (!this.currentJobId) return;
        
        try {
            const response = await fetch(`/api/status/${this.currentJobId}`);
            
            if (!response.ok) {
                throw new Error('Failed to get status');
            }
            
            const status = await response.json();
            
            // Update progress
            this.progressFill.style.width = `${status.progress}%`;
            this.progressPercent.textContent = `${Math.round(status.progress)}%`;
            this.progressStatus.textContent = status.message;
            
            // Update pipeline steps based on progress
            this.updatePipelineSteps(status.progress, status.message);
            
            // Check if complete
            if (status.status === 'completed') {
                this.handleProcessingComplete(status);
            } else if (status.status === 'failed') {
                this.handleProcessingError(status.message);
            }
            
        } catch (error) {
            console.error('Error checking progress:', error);
        }
    }
    
    updatePipelineSteps(progress, message) {
        // Map progress to pipeline steps
        if (progress < 10) {
            this.updatePipelineStep(this.stepInput, 'active', 'Loading...');
        } else if (progress < 20) {
            this.updatePipelineStep(this.stepInput, 'completed', 'Complete');
            this.updatePipelineStep(this.stepAnalyze, 'active', 'Analyzing...');
        } else if (progress < 30) {
            this.updatePipelineStep(this.stepAnalyze, 'completed', 'Complete');
            this.updatePipelineStep(this.step3d, 'active', 'Converting...');
        } else if (progress < 50) {
            this.updatePipelineStep(this.step3d, 'completed', 'Complete');
            this.updatePipelineStep(this.stepInterpolate, 'active', 'Interpolating...');
        } else if (progress < 70) {
            this.updatePipelineStep(this.stepInterpolate, 'completed', 'Complete');
            this.updatePipelineStep(this.stepUpscale, 'active', 'Upscaling...');
        } else if (progress < 85) {
            this.updatePipelineStep(this.stepUpscale, 'completed', 'Complete');
            this.updatePipelineStep(this.stepCadence, 'active', 'Applying cadence...');
        } else if (progress < 95) {
            this.updatePipelineStep(this.stepCadence, 'completed', 'Complete');
            this.updatePipelineStep(this.stepEncode, 'active', 'Encoding...');
        } else if (progress < 100) {
            this.updatePipelineStep(this.stepEncode, 'completed', 'Complete');
            this.updatePipelineStep(this.stepOutput, 'active', 'Finalizing...');
        }
    }
    
    handleProcessingComplete(status) {
        clearInterval(this.progressInterval);
        
        // Mark all pipeline steps as completed
        const steps = [
            this.stepInput,
            this.stepAnalyze,
            this.step3d,
            this.stepInterpolate,
            this.stepUpscale,
            this.stepCadence,
            this.stepEncode,
            this.stepOutput
        ];
        
        steps.forEach(step => {
            step.classList.remove('active');
            step.classList.add('completed');
            step.querySelector('.step-status').textContent = 'Complete';
        });
        
        // Update UI
        this.progressSection.style.display = 'none';
        this.resultsSection.style.display = 'block';
        
        // Update results
        this.resultResolution.textContent = this.targetResolution.value;
        this.resultFrameRate.textContent = `${this.targetFrameRate.value} fps`;
        this.resultTime.textContent = 'Processing complete';
        
        // Store output path for download
        this.outputPath = status.output_path;
        
        this.resetProcessButton();
    }
    
    handleProcessingError(message) {
        clearInterval(this.progressInterval);
        
        alert('Processing failed: ' + message);
        this.resetProcessButton();
        this.resetUI();
    }
    
    async downloadVideo() {
        if (!this.currentJobId || !this.outputPath) {
            alert('No video available for download');
            return;
        }
        
        try {
            const response = await fetch(`/api/download/${this.currentJobId}`);
            
            if (!response.ok) {
                throw new Error('Failed to download video');
            }
            
            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.outputPath.split('/').pop();
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error downloading video:', error);
            alert('Error downloading video: ' + error.message);
        }
    }
    
    resetUI() {
        // Reset file
        this.currentFile = null;
        this.currentJobId = null;
        this.outputPath = null;
        
        // Reset upload UI
        this.fileInfo.style.display = 'none';
        this.processBtn.disabled = true;
        this.videoInput.value = '';
        
        // Reset progress
        this.progressSection.style.display = 'none';
        this.progressFill.style.width = '0%';
        this.progressPercent.textContent = '0%';
        this.progressStatus.textContent = 'Initializing...';
        
        // Reset results
        this.resultsSection.style.display = 'none';
        
        // Reset configuration
        this.outputMode.value = '3d-projector';
        this.targetResolution.value = '3840x2160';
        this.targetFrameRate.value = '120';
        this.enableInterpolation.checked = true;
        this.enableUpscaling.checked = true;
        this.enableStereoCrafter.checked = true;
        this.interpolationMethod.value = 'optical_flow';
        this.upscalingMethod.value = 'bicubic';
    }
    
    resetProcessButton() {
        this.processBtn.disabled = false;
        this.btnText.style.display = 'block';
        this.btnLoader.style.display = 'none';
    }
}

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MAGIPipelineUI();
});