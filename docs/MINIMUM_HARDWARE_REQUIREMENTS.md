# MAGI Pipeline - Minimum Hardware Requirements

## Overview

This document outlines the minimum hardware requirements for converting any video content to MAGI format using the MAGI Pipeline software.

---

## Minimum System Requirements

### **Absolute Minimum (Basic Conversion)**

**For converting 1080p@24fps to 1080p@120fps MAGI:**

| Component | Minimum Requirement | Recommended |
|-----------|---------------------|-------------|
| **CPU** | Intel Core i5-10400 (6 cores) | Intel Core i7-12700 (12 cores) |
| **GPU** | NVIDIA GTX 1660 SUPER (6GB VRAM) | NVIDIA RTX 3060 (12GB VRAM) |
| **RAM** | 16GB DDR4 | 32GB DDR4 |
| **Storage** | 500GB SSD (SATA) | 1TB NVMe SSD |
| **OS** | Windows 10/11 64-bit | Windows 11 64-bit |
| **Power Supply** | 500W | 650W |

**Performance:**
- **Processing Speed:** 0.5x real-time (2 hours video = 4 hours processing)
- **Quality:** Basic interpolation and upscaling
- **Resolution:** Up to 1080p per eye
- **Frame Rate:** Up to 120 fps

**Use Cases:**
- Converting standard Blu-ray movies
- Basic 2D to 3D conversion
- Home theater use

---

### **Recommended Minimum (Good Performance)**

**For converting 4K@24fps to 4K@120fps MAGI:**

| Component | Minimum Requirement | Recommended |
|-----------|---------------------|-------------|
| **CPU** | Intel Core i7-12700 (12 cores) | Intel Core i9-13900 (24 cores) |
| **GPU** | NVIDIA RTX 3060 (12GB VRAM) | NVIDIA RTX 4070 (12GB VRAM) |
| **RAM** | 32GB DDR4 | 64GB DDR5 |
| **Storage** | 1TB NVMe SSD | 2TB NVMe SSD |
| **OS** | Windows 11 64-bit | Windows 11 64-bit |
| **Power Supply** | 650W | 750W |

**Performance:**
- **Processing Speed:** 1x real-time (1 hour video = 1 hour processing)
- **Quality:** Good interpolation and upscaling
- **Resolution:** Up to 4K per eye
- **Frame Rate:** Up to 120 fps

**Use Cases:**
- Converting 4K Blu-ray movies
- High-quality 2D to 3D conversion
- Professional home theater
- Small studio use

---

### **Optimal (Best Performance)**

**For converting 4K@60fps to 4K@120fps MAGI with AI enhancement:**

| Component | Minimum Requirement | Recommended |
|-----------|---------------------|-------------|
| **CPU** | Intel Core i9-13900 (24 cores) | Intel Core i9-14900 (24 cores) |
| **GPU** | NVIDIA RTX 4070 (12GB VRAM) | NVIDIA RTX 4090 (24GB VRAM) |
| **RAM** | 64GB DDR5 | 128GB DDR5 |
| **Storage** | 2TB NVMe SSD | 4TB NVMe SSD |
| **OS** | Windows 11 64-bit | Windows 11 64-bit |
| **Power Supply** | 750W | 1000W |

**Performance:**
- **Processing Speed:** 2x real-time (1 hour video = 30 minutes processing)
- **Quality:** Best interpolation and upscaling with AI
- **Resolution:** Up to 4K per eye
- **Frame Rate:** Up to 120 fps

**Use Cases:**
- Converting 4K@60fps content
- AI-enhanced 2D to 3D conversion
- Professional cinema
- Large studio use
- Real-time conversion

---

## Component Breakdown

### **CPU (Central Processing Unit)**

**Minimum:**
- **Intel Core i5-10400** (6 cores, 12 threads, 4.3 GHz)
- **AMD Ryzen 5 3600** (6 cores, 12 threads, 4.2 GHz)

**Recommended:**
- **Intel Core i7-12700** (12 cores, 20 threads, 5.0 GHz)
- **AMD Ryzen 7 5800X** (8 cores, 16 threads, 4.7 GHz)

**Optimal:**
- **Intel Core i9-13900** (24 cores, 32 threads, 5.8 GHz)
- **AMD Ryzen 9 7950X** (16 cores, 32 threads, 5.7 GHz)

**Why CPU Matters:**
- Video decoding (H.264, H.265, MPEG-2)
- System management
- File I/O operations
- Multi-threading for parallel processing

---

### **GPU (Graphics Processing Unit)**

**Minimum:**
- **NVIDIA GTX 1660 SUPER** (6GB VRAM, 1408 CUDA cores)
- **AMD RX 5600 XT** (6GB VRAM, 2304 stream processors)

**Recommended:**
- **NVIDIA RTX 3060** (12GB VRAM, 3584 CUDA cores)
- **AMD RX 6700 XT** (12GB VRAM, 2560 stream processors)

**Optimal:**
- **NVIDIA RTX 4090** (24GB VRAM, 16384 CUDA cores)
- **AMD RX 7900 XTX** (24GB VRAM, 6144 stream processors)

