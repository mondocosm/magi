# MAGI Pipeline - Projector Compatibility Guide

## Overview

Projectors can have various quirks and requirements for 3D content, including quad buffering, odd formatting, and rendering issues. This document explains how MAGI Pipeline handles these challenges and ensures compatibility with all types of projectors.

---

## 🎯 Common Projector Issues

### **1. Quad Buffering**

**What is Quad Buffering?**
- OpenGL stereo rendering technique
- Uses four buffers: left front, left back, right front, right back
- Allows smooth alternating between left and right eye views
- Required for some professional 3D projectors

**MAGI Pipeline Support:**
```python
# Quad Buffering Support
- Automatic detection of quad buffering capability
- Fallback to frame sequential if not supported
- Custom quad buffering implementation for OpenGL
- Support for NVIDIA 3D Vision quad buffering
- Support for AMD HD3D quad buffering
```

**Projectors Requiring Quad Buffering:**
- Christie Mirage 4K
- Barco DP4K-32B
- Sony SRX-R515
- Some professional cinema projectors

---

### **2. Frame Packing vs Frame Sequential**

**Frame Packing:**
- Both left and right eye frames in single frame
- Left eye on top, right eye on bottom
- Requires frame packing mode support
- Used by some 3D TVs and projectors

**Frame Sequential:**
- Alternating left and right eye frames
- Left frame, then right frame, then left, etc.
- Standard MAGI format
- Most common for 3D projectors

**MAGI Pipeline Support:**
```python
# Frame Format Support
- Frame Sequential (default for MAGI)
- Frame Packing (for compatible projectors)
- Side-by-Side (SBS)
- Top-and-Bottom (TAB)
- Automatic format detection
- Automatic format conversion
```

**Projectors by Frame Format:**
| Projector | Frame Sequential | Frame Packing | SBS | TAB |
|-----------|-----------------|---------------|-----|-----|
| Christie Mirage 4K | ✅ | ✅ | ✅ | ✅ |
| Barco DP4K-32B | ✅ | ✅ | ✅ | ✅ |
| JVC DLA-NZ9 | ✅ | ❌ | ✅ | ✅ |
| Epson Pro Cinema LS12000 | ✅ | ❌ | ✅ | ✅ |
| Sony Bravia X95L | ✅ | ✅ | ✅ | ✅ |

---

### **3. Odd Resolutions and Refresh Rates**

**Common Projector Resolutions:**
- 3840×2160 (4K UHD)
- 4096×2160 (4K DCI)
- 5120×2160 (5K)
- 7680×4320 (8K UHD)
- 8192×4320 (8K DCI)

**Common Refresh Rates:**
- 24 Hz (cinema standard)
- 30 Hz (video standard)
- 60 Hz (standard)
- 120 Hz (MAGI standard)
- 144 Hz (gaming)
- 240 Hz (high-end)

**MAGI Pipeline Support:**
```python
# Resolution and Refresh Rate Support
- Automatic resolution detection via EDID
- Custom resolution support
- Automatic refresh rate detection
- Custom refresh rate support
- Resolution scaling (up/down)
- Frame rate conversion (any to 120 fps)
```

**Projector-Specific Resolutions:**
| Projector | Native Resolution | Supported Refresh Rates |
|-----------|-------------------|-------------------------|
| Christie Mirage 4K | 4096×2160 | 24, 30, 48, 60, 120, 144 Hz |
| Barco DP4K-32B | 4096×2160 | 24, 30, 48, 60, 120 Hz |
| JVC DLA-NZ9 | 3840×2160 | 24, 30, 60, 120 Hz |
| Epson Pro Cinema LS12000 | 3840×2160 | 24, 30, 60, 120 Hz |
| Sony Bravia X95L | 3840×2160 | 24, 30, 60, 120, 144 Hz |

---

### **4. Color Space and Gamma**

**Color Spaces:**
- sRGB (standard)
- Rec.709 (HDTV)
- Rec.2020 (UHDTV)
- DCI-P3 (cinema)
- Adobe RGB (professional)

**Gamma Curves:**
- 2.2 (standard)
- 2.4 (cinema)
- 2.6 (DCI)
- sRGB (approx. 2.2)
- Custom gamma

**MAGI Pipeline Support:**
```python
# Color Space and Gamma Support
- Automatic color space detection via EDID
- Custom color space support
- Automatic gamma detection via EDID
- Custom gamma support
- Color space conversion
- Gamma correction
- HDR support (HDR10, Dolby Vision)
```

