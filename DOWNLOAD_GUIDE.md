# How to Download MAGI Pipeline Executables

## Quick Start

The executables are now available in GitHub Actions! Follow these steps:

## Step-by-Step Instructions

### 1. Go to GitHub Actions

1. Navigate to the MAGI Pipeline repository: https://github.com/mondocosm/magi
2. Click on the **Actions** tab at the top of the page (between "Pull requests" and "Projects")

### 2. Find the Latest Workflow Run

1. You'll see a list of workflow runs on the left side
2. Look for the most recent run with a green checkmark (✓) indicating success
3. The workflows you'll see are:
   - **Build Windows Executable** - For Windows users
   - **Build macOS Executable** - For macOS users
   - **Build Linux Executable** - For Linux users
   - **Build All Platforms** - Contains all platforms in one download

### 3. Click on the Workflow Run

1. Click on the workflow run name (e.g., "Build Windows Executable")
2. This will show you the details of that specific run

### 4. Find the Artifacts Section

**Important**: The Artifacts section is located at the **bottom** of the workflow run page, not at the top!

1. Scroll all the way to the bottom of the page
2. Look for a section titled **"Artifacts"** (usually near the bottom, after the job logs)
3. You should see one or more artifact names listed

### 5. Download the Executable

1. Click on the artifact name for your platform:
   - **Windows**: Click "MAGI-Pipeline-Windows-Executable"
   - **macOS**: Click "MAGI-Pipeline-macOS-Executable"
   - **Linux**: Click "MAGI-Pipeline-Linux-Executable"
   - **All Platforms**: Click "MAGI-Pipeline-All-Platforms"

2. The download will start automatically (a .zip file)

### 6. Extract and Run

**Windows:**
1. Extract the downloaded .zip file
2. Double-click `MAGI-Pipeline-Windows.exe`
3. The web UI will open automatically in your browser

**macOS:**
1. Extract the downloaded .zip file
2. Double-click `MAGI Pipeline.app`
3. The web UI will open automatically in your browser

**Linux:**
1. Extract the downloaded .zip file
2. Open a terminal in the extracted directory
3. Run: `chmod +x MAGI-Pipeline-Linux`
4. Run: `./MAGI-Pipeline-Linux`
5. The web UI will open automatically in your browser

## Troubleshooting

### Can't find the Artifacts section?

1. **Make sure you're on a workflow run page**: You should see workflow logs and job information
2. **Scroll to the bottom**: The Artifacts section is at the very bottom of the page
3. **Check if the workflow completed**: Look for a green checkmark (✓) next to the workflow run
4. **Wait for the build to complete**: If the workflow is still running, artifacts won't be available yet

### No recent workflow runs?

1. Workflows are triggered automatically when code is pushed to the master branch
2. You can also trigger workflows manually:
   - Go to the Actions tab
   - Click on the workflow name (e.g., "Build Windows Executable")
   - Click "Run workflow" button on the right side
   - Select the branch and click "Run workflow"

### Download failed?

1. Try refreshing the page and clicking the artifact again
2. Check your internet connection
3. Try a different browser
4. If the issue persists, open an issue on GitHub

## Alternative: Build from Source

If you prefer to build from source or can't download the executables:

```bash
# Clone the repository
git clone https://github.com/mondocosm/magi.git
cd magi

# Install dependencies
pip install -r requirements.txt

# Run the web UI
python -m src.ui.web_ui

# Or run the desktop launcher
python -m src.ui.desktop_launcher
```

## What's Included?

Each executable includes:
- Full MAGI Pipeline web UI
- MAGI Viewer with test patterns
- 3D display mode support
- Frame synchronization (VSync, G-Sync, FreeSync)
- Real-time game capture
- Camera input support
- All video processing features

## Need Help?

If you encounter any issues:
1. Check the [User Manual](USER_MANUAL.md)
2. Open an issue on GitHub: https://github.com/mondocosm/magi/issues
3. Review the [FAQ](docs/FAQ.md)

## System Requirements

**Minimum:**
- CPU: 4-core processor
- RAM: 8 GB
- GPU: Integrated graphics or entry-level GPU
- Storage: 10 GB free space

**Recommended:**
- CPU: 8-core processor or better
- RAM: 16 GB or more
- GPU: NVIDIA RTX 3060 or better, AMD RX 6600 or better, Apple M1 or better
- Storage: 50 GB free space (SSD recommended)