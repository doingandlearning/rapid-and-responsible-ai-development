# Software Installation Guide
**University of Edinburgh IT Services**

---

## Overview

This guide provides step-by-step instructions for installing and configuring software on university-managed systems. All installations must comply with university licensing agreements and security policies.

## Prerequisites

Before installing any software, ensure you have:

- [ ] Valid university credentials
- [ ] Administrative privileges (if required)
- [ ] Sufficient disk space (check with `df -h`)
- [ ] Internet connectivity
- [ ] Software license (if applicable)

## Installation Methods

### 1. University Software Center

The preferred method for installing approved software:

```bash
# Access software center
open /Applications/University\ Software\ Center.app

# Or via command line
software-center --list-available
software-center --install "Software Name"
```

**Available Software:**
- Microsoft Office 365
- Adobe Creative Suite
- MATLAB
- SPSS
- Python 3.x
- R Statistical Software

### 2. Package Managers

#### Homebrew (macOS)
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install software
brew install python
brew install node
brew install git
```

#### Chocolatey (Windows)
```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install software
choco install python
choco install nodejs
choco install git
```

#### APT (Linux)
```bash
# Update package list
sudo apt update

# Install software
sudo apt install python3
sudo apt install nodejs
sudo apt install git
```

### 3. Manual Installation

For software not available through package managers:

1. **Download from official source**
2. **Verify checksum** (if provided)
3. **Run installer with appropriate permissions**
4. **Configure according to university standards**

## Software-Specific Instructions

### Python Development Environment

#### Step 1: Install Python
```bash
# macOS/Linux
brew install python3

# Windows
choco install python3
```

#### Step 2: Set up Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install packages
pip install --upgrade pip
pip install requests pandas numpy
```

#### Step 3: Configure IDE
```json
// VS Code settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

### R Statistical Software

#### Installation
```bash
# macOS
brew install r

# Windows
choco install r.project

# Linux
sudo apt install r-base
```

#### Package Management
```r
# Install packages
install.packages(c("tidyverse", "ggplot2", "dplyr"))

# Load packages
library(tidyverse)
library(ggplot2)
```

### MATLAB

#### Installation via Software Center
1. Open University Software Center
2. Search for "MATLAB"
3. Click "Install"
4. Follow on-screen instructions

#### License Configuration
```matlab
% Set license server
license('test', 'MATLAB')
license('checkout', 'MATLAB')
```

## Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Check permissions
ls -la /usr/local/bin/

# Fix permissions (if appropriate)
sudo chown -R $(whoami) /usr/local/bin/
```

#### Disk Space Issues
```bash
# Check disk usage
df -h

# Clean up temporary files
# macOS:
sudo rm -rf /private/var/folders/*/T/*
# Linux:
sudo apt autoremove
sudo apt autoclean
# Windows:
cleanmgr /sagerun:1
```

#### Network Connectivity
```bash
# Test connectivity
ping google.com
nslookup ed.ac.uk

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

### Software-Specific Troubleshooting

#### Python Import Errors
```python
# Check Python path
import sys
print(sys.path)

# Add path if needed
sys.path.append('/path/to/module')
```

#### R Package Installation Failures
```r
# Check available packages
available.packages()

# Install from source if needed
install.packages("package_name", type = "source")
```

## Security Considerations

### License Compliance
- Only install software with valid licenses
- Report unlicensed software immediately
- Keep track of license renewals

### Security Scanning
```bash
# Scan for vulnerabilities (if available)
security-scan --scan-software

# Update all packages
# Python:
pip list --outdated
pip install --upgrade package_name

# R:
update.packages()
```

### Data Protection
- Never install software that requires excessive permissions
- Ensure software doesn't collect unnecessary data
- Use university-approved alternatives when possible

## Support and Resources

### Getting Help
- **IT Helpdesk:** ithelpdesk@ed.ac.uk
- **Software Support:** software-support@ed.ac.uk
- **Documentation:** https://www.ed.ac.uk/information-services/computing

### Useful Commands
```bash
# Check installed software
# macOS:
brew list
# Windows:
choco list --local-only
# Linux:
dpkg -l

# Check system information
# macOS:
system_profiler SPSoftwareDataType
# Windows:
systeminfo
# Linux:
uname -a
```

### Emergency Procedures
If software installation causes system instability:

1. **Disconnect from network**
2. **Boot into safe mode**
3. **Uninstall problematic software**
4. **Contact IT support immediately**

---

**Last Updated:** December 2024  
**Version:** 1.2  
**Next Review:** March 2025