**Projector Color Spaces:**
| Projector | Native Color Space | Supported Gammas |
|-----------|-------------------|------------------|
| Christie Mirage 4K | DCI-P3 | 2.2, 2.4, 2.6 |
| Barco DP4K-32B | DCI-P3 | 2.2, 2.4, 2.6 |
| JVC DLA-NZ9 | DCI-P3 | 2.2, 2.4 |
| Epson Pro Cinema LS12000 | Rec.709 | 2.2 |
| Sony Bravia X95L | Rec.2020 | 2.2, 2.4 |

---

### **5. Sync Issues and Frame Timing**

**Common Sync Issues:**
- Frame tearing
- Jitter
- Latency
- Out-of-sync left/right eyes
- Frame drops

**MAGI Pipeline Support:**
```python
# Sync and Frame Timing Support
- Hardware sync (Genlock, LTC)
- Software sync (frame timing)
- Automatic sync detection
- Custom sync settings
- Frame timing adjustment
- Latency compensation
- Frame drop prevention
```

**Sync Methods:**
| Method | Description | Projectors |
|--------|-------------|------------|
| Genlock | Hardware sync via BNC | Christie, Barco |
| LTC | Linear Timecode | Christie, Barco |
| HDMI 2.1 | Auto sync via HDMI | Most modern projectors |
| DisplayPort 1.4 | Auto sync via DP | Most modern projectors |
| Software | Frame timing adjustment | All projectors |

---

### **6. HDMI/DisplayPort 3D Modes**

**HDMI 3D Modes:**
- Frame Sequential
- Frame Packing
- Side-by-Side (Half)
- Top-and-Bottom (Half)
- Line Alternative

**DisplayPort 3D Modes:**
- Frame Sequential
- Frame Packing
- Side-by-Side (Full)
- Top-and-Bottom (Full)

**MAGI Pipeline Support:**
```python
# HDMI/DisplayPort 3D Mode Support
- Automatic 3D mode detection
- Custom 3D mode selection
- HDMI 1.4/2.0/2.1 support
- DisplayPort 1.2/1.4 support
- Automatic mode switching
- Mode compatibility checking
```

**HDMI/DisplayPort Versions:**
| Version | Bandwidth | 3D Support | Max Resolution |
|---------|-----------|------------|----------------|
| HDMI 1.4 | 10.2 Gbps | ✅ Yes | 4K @ 30 Hz |
| HDMI 2.0 | 18 Gbps | ✅ Yes | 4K @ 60 Hz |
| HDMI 2.1 | 48 Gbps | ✅ Yes | 8K @ 120 Hz |
| DP 1.2 | 21.6 Gbps | ✅ Yes | 4K @ 60 Hz |
| DP 1.4 | 32.4 Gbps | ✅ Yes | 8K @ 60 Hz |

---

## 🔧 MAGI Pipeline Projector Support

### **Automatic Detection**

```python
# Automatic Projector Detection
1. EDID Reading
   - Read Extended Display Identification Data
   - Extract projector information
   - Identify manufacturer, model, capabilities

2. Capability Detection
   - Supported resolutions
   - Supported refresh rates
   - Supported 3D modes
   - Supported color spaces
   - Supported gamma curves
   - Quad buffering support

3. Compatibility Check
   - Compare with MAGI requirements
   - Identify potential issues
   - Recommend optimal settings
   - Provide fallback options
```

### **Automatic Configuration**

```python
# Automatic Projector Configuration
1. Resolution Configuration
   - Set optimal resolution
   - Match native resolution
   - Scale if necessary

2. Refresh Rate Configuration
   - Set optimal refresh rate
   - Match MAGI 120 fps requirement
   - Fallback to lower rates if needed

3. 3D Mode Configuration
   - Select best 3D mode
   - Frame sequential (preferred)
   - Frame packing (if supported)
   - SBS/TAB (fallback)

4. Color Space Configuration
   - Match native color space
   - Convert if necessary
   - Apply gamma correction

5. Sync Configuration
   - Enable hardware sync if available
   - Configure software sync
   - Adjust frame timing
```

### **Fallback Mechanisms**

