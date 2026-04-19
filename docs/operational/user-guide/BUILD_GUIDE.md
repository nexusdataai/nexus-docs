# Windows Installer Build Guide

This guide explains how to build the Totogi Capability Installer Windows executable (.exe) for distribution to customers.

## Overview

The build process creates a self-contained Windows installer that includes:
- React frontend (bundled with Vite)
- Python backend (bundled with PyInstaller)
- Electron desktop wrapper (packaged with electron-builder)

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Node.js | 18.x or higher | Frontend build and Electron packaging |
| Python | 3.11.x | Backend runtime |
| Git | Latest | Source control |

### Installation Commands

```powershell
# Verify installations
node --version    # Should show v18.x.x or higher
python --version  # Should show Python 3.11.x
git --version     # Any recent version
```

### Python Dependencies

```powershell
# Install PyInstaller globally (or in venv)
pip install pyinstaller
```

## Project Structure

```
starhub-deployer/
├── frontend/           # React application
│   ├── dist/          # Built frontend (created during build)
│   └── package.json
├── backend/           # FastAPI backend
│   ├── app/           # Application code
│   ├── capabilities/  # Capability definitions
│   ├── dist/          # Built backend (created during build)
│   └── requirements.txt
├── electron/          # Electron wrapper
│   ├── dist/          # Final installer (created during build)
│   ├── main.js
│   └── package.json
└── scripts/
    └── capabilities/  # Capability CloudFormation templates
```

## Build Process

### Step 1: Build the Python Backend

The backend must be compiled into a standalone executable using PyInstaller.

#### 1.1 Create Virtual Environment (if not exists)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller
```

#### 1.2 Create PyInstaller Spec File

Create `backend/backend.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all app submodules
hiddenimports = collect_submodules('app')
hiddenimports += [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'boto3',
    'botocore',
    'tinydb',
    'pydantic',
    'pydantic_settings',
    'cryptography',
    'httpx',
    'aiofiles',
    'websockets',
    'beautifulsoup4',
    'lxml',
    'yaml',
]

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('capabilities', 'capabilities'),
        ('data', 'data'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='totogi-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for production to hide console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

#### 1.3 Build Backend Executable

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pyinstaller backend.spec --clean
```

This creates `backend/dist/totogi-backend.exe`

### Step 2: Build the React Frontend

```powershell
cd frontend

# Install dependencies (first time only)
npm install

# Build for production
npm run build
```

This creates the `frontend/dist/` directory with optimized static files.

### Step 3: Package with Electron Builder

#### 3.1 Install Electron Dependencies

```powershell
cd electron
npm install
```

#### 3.2 Set Environment Variable

The electron-builder config uses `${env.EXE_EXT}` for cross-platform builds:

```powershell
# Windows PowerShell
$env:EXE_EXT = ".exe"
```

#### 3.3 Build Windows Installer

```powershell
cd electron
npm run build:win
```

This creates two outputs in `electron/dist/`:
- `Totogi Installer Setup x.x.x.exe` - NSIS installer
- `Totogi Installer x.x.x.exe` - Portable executable

## Complete Build Script

Create `build-windows.ps1` in the project root:

```powershell
# build-windows.ps1 - Complete Windows build script
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Totogi Capability Installer - Windows Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Set environment variable for electron-builder
$env:EXE_EXT = ".exe"

# Step 1: Build Backend
Write-Host "`n[1/3] Building Python Backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

.\venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

Write-Host "Running PyInstaller..."
pyinstaller backend.spec --clean --noconfirm

if (-not (Test-Path "dist/totogi-backend.exe")) {
    Write-Error "Backend build failed - totogi-backend.exe not found"
    exit 1
}
Write-Host "Backend build complete!" -ForegroundColor Green

# Step 2: Build Frontend
Write-Host "`n[2/3] Building React Frontend..." -ForegroundColor Yellow
Set-Location ../frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..."
    npm install
}

npm run build

if (-not (Test-Path "dist/index.html")) {
    Write-Error "Frontend build failed - dist/index.html not found"
    exit 1
}
Write-Host "Frontend build complete!" -ForegroundColor Green

# Step 3: Package with Electron
Write-Host "`n[3/3] Packaging with Electron Builder..." -ForegroundColor Yellow
Set-Location ../electron

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..."
    npm install
}

npm run build:win

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nOutput files:"
Get-ChildItem -Path "dist" -Filter "*.exe" | ForEach-Object {
    Write-Host "  - $($_.FullName)" -ForegroundColor White
}

Set-Location ..
```

Run the complete build:

```powershell
.\build-windows.ps1
```

## Output Files

After a successful build, you'll find these files in `electron/dist/`:

| File | Description | Use Case |
|------|-------------|----------|
| `Totogi Installer Setup x.x.x.exe` | NSIS installer | Standard installation with shortcuts |
| `Totogi Installer x.x.x.exe` | Portable executable | No installation required |

### NSIS Installer Features

The NSIS installer provides:
- Custom installation directory selection
- Desktop shortcut creation
- Start menu shortcut creation
- Uninstaller in Add/Remove Programs

## Troubleshooting

### PyInstaller Issues

**Problem**: `ModuleNotFoundError` when running the built executable

**Solution**: Add the missing module to `hiddenimports` in `backend.spec`:
```python
hiddenimports += ['missing_module_name']
```

**Problem**: Data files not found (capabilities, templates)

**Solution**: Ensure `datas` in the spec file includes all required directories:
```python
datas=[
    ('capabilities', 'capabilities'),
    ('data', 'data'),
]
```

### Electron Builder Issues

**Problem**: `extraResources` not found

**Solution**: Verify the backend executable exists before running electron-builder:
```powershell
Test-Path "backend/dist/totogi-backend.exe"
```

**Problem**: Build fails with signing errors

**Solution**: For unsigned builds, you can skip code signing:
```powershell
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
npm run build:win
```

### Frontend Build Issues

**Problem**: TypeScript compilation errors

**Solution**: Fix type errors or build with:
```powershell
npm run build -- --skipLibCheck
```

## Code Signing (Optional)

For production releases, sign the executable with a code signing certificate:

1. Obtain a code signing certificate from a trusted CA
2. Set environment variables:
   ```powershell
   $env:CSC_LINK = "path/to/certificate.pfx"
   $env:CSC_KEY_PASSWORD = "certificate_password"
   ```
3. Run the build - electron-builder will automatically sign

## Version Management

Update version numbers in these files before building:

1. `electron/package.json` - `version` field
2. `frontend/package.json` - `version` field
3. `backend/app/main.py` - `version` in FastAPI app

## Distribution Checklist

Before distributing to customers:

- [ ] All tests pass (`npm test` in frontend, `pytest` in backend)
- [ ] Version numbers updated
- [ ] Build completes without errors
- [ ] Installer runs on clean Windows machine
- [ ] Application connects to AWS successfully
- [ ] Deployment wizard completes end-to-end
- [ ] Uninstaller works correctly

## CI/CD Integration

For automated builds, see the GitHub Actions workflow in `.github/workflows/build.yml` (if available).

Example workflow step:
```yaml
- name: Build Windows Installer
  run: |
    $env:EXE_EXT = ".exe"
    .\build-windows.ps1
  shell: pwsh
```
