"""
GPU detection and management for MAGI Pipeline
Supports NVIDIA (CUDA), AMD (ROCm), and Apple Silicon (Metal)
"""

import platform
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class GPUVendor(Enum):
    """GPU vendor types"""
    NVIDIA = "nvidia"
    AMD = "amd"
    APPLE = "apple"
    UNKNOWN = "unknown"


@dataclass
class GPUInfo:
    """GPU information"""
    vendor: GPUVendor
    name: str
    memory_mb: int
    compute_capability: Optional[str] = None
    available: bool = True
    device_index: int = 0


class GPUDetector:
    """Detect and manage available GPUs"""
    
    def __init__(self):
        self._detected_gpus: List[GPUInfo] = []
        self._system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return {
            "platform": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
    
    def detect_gpus(self) -> List[GPUInfo]:
        """
        Detect available GPUs on the system
        
        Returns:
            List of GPUInfo objects
        """
        self._detected_gpus = []
        
        # Try NVIDIA GPUs first
        nvidia_gpus = self._detect_nvidia_gpus()
        if nvidia_gpus:
            self._detected_gpus.extend(nvidia_gpus)
        
        # Try AMD GPUs
        amd_gpus = self._detect_amd_gpus()
        if amd_gpus:
            self._detected_gpus.extend(amd_gpus)
        
        # Try Apple Silicon GPUs
        apple_gpus = self._detect_apple_gpus()
        if apple_gpus:
            self._detected_gpus.extend(apple_gpus)
        
        return self._detected_gpus
    
    def _detect_nvidia_gpus(self) -> List[GPUInfo]:
        """Detect NVIDIA GPUs using nvidia-smi"""
        gpus = []
        
        try:
            # Try nvidia-smi command
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for idx, line in enumerate(lines):
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 2:
                            name = parts[0]
                            memory_str = parts[1]
                            
                            # Parse memory (e.g., "8192 MiB")
                            memory_mb = 0
                            if 'MiB' in memory_str:
                                memory_mb = int(memory_str.split()[0])
                            elif 'GiB' in memory_str:
                                memory_mb = int(float(memory_str.split()[0]) * 1024)
                            
                            # Get compute capability
                            compute_cap = self._get_nvidia_compute_capability(idx)
                            
                            gpu = GPUInfo(
                                vendor=GPUVendor.NVIDIA,
                                name=name,
                                memory_mb=memory_mb,
                                compute_capability=compute_cap,
                                device_index=idx
                            )
                            gpus.append(gpu)
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        return gpus
    
    def _get_nvidia_compute_capability(self, device_index: int) -> Optional[str]:
        """Get NVIDIA GPU compute capability"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader", "-i", str(device_index)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        return None
    
    def _detect_amd_gpus(self) -> List[GPUInfo]:
        """Detect AMD GPUs using rocm-smi"""
        gpus = []
        
        try:
            # Try rocm-smi command
            result = subprocess.run(
                ["rocm-smi", "--showmeminfo", "vram", "--showproductname"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse rocm-smi output
                lines = result.stdout.split('\n')
                gpu_name = None
                memory_mb = 0
                
                for line in lines:
                    if 'Card series' in line or 'Device Name' in line:
                        gpu_name = line.split(':')[-1].strip()
                    elif 'VRAM Total Memory' in line:
                        memory_str = line.split(':')[-1].strip()
                        # Parse memory (e.g., "8192 MB")
                        memory_mb = int(memory_str.split()[0])
                
                if gpu_name and memory_mb > 0:
                    gpu = GPUInfo(
                        vendor=GPUVendor.AMD,
                        name=gpu_name,
                        memory_mb=memory_mb,
                        device_index=0
                    )
                    gpus.append(gpu)
        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        return gpus
    
    def _detect_apple_gpus(self) -> List[GPUInfo]:
        """Detect Apple Silicon GPUs"""
        gpus = []
        
        # Check if running on Apple Silicon
        if self._system_info["platform"] == "Darwin" and "arm64" in self._system_info["machine"]:
            try:
                # Get GPU info from system_profiler
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    gpu_name = None
                    
                    for line in lines:
                        if 'Chipset Model' in line:
                            gpu_name = line.split(':')[-1].strip()
                            break
                    
                    if gpu_name:
                        # Apple Silicon GPUs share system memory
                        # Get system memory
                        mem_result = subprocess.run(
                            ["sysctl", "-n", "hw.memsize"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        memory_mb = 0
                        if mem_result.returncode == 0:
                            total_bytes = int(mem_result.stdout.strip())
                            memory_mb = total_bytes // (1024 * 1024)
                        
                        gpu = GPUInfo(
                            vendor=GPUVendor.APPLE,
                            name=gpu_name,
                            memory_mb=memory_mb,
                            device_index=0
                        )
                        gpus.append(gpu)
            
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                pass
        
        return gpus
    
    def get_best_gpu(self) -> Optional[GPUInfo]:
        """
        Get the best available GPU for processing
        
        Returns:
            GPUInfo object for the best GPU, or None if no GPU available
        """
        if not self._detected_gpus:
            self.detect_gpus()
        
        if not self._detected_gpus:
            return None
        
        # Prioritize NVIDIA GPUs (best CUDA support)
        nvidia_gpus = [gpu for gpu in self._detected_gpus if gpu.vendor == GPUVendor.NVIDIA]
        if nvidia_gpus:
            # Return the one with most memory
            return max(nvidia_gpus, key=lambda g: g.memory_mb)
        
        # Then AMD GPUs
        amd_gpus = [gpu for gpu in self._detected_gpus if gpu.vendor == GPUVendor.AMD]
        if amd_gpus:
            return max(amd_gpus, key=lambda g: g.memory_mb)
        
        # Then Apple Silicon
        apple_gpus = [gpu for gpu in self._detected_gpus if gpu.vendor == GPUVendor.APPLE]
        if apple_gpus:
            return apple_gpus[0]
        
        return self._detected_gpus[0]
    
    def get_gpu_by_index(self, index: int) -> Optional[GPUInfo]:
        """
        Get GPU by device index
        
        Args:
            index: Device index
            
        Returns:
            GPUInfo object or None
        """
        if not self._detected_gpus:
            self.detect_gpus()
        
        for gpu in self._detected_gpus:
            if gpu.device_index == index:
                return gpu
        
        return None
    
    def get_gpu_info_dict(self) -> List[Dict]:
        """
        Get GPU information as dictionary
        
        Returns:
            List of GPU information dictionaries
        """
        if not self._detected_gpus:
            self.detect_gpus()
        
        return [
            {
                "vendor": gpu.vendor.value,
                "name": gpu.name,
                "memory_mb": gpu.memory_mb,
                "compute_capability": gpu.compute_capability,
                "device_index": gpu.device_index
            }
            for gpu in self._detected_gpus
        ]
    
    def has_gpu(self) -> bool:
        """Check if any GPU is available"""
        if not self._detected_gpus:
            self.detect_gpus()
        
        return len(self._detected_gpus) > 0
    
    def get_processing_backend(self) -> str:
        """
        Get the recommended processing backend based on available GPU
        
        Returns:
            Backend name: 'cuda', 'rocm', 'metal', or 'cpu'
        """
        best_gpu = self.get_best_gpu()
        
        if best_gpu:
            if best_gpu.vendor == GPUVendor.NVIDIA:
                return "cuda"
            elif best_gpu.vendor == GPUVendor.AMD:
                return "rocm"
            elif best_gpu.vendor == GPUVendor.APPLE:
                return "metal"
        
        return "cpu"


def detect_gpu() -> GPUDetector:
    """
    Create and return a GPU detector instance
    
    Returns:
        GPUDetector instance
    """
    return GPUDetector()


if __name__ == "__main__":
    # Test GPU detection
    detector = detect_gpu()
    gpus = detector.detect_gpus()
    
    print("Detected GPUs:")
    for gpu in gpus:
        print(f"  - {gpu.vendor.value.upper()}: {gpu.name}")
        print(f"    Memory: {gpu.memory_mb} MB")
        if gpu.compute_capability:
            print(f"    Compute Capability: {gpu.compute_capability}")
        print()
    
    best_gpu = detector.get_best_gpu()
    if best_gpu:
        print(f"Best GPU: {best_gpu.name}")
        print(f"Recommended backend: {detector.get_processing_backend()}")
    else:
        print("No GPU detected. Using CPU.")