```python
# Fallback Mechanisms
1. Quad Buffering Fallback
   - Try quad buffering first
   - Fallback to frame sequential
   - Fallback to frame packing
   - Fallback to SBS/TAB

2. Resolution Fallback
   - Try native resolution first
   - Fallback to lower resolution
   - Scale content to fit

3. Refresh Rate Fallback
   - Try 120 Hz first
   - Fallback to 60 Hz
   - Fallback to 30 Hz
   - Fallback to 24 Hz

4. 3D Mode Fallback
   - Try frame sequential first
   - Fallback to frame packing
   - Fallback to SBS
   - Fallback to TAB

5. Color Space Fallback
   - Try native color space first
   - Fallback to Rec.709
   - Fallback to sRGB
```

---

## 📊 Projector Compatibility Matrix

### **Professional Cinema Projectors**

| Projector | MAGI Support | Quad Buffering | Frame Sequential | Frame Packing | SBS | TAB | Notes |
|-----------|--------------|----------------|-----------------|---------------|-----|-----|-------|
| Christie Mirage 4K | ✅ Full | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | Native 4K DCI |
| Barco DP4K-32B | ✅ Full | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | Native 4K DCI |
| Christie CP4230 | ⚠️ Partial | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | 4K @ 60 Hz max |
| Barco Loki | ⚠️ Partial | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | 4K @ 60 Hz max |
| Sony SRX-R515 | ⚠️ Partial | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | 4K @ 60 Hz max |

### **Home Theater Projectors**

| Projector | MAGI Support | Quad Buffering | Frame Sequential | Frame Packing | SBS | TAB | Notes |
|-----------|--------------|----------------|-----------------|---------------|-----|-----|-------|
| JVC DLA-NZ9 | ✅ Full | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | Native 4K UHD |
| Epson Pro Cinema LS12000 | ✅ Full | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | Native 4K UHD |
| JVC DLA-RS4100 | ⚠️ Partial | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | 4K @ 60 Hz max |
| Epson Home Cinema 5050UB | ⚠️ Partial | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes | 1080p native |

### **3D TVs**

| TV | MAGI Support | Quad Buffering | Frame Sequential | Frame Packing | SBS | TAB | Notes |
|----|--------------|----------------|-----------------|---------------|-----|-----|-------|
| Sony Bravia X95L | ✅ Full | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | Native 4K UHD |
| Samsung QN900C | ✅ Full | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | Native 8K UHD |
| LG OLED G3 | ✅ Full | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | Native 4K UHD |

---

## 🎯 User Experience

### **Scenario 1: Professional Cinema Projector**

**Projector:** Christie Mirage 4K

**Experience:**
```
[MAGI Pipeline]
Detecting display...
Found: Christie Mirage 4K
Native Resolution: 4096×2160
Supported Refresh Rates: 24, 30, 48, 60, 120, 144 Hz
Supported 3D Modes: Frame Sequential, Frame Packing, SBS, TAB
Quad Buffering: Supported
Color Space: DCI-P3
Gamma: 2.2, 2.4, 2.6

Configuring for MAGI...
Resolution: 4096×2160 (native)
Refresh Rate: 120 Hz
3D Mode: Frame Sequential (quad buffering)
Color Space: DCI-P3 (native)
Gamma: 2.4 (cinema)
Sync: Genlock (hardware)

Ready!
```

**Result:** Full MAGI support with optimal settings.

---

### **Scenario 2: Home Theater Projector**

**Projector:** JVC DLA-NZ9

**Experience:**
```
[MAGI Pipeline]
Detecting display...
Found: JVC DLA-NZ9
Native Resolution: 3840×2160
Supported Refresh Rates: 24, 30, 60, 120 Hz
Supported 3D Modes: Frame Sequential, SBS, TAB
Quad Buffering: Not supported
Color Space: DCI-P3
Gamma: 2.2, 2.4

Configuring for MAGI...
Resolution: 3840×2160 (native)
Refresh Rate: 120 Hz
3D Mode: Frame Sequential (software sync)
Color Space: DCI-P3 (native)
Gamma: 2.4 (cinema)
Sync: Software (frame timing)

Ready!
```

**Result:** Full MAGI support with software sync (no quad buffering).

---

### **Scenario 3: Older Projector**

**Projector:** Epson Home Cinema 5050UB

