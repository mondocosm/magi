"""
Cloud GPU integration for MAGI Pipeline
Supports RunPod, Vast.ai, Lambda Labs, and custom endpoints
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading


class CloudProvider(Enum):
    """Cloud GPU providers"""
    LOCAL = "local"
    RUNPOD = "runpod"
    VASTAI = "vastai"
    LAMBDA = "lambda"
    CUSTOM = "custom"


@dataclass
class CloudGPUInstance:
    """Cloud GPU instance information"""
    instance_id: str
    provider: CloudProvider
    gpu_type: str
    gpu_count: int
    status: str  # starting, running, stopped, terminated
    ip_address: Optional[str] = None
    port: Optional[int] = None
    cost_per_hour: float = 0.0
    region: str = "us-east-1"
    created_at: float = field(default_factory=time.time)


@dataclass
class CloudJob:
    """Cloud processing job"""
    job_id: str
    instance_id: str
    status: str  # pending, running, completed, failed
    input_path: str
    output_path: str
    progress: float = 0.0
    message: str = ""
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None


class CloudGPUManager:
    """Manage cloud GPU instances and jobs"""
    
    def __init__(self, config):
        """
        Initialize cloud GPU manager
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.active_instances: Dict[str, CloudGPUInstance] = {}
        self.active_jobs: Dict[str, CloudJob] = {}
        self._lock = threading.Lock()
        
        # Provider-specific configurations
        self._provider_configs = {
            CloudProvider.RUNPOD: {
                "api_base": "https://api.runpod.io/v2",
                "headers": lambda key: {"Authorization": f"Bearer {key}"}
            },
            CloudProvider.VASTAI: {
                "api_base": "https://console.vast.ai/api/v0",
                "headers": lambda key: {"Authorization": f"Bearer {key}"}
            },
            CloudProvider.LAMBDA: {
                "api_base": "https://cloud.lambdalabs.com/api/v1",
                "headers": lambda key: {"Authorization": f"Bearer {key}"}
            }
        }
    
    def is_enabled(self) -> bool:
        """Check if cloud GPU is enabled"""
        return self.config.cloud.enabled
    
    def get_provider(self) -> CloudProvider:
        """Get current cloud provider"""
        provider_str = self.config.cloud.provider.lower()
        try:
            return CloudProvider(provider_str)
        except ValueError:
            return CloudProvider.LOCAL
    
    def launch_instance(self, gpu_type: Optional[str] = None) -> Optional[CloudGPUInstance]:
        """
        Launch a cloud GPU instance
        
        Args:
            gpu_type: Type of GPU to request (uses config default if not specified)
            
        Returns:
            CloudGPUInstance object or None if failed
        """
        if not self.is_enabled():
            return None
        
        provider = self.get_provider()
        if provider == CloudProvider.LOCAL:
            return None
        
        gpu_type = gpu_type or self.config.cloud.gpu_type
        
        try:
            if provider == CloudProvider.RUNPOD:
                instance = self._launch_runpod_instance(gpu_type)
            elif provider == CloudProvider.VASTAI:
                instance = self._launch_vastai_instance(gpu_type)
            elif provider == CloudProvider.LAMBDA:
                instance = self._launch_lambda_instance(gpu_type)
            elif provider == CloudProvider.CUSTOM:
                instance = self._launch_custom_instance(gpu_type)
            else:
                return None
            
            if instance:
                with self._lock:
                    self.active_instances[instance.instance_id] = instance
                
                return instance
        
        except Exception as e:
            print(f"Error launching cloud instance: {e}")
            return None
    
    def _launch_runpod_instance(self, gpu_type: str) -> Optional[CloudGPUInstance]:
        """Launch RunPod instance"""
        api_key = self.config.cloud.api_key
        if not api_key:
            raise ValueError("RunPod API key not configured")
        
        headers = self._provider_configs[CloudProvider.RUNPOD]["headers"](api_key)
        
        # Create pod
        payload = {
            "name": f"magi-pipeline-{int(time.time())}",
            "image": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel",
            "gpuType": gpu_type,
            "gpuCount": 1,
            "volumeInGb": 50,
            "containerDiskInGb": 10,
            "minMemoryInGb": 30,
            "minVcpuCount": 4,
            "env": [
                {"key": "MAGI_PIPELINE", "value": "1"}
            ]
        }
        
        response = requests.post(
            f"{self._provider_configs[CloudProvider.RUNPOD]['api_base']}/pods",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return CloudGPUInstance(
                instance_id=data["id"],
                provider=CloudProvider.RUNPOD,
                gpu_type=gpu_type,
                gpu_count=1,
                status="starting",
                cost_per_hour=self._get_runpod_cost(gpu_type),
                region=self.config.cloud.region
            )
        
        return None
    
    def _launch_vastai_instance(self, gpu_type: str) -> Optional[CloudGPUInstance]:
        """Launch Vast.ai instance"""
        api_key = self.config.cloud.api_key
        if not api_key:
            raise ValueError("Vast.ai API key not configured")
        
        headers = self._provider_configs[CloudProvider.VASTAI]["headers"](api_key)
        
        # Search for instances
        search_params = {
            "gpu_name": gpu_type,
            "min_gpu_ram": 24,
            "min_disk_space": 50,
            "min_cpu_ram": 30,
            "internet_max": 10,
            "reliability": 0.9
        }
        
        response = requests.get(
            f"{self._provider_configs[CloudProvider.VASTAI]['api_base']}/bundles",
            headers=headers,
            params=search_params,
            timeout=30
        )
        
        if response.status_code == 200:
            instances = response.json()
            if instances:
                # Launch the first available instance
                instance_id = instances[0]["id"]
                return CloudGPUInstance(
                    instance_id=instance_id,
                    provider=CloudProvider.VASTAI,
                    gpu_type=gpu_type,
                    gpu_count=1,
                    status="starting",
                    cost_per_hour=instances[0]["dph_total"],
                    region=instances[0].get("geolocation", {}).get("region", "unknown")
                )
        
        return None
    
    def _launch_lambda_instance(self, str) -> Optional[CloudGPUInstance]:
        """Launch Lambda Labs instance"""
        api_key = self.config.cloud.api_key
        if not api_key:
            raise ValueError("Lambda Labs API key not configured")
        
        headers = self._provider_configs[CloudProvider.LAMBDA]["headers"](api_key)
        
        # Create instance
        payload = {
            "region_name": self.config.cloud.region,
            "instance_type": gpu_type,
            "file_system_names": [],
            "quantity": 1
        }
        
        response = requests.post(
            f"{self._provider_configs[CloudProvider.LAMBDA]['api_base']}/instance-operations/launch",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return CloudGPUInstance(
                instance_id=data["id"],
                provider=CloudProvider.LAMBDA,
                gpu_type=gpu_type,
                gpu_count=1,
                status="starting",
                cost_per_hour=self._get_lambda_cost(gpu_type),
                region=self.config.cloud.region
            )
        
        return None
    
    def _launch_custom_instance(self, gpu_type: str) -> Optional[CloudGPUInstance]:
        """Launch custom endpoint instance"""
        endpoint = self.config.cloud.endpoint
        if not endpoint:
            raise ValueError("Custom endpoint not configured")
        
        # For custom endpoints, we just create a placeholder instance
        return CloudGPUInstance(
            instance_id="custom-" + str(int(time.time())),
            provider=CloudProvider.CUSTOM,
            gpu_type=gpu_type,
            gpu_count=1,
            status="running",
            ip_address=endpoint,
            cost_per_hour=0.0,
            region="custom"
        )
    
    def _get_runpod_cost(self, gpu_type: str) -> float:
        """Get estimated cost for RunPod GPU type"""
        # Approximate costs (USD per hour)
        costs = {
            "NVIDIA RTX 3090": 0.44,
            "NVIDIA RTX 4090": 0.79,
            "NVIDIA A100 80GB": 1.89,
            "NVIDIA A6000": 0.79,
            "NVIDIA V100": 0.74
        }
        return costs.get(gpu_type, 0.50)
    
    def _get_lambda_cost(self, gpu_type: str) -> float:
        """Get estimated cost for Lambda Labs GPU type"""
        # Approximate costs (USD per hour)
        costs = {
            "gpu_1x_a10": 0.60,
            "gpu_1x_a100": 1.49,
            "gpu_1x_a6000": 0.90,
            "gpu_1x_rtx_3090": 0.50,
            "gpu_1x_rtx_4090": 0.80
        }
        return costs.get(gpu_type, 0.60)
    
    def get_instance_status(self, instance_id: str) -> Optional[str]:
        """
        Get status of a cloud instance
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Status string or None if not found
        """
        with self._lock:
            instance = self.active_instances.get(instance_id)
            if not instance:
                return None
        
        # Update status from provider
        try:
            if instance.provider == CloudProvider.RUNPOD:
                status = self._get_runpod_status(instance_id)
            elif instance.provider == CloudProvider.VASTAI:
                status = self._get_vastai_status(instance_id)
            elif instance.provider == CloudProvider.LAMBDA:
                status = self._get_lambda_status(instance_id)
            else:
                status = instance.status
            
            if status:
                with self._lock:
                    instance.status = status
            
            return status
        
        except Exception as e:
            print(f"Error getting instance status: {e}")
            return instance.status
    
    def _get_runpod_status(self, instance_id: str) -> Optional[str]:
        """Get RunPod instance status"""
        api_key = self.config.cloud.api_key
        headers = self._provider_configs[CloudProvider.RUNPOD]["headers"](api_key)
        
        response = requests.get(
            f"{self._provider_configs[CloudProvider.RUNPOD]['api_base']}/pods/{instance_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("status", "unknown")
        
        return None
    
    def _get_vastai_status(self, instance_id: str) -> Optional[str]:
        """Get Vast.ai instance status"""
        api_key = self.config.cloud.api_key
        headers = self._provider_configs[CloudProvider.VASTAI]["headers"](api_key)
        
        response = requests.get(
            f"{self._provider_configs[CloudProvider.VASTAI]['api_base']}/instances/{instance_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("state", "unknown")
        
        return None
    
    def _get_lambda_status(self, instance_id: str) -> Optional[str]:
        """Get Lambda Labs instance status"""
        api_key = self.config.cloud.api_key
        headers = self._provider_configs[CloudProvider.LAMBDA]["headers"](api_key)
        
        response = requests.get(
            f"{self._provider_configs[CloudProvider.LAMBDA]['api_base']}/instances/{instance_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("status", "unknown")
        
        return None
    
    def terminate_instance(self, instance_id: str) -> bool:
        """
        Terminate a cloud instance
        
        Args:
            instance_id: Instance ID
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            instance = self.active_instances.get(instance_id)
            if not instance:
                return False
        
        try:
            if instance.provider == CloudProvider.RUNPOD:
                success = self._terminate_runpod_instance(instance_id)
            elif instance.provider == CloudProvider.VASTAI:
                success = self._terminate_vastai_instance(instance_id)
            elif instance.provider == CloudProvider.LAMBDA:
                success = self._terminate_lambda_instance(instance_id)
            else:
                success = True  # Custom endpoints don't need termination
            
            if success:
                with self._lock:
                    instance.status = "terminated"
            
            return success
        
        except Exception as e:
            print(f"Error terminating instance: {e}")
            return False
    
    def _terminate_runpod_instance(self, instance_id: str) -> bool:
        """Terminate RunPod instance"""
        api_key = self.config.cloud.api_key
        headers = self._provider_configs[CloudProvider.RUNPOD]["headers"](api_key)
        
        response = requests.post(
            f"{self._provider_configs[CloudProvider.RUNPOD]['api_base']}/pods/{instance_id}/terminate",
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200
    
    def _terminate_vastai_instance(self, instance_id: str) -> bool:
        """Terminate Vast.ai instance"""
        api_key = self.config.cloud.api_key
        headers = self._provider_configs[CloudProvider.VASTAI]["headers"](api_key)
        
        response = requests.delete(
            f"{self._provider_configs[CloudProvider.VASTAI]['api_base']}/instances/{instance_id}",
            headers=headers,
            timeout=10
        )
        
        return response.status_code == 200
    
    def _terminate_lambda_instance(self, instance_id: str) -> bool:
        """Terminate Lambda Labs instance"""
        api_key = self.config.cloud.api_key
        headers = self._provider_configs[CloudProvider.LAMBDA]["headers"](api_key)
        
        response = requests.post(
            f"{self._provider_configs[CloudProvider.LAMBDA]['api_base']}/instance-operations/terminate",
            headers=headers,
            json={"instance_ids": [instance_id]},
            timeout=10
        )
        
        return response.status_code == 200
    
    def list_instances(self) -> List[CloudGPUInstance]:
        """List all active instances"""
        with self._lock:
            return list(self.active_instances.values())
    
    def cleanup_terminated_instances(self):
        """Clean up terminated instances from the list"""
        with self._lock:
            to_remove = [
                instance_id for instance_id, instance in self.active_instances.items()
                if instance.status in ["terminated", "stopped"]
            ]
            for instance_id in to_remove:
                del self.active_instances[instance_id]
    
    def get_total_cost(self) -> float:
        """Calculate total cost of all active instances"""
        total_cost = 0.0
        current_time = time.time()
        
        with self._lock:
            for instance in self.active_instances.values():
                if instance.status == "running":
                    hours_running = (current_time - instance.created_at) / 3600
                    total_cost += hours_running * instance.cost_per_hour
        
        return total_cost


def create_cloud_manager(config) -> CloudGPUManager:
    """
    Create cloud GPU manager instance
    
    Args:
        config: Configuration object
        
    Returns:
        CloudGPUManager instance
    """
    return CloudGPUManager(config)


if __name__ == "__main__":
    # Test cloud manager
    from ..core.config import Config
    
    config = Config()
    manager = create_cloud_manager(config)
    
    print(f"Cloud enabled: {manager.is_enabled()}")
    print(f"Provider: {manager.get_provider()}")
    print(f"Active instances: {len(manager.list_instances())}")