**Why GPU Matters:**
- AI processing (StereoCrafter, RIFE, Waifu2x)
- Frame interpolation
- Upscaling
- 3D rendering
- Video encoding (HEVC H.265)

**GPU Requirements by Task:**

| Task | Minimum VRAM | Recommended VRAM |
|------|--------------|------------------|
| **2D to 3D Conversion** | 6GB | 12GB |
| **Frame Interpolation** | 6GB | 12GB |
| **Upscaling to 4K** | 8GB | 16GB |
| **MAGI Encoding** | 6GB | 12GB |
| **Real-time Processing** | 12GB | 24GB |

---

### **RAM (Random Access Memory)**

**Minimum:**
- **16GB DDR4** (2666 MHz)

**Recommended:**
- **32GB DDR4** (3200 MHz)

**Optimal:**
- **64GB DDR5** (4800 MHz)

**Why RAM Matters:**
- Frame buffering
- Processing buffer
- System memory
- Multi-tasking

**RAM Requirements by Resolution:**

| Resolution | Minimum RAM | Recommended RAM |
|------------|-------------|-----------------|
| **1080p** | 16GB | 32GB |
| **4K** | 32GB | 64GB |
| **8K** | 64GB | 128GB |

---

### **Storage**

**Minimum:**
- **500GB SSD** (SATA, 550 MB/s read/write)

**Recommended:**
- **1TB NVMe SSD** (PCIe 3.0, 3500 MB/s read/write)

**Optimal:**
- **2TB NVMe SSD** (PCIe 4.0, 7000 MB/s read/write)

**Why Storage Matters:**
- Fast read/write for video files
- Temporary storage for processing
- System performance
- File I/O speed

**Storage Requirements by Video Length:**

| Video Length | Minimum Storage | Recommended Storage |
|--------------|-----------------|---------------------|
| **1 hour (1080p)** | 50GB | 100GB |
| **1 hour (4K)** | 200GB | 400GB |
| **1 hour (8K)** | 800GB | 1.6TB |

---

### **Power Supply**

**Minimum:**
- **500W** (80+ Bronze)

**Recommended:**
- **650W** (80+ Gold)

**Optimal:**
- **1000W** (80+ Platinum)

**Why Power Supply Matters:**
- Stable power delivery
- GPU power requirements
- System stability
- Efficiency

**Power Requirements by GPU:**

| GPU | Minimum Power | Recommended Power |
|-----|---------------|-------------------|
| **GTX 1660 SUPER** | 450W | 500W |
| **RTX 3060** | 550W | 650W |
| **RTX 4070** | 650W | 750W |
| **RTX 4090** | 850W | 1000W |

---

## Operating System Requirements

### **Windows**

**Minimum:**
- **Windows 10** (64-bit, version 21H2 or later)
- **Windows 11** (64-bit, version 22H2 or later)

**Recommended:**
- **Windows 11** (64-bit, version 23H2 or later)

**Requirements:**
- DirectX 12 support
- GPU drivers (NVIDIA 530+ or AMD 23.10+)
- .NET Framework 4.8
- Visual C++ Redistributable 2015-2022

---

### **macOS**

**Minimum:**
- **macOS 12.0** (Monterey) or later
- **Apple Silicon M1** or later
- **Intel-based Mac** (with dedicated GPU)

**Recommended:**
- **macOS 14.0** (Sonoma) or later
- **Apple Silicon M2** or later

**Requirements:**
- Metal support
- GPU drivers (latest)
- Xcode Command Line Tools

---

### **Linux**

**Minimum:**
- **Ubuntu 22.04 LTS** or later
- **Fedora 38** or later
- **Debian 12** or later

**Recommended:**
- **Ubuntu 24.04 LTS** or later
- **Fedora 40** or later

**Requirements:**
- GPU drivers (NVIDIA 530+ or AMD 23.10+)
- Vulkan support
- FFmpeg 6.0+

---

## Software Requirements

### **Required Software**

| Software | Minimum Version | Recommended Version |
|----------|-----------------|---------------------|
| **Python** | 3.10 | 3.11 |
| **FFmpeg** | 6.0 | 6.1 |
| **CUDA** | 11.8 | 12.4 |
| **PyTorch** | 2.0 | 2.2 |
| **OpenCV** | 4.8 | 4.9 |
| **NumPy** | 1.24 | 1.26 |

### **Optional Software**

| Software | Purpose |
|----------|---------|
| **StereoCrafter** | 2D to 3D conversion |
| **RIFE** | Frame interpolation |
| **Waifu2x** | Upscaling |
| **RealESRGAN** | Upscaling |
| **TensorRT** | GPU acceleration |

---

## Performance Benchmarks

### **Processing Speed by Hardware**

| Hardware | 1080p@24fps | 4K@24fps | 4K@60fps |
|----------|-------------|----------|----------|
| **Minimum** | 0.5x | 0.25x | 0.1x |
| **Recommended** | 1x | 0.5x | 0.25x |
| **Optimal** | 2x | 1x | 0.5x |