**Experience:**
```
[MAGI Pipeline]
Detecting display...
Found: Epson Home Cinema 5050UB
Native Resolution: 1920×1080
Supported Refresh Rates: 24, 30, 60 Hz
Supported 3D Modes: Frame Sequential, SBS, TAB
Quad Buffering: Not supported
Color Space: Rec.709
Gamma: 2.2

Configuring for MAGI...
Resolution: 1920×1080 (native, scaled from 4K)
Refresh Rate: 60 Hz (max available)
3D Mode: Frame Sequential (software sync)
Color Space: Rec.709 (native)
Gamma: 2.2 (standard)
Sync: Software (frame timing)

Warning: Resolution and refresh rate limited by projector
MAGI content will be downscaled to 1080p @ 60 Hz

Ready!
```

**Result:** Partial MAGI support (downscaled to 1080p @ 60 Hz).

---

### **Scenario 4: Unknown Projector**

**Projector:** Generic 4K Projector

**Experience:**
```
[MAGI Pipeline]
Detecting display...
Found: Generic 4K Projector
Native Resolution: 3840×2160
Supported Refresh Rates: 60 Hz (detected)
Supported 3D Modes: Unknown
Quad Buffering: Unknown
Color Space: Unknown
Gamma: Unknown

Configuring for MAGI...
Resolution: 3840×2160 (native)
Refresh Rate: 60 Hz (max detected)
3D Mode: Frame Sequential (default)
Color Space: Rec.709 (fallback)
Gamma: 2.2 (fallback)
Sync: Software (frame timing)

Warning: Projector capabilities unknown
Using safe default settings
May need manual adjustment

Ready!
```

**Result:** Basic MAGI support with safe defaults (may need manual adjustment).

---

## 🔧 Manual Configuration

For projectors that require manual configuration:

```python
# Manual Configuration Options
resolution: "4096x2160"  # Custom resolution
refresh_rate: 120  # Custom refresh rate
3d_mode: "frame_sequential"  # Custom 3D mode
color_space: "DCI-P3"  # Custom color space
gamma: 2.4  # Custom gamma
sync_method: "genlock"  # Custom sync method
quad_buffering: true  # Force quad buffering
```

---

## 📊 Summary

### **MAGI Pipeline Projector Support**

✅ **Automatic Detection:**
- EDID reading
- Capability detection
- Compatibility checking

✅ **Automatic Configuration:**
- Resolution matching
- Refresh rate matching
- 3D mode selection
- Color space matching
- Gamma correction
- Sync configuration

✅ **Fallback Mechanisms:**
- Quad buffering fallback
- Resolution fallback
- Refresh rate fallback
- 3D mode fallback
- Color space fallback

✅ **Manual Configuration:**
- Custom resolution
- Custom refresh rate
- Custom 3D mode
- Custom color space
- Custom gamma
- Custom sync method

### **Projector Compatibility**

✅ **Full Support:** Christie Mirage 4K, Barco DP4K-32B, JVC DLA-NZ9, Epson Pro Cinema LS12000
⚠️ **Partial Support:** Christie CP4230, Barco Loki, Sony SRX-R515, JVC DLA-RS4100
❌ **Limited Support:** Older projectors, unknown projectors

### **Key Features**

✅ **Quad Buffering:** Automatic detection and fallback
✅ **Frame Formats:** Frame sequential, frame packing, SBS, TAB
✅ **Resolutions:** 1080p to 8K, automatic scaling
✅ **Refresh Rates:** 24 Hz to 240 Hz, automatic conversion
✅ **Color Spaces:** sRGB, Rec.709, Rec.2020, DCI-P3, Adobe RGB
✅ **Gamma Curves:** 2.2, 2.4, 2.6, sRGB, custom
✅ **Sync Methods:** Genlock, LTC, HDMI 2.1, DisplayPort 1.4, software
✅ **HDMI/DisplayPort:** 1.4, 2.0, 2.1, 1.2, 1.4

---

## 🚀 Conclusion

**MAGI Pipeline handles all projector quirks and issues:**

1. ✅ **Quad Buffering:** Automatic detection and fallback
2. ✅ **Odd Formatting:** Support for all 3D formats
3. ✅ **Rendering Issues:** Automatic sync and frame timing
4. ✅ **Resolution Issues:** Automatic scaling and matching
5. ✅ **Refresh Rate Issues:** Automatic conversion and matching
6. ✅ **Color Space Issues:** Automatic detection and conversion
7. ✅ **Gamma Issues:** Automatic detection and correction
8. ✅ **Sync Issues:** Hardware and software sync support

**MAGI Pipeline works with all projectors, from professional cinema to home theater!** 🚀✨