**Example:**
- **Minimum:** 1 hour video = 2 hours processing (1080p)
- **Recommended:** 1 hour video = 1 hour processing (1080p)
- **Optimal:** 1 hour video = 30 minutes processing (1080p)

---

## Cost Estimates

### **Minimum System Cost**

| Component | Cost |
|-----------|------|
| **CPU** | $150 - $200 |
| **GPU** | $200 - $250 |
| **RAM** | $50 - $70 |
| **Storage** | $50 - $70 |
| **Motherboard** | $100 - $150 |
| **Power Supply** | $50 - $70 |
| **Case** | $50 - $70 |
| **Total** | **$650 - $880** |

### **Recommended System Cost**

| Component | Cost |
|-----------|------|
| **CPU** | $300 - $400 |
| **GPU** | $300 - $400 |
| **RAM** | $100 - $150 |
| **Storage** | $100 - $150 |
| **Motherboard** | $200 - $300 |
| **Power Supply** | $100 - $150 |
| **Case** | $100 - $150 |
| **Total** | **$1,200 - $1,700** |

### **Optimal System Cost**

| Component | Cost |
|-----------|------|
| **CPU** | $600 - $700 |
| **GPU** | $1,600 - $2,000 |
| **RAM** | $200 - $300 |
| **Storage** | $200 - $300 |
| **Motherboard** | $300 - $400 |
| **Power Supply** | $200 - $300 |
| **Case** | $150 - $200 |
| **Total** | **$3,250 - $4,200** |

---

## Pre-built Systems

### **Minimum Pre-built**

| System | Price | Specs |
|--------|-------|-------|
| **Dell Inspiron Desktop** | $700 - $800 | i5-12400, RTX 3060, 16GB RAM, 512GB SSD |
| **HP Pavilion Gaming** | $750 - $850 | i5-12400, RTX 3060, 16GB RAM, 512GB SSD |
| **Lenovo Legion Tower 5** | $800 - $900 | i5-12400, RTX 3060, 16GB RAM, 512GB SSD |

### **Recommended Pre-built**

| System | Price | Specs |
|--------|-------|-------|
| **Dell XPS Desktop** | $1,500 - $1,800 | i7-13700, RTX 4070, 32GB RAM, 1TB SSD |
| **HP Omen Desktop** | $1,600 - $1,900 | i7-13700, RTX 4070, 32GB RAM, 1TB SSD |
| **Lenovo Legion Tower 7** | $1,700 - $2,000 | i7-13700, RTX 4070, 32GB RAM, 1TB SSD |

### **Optimal Pre-built**

| System | Price | Specs |
|--------|-------|-------|
| **Dell Alienware Aurora R16** | $3,500 - $4,000 | i9-14900, RTX 4090, 64GB RAM, 2TB SSD |
| **HP Omen 45L** | $3,600 - $4,100 | i9-14900, RTX 4090, 64GB RAM, 2TB SSD |
| **Lenovo Legion Tower 9i** | $3,800 - $4,300 | i9-14900, RTX 4090, 64GB RAM, 2TB SSD |

---

## Cloud Alternative

If you don't have the required hardware, you can use the **MAGI Cloud Service**:

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0/month | 100 MB files, 3 conversions/day, 1080p |
| **Pro** | $9.99/month | 2 GB files, 50 conversions/day, 4K |
| **Enterprise** | $99.99/month | 10 GB files, unlimited, 8K |

**Benefits:**
- No hardware required
- No installation needed
- Access from anywhere
- Automatic updates

---

## Summary

### **Absolute Minimum (Basic)**
- **Cost:** $650 - $880
- **Performance:** 0.5x real-time
- **Use Case:** Basic 1080p conversion

### **Recommended (Good)**
- **Cost:** $1,200 - $1,700
- **Performance:** 1x real-time
- **Use Case:** 4K conversion, professional use

### **Optimal (Best)**
- **Cost:** $3,250 - $4,200
- **Performance:** 2x real-time
- **Use Case:** 4K@60fps, AI enhancement, real-time

### **Cloud Alternative**
- **Cost:** $0 - $99.99/month
- **Performance:** Depends on tier
- **Use Case:** No hardware, convenience

---

## Conclusion

The **minimum hardware** required to convert anything to MAGI format is:

- **CPU:** Intel Core i5-10400 or AMD Ryzen 5 3600
- **GPU:** NVIDIA GTX 1660 SUPER or AMD RX 5600 XT
- **RAM:** 16GB DDR4
- **Storage:** 500GB SSD
- **OS:** Windows 10/11 64-bit
- **Power Supply:** 500W

**Total Cost:** $650 - $880

This minimum system can convert 1080p@24fps content to 1080p@120fps MAGI format at 0.5x real-time speed.

**For better performance and 4K support, we recommend the recommended system with a cost of $1,200 - $1,700.**

**For the best performance and real-time conversion, we recommend the optimal system with a cost of $3,250 - $4,200.**

**If you don't have the hardware, you can use the MAGI Cloud Service starting at $0/month.** 🚀
