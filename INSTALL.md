# Installation and Setup

## Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| git | any | for cloning |
| Python 3 | 3.8+ | for the cross-platform scaffolding engine and GUI |
| tkinter | — | GUI only; included with the standard Python.org Windows installer |
| PowerShell | 5.1+ | Windows launch and validation scripts |
| bash | 4.0+ | Linux/macOS shell launchers; macOS ships bash 3 — see macOS note below |
| sed, awk | standard | used by legacy shell workflows on Linux/macOS |

---

## 1. Clone the repo

```bash
git clone https://github.com/Adamgdwn/new-build-governance-agent.git
```

You can put it anywhere. A good default:

```bash
git clone https://github.com/Adamgdwn/new-build-governance-agent.git ~/code/new-build-governance-agent
cd ~/code/new-build-governance-agent
```

---

## 2. Windows first run

For non-technical Windows users, download the release package from GitHub **Releases**:

1. Download `NewBuildGovernanceAgent-Windows.zip`.
2. Unzip it.
3. If your projects should live somewhere other than the default code workspace, set `NEW_BUILD_CODE_ROOT` as described below.
4. Double-click `NewBuildGovernanceAgent.exe`.

The `.exe` opens the desktop GUI and shows a Windows error dialog if Python or the full package is missing.

For normal development and future self-updates, use `git clone` instead of a release ZIP or source ZIP download. Self-update requires a cloned checkout with an upstream branch.

From PowerShell:

```powershell
cd new-build-governance-agent
.\automation\new_build.ps1
```

To launch the GUI:

```powershell
.\automation\launch_gui.ps1
```

The two Windows launcher files are:

- `NewBuildGovernanceAgent.exe` for the double-click desktop GUI.
- `automation\new_build.ps1` for the terminal guided intake.
- `automation\launch_gui.ps1` for the desktop GUI.
- `scripts\build-windows-launcher.ps1` for building `dist\NewBuildGovernanceAgent-Windows.zip` from source on Windows.

If PowerShell blocks local scripts, run this from the cloned repository for the current process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

The Windows launchers keep these categories:

```text
agents        AI agent projects
Applications  apps, tools, automations, and other builds
```

By default, generated projects are created under your code workspace. If this agent is installed inside `code` or `01. Code Projects`, that parent folder is used. Otherwise, the default is `%USERPROFILE%\code`.

Set `NEW_BUILD_CODE_ROOT` before launching when you want a specific project root:

```powershell
$env:NEW_BUILD_CODE_ROOT = "C:\Users\you\01. Code Projects"
New-Item -ItemType Directory -Force -Path "$env:NEW_BUILD_CODE_ROOT\agents", "$env:NEW_BUILD_CODE_ROOT\Applications"
.\automation\launch_gui.ps1
```

Run Windows validation with:

```powershell
.\scripts\validate.ps1
```

The Windows validator checks required governance files, project-control schema, Python compilation, PowerShell syntax, optional shell syntax when Bash is available, unit tests, and Windows launcher smoke tests.

The new-build and GUI launch paths do not require WSL. Some governance and release workflows still call shell tooling when you use the Linux/macOS scripts or advanced release checks.

---

## 3. Make Linux/macOS scripts executable

```bash
chmod +x automation/new_build.sh
chmod +x automation/launch_gui.sh
chmod +x automation/bootstrap_project.sh
chmod +x automation/governance_check.sh
chmod +x automation/check_required_files.sh
```

---

## 4. Set your Linux/macOS project root

The Linux/macOS launchers use the same categories:

```text
agents        AI agent projects
Applications  apps, tools, automations, and other builds
```

By default, generated projects are created under your code workspace. If this agent is installed inside `code` or `01. Code Projects`, that parent folder is used. Otherwise, the default is `~/code`.

Set `NEW_BUILD_CODE_ROOT` before launching when you want a specific project root:

```bash
export NEW_BUILD_CODE_ROOT="$HOME/code"
mkdir -p "$NEW_BUILD_CODE_ROOT/agents" "$NEW_BUILD_CODE_ROOT/Applications"
bash automation/new_build.sh
```

For a persistent setting, add the `export NEW_BUILD_CODE_ROOT=...` line to your shell profile.

If you use the default root, make the target directories if they do not exist:

```bash
mkdir -p ~/code/agents ~/code/Applications
```

---

## 5. Set your name (optional)

The launchers fill the `Project Owner` field in `project-control.yaml` with a default owner. For the Bash launcher, find this line and change it to yours:

```bash
sed -i "s/name: Project Owner/name: Adam Goodwin/" "$PC"
```

---

## 6. Verify

Run the Linux/macOS terminal launcher:

```bash
bash automation/new_build.sh
```

You should see the intake prompt. Enter a name, pick `app`, accept the defaults, and confirm. Check that a new directory was created under your `APPS_ROOT`.

---

## GUI setup (Linux)

### Install tkinter

**Debian / Ubuntu / Pop!_OS:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**Arch:**
```bash
sudo pacman -S tk
```

### Run the GUI

```bash
python3 automation/new_build_gui.py
```

### Add a desktop launcher

To launch the GUI from your application menu or desktop, create a `.desktop` file:

```bash
REPO="$HOME/code/new-build-governance-agent"   # adjust to where you cloned

cat > ~/.local/share/applications/new-build-governance-agent.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=New Build Governance Agent
Comment=Scope and scaffold a new governed project
Icon=${REPO}/automation/new-build-governance-agent.svg
Exec=${REPO}/automation/launch_gui.sh
Terminal=false
StartupNotify=true
Categories=Development;Utility;
EOF

chmod +x ~/.local/share/applications/new-build-governance-agent.desktop
update-desktop-database ~/.local/share/applications/
```

The wrapper script keeps the launch command stable even if the repo path contains spaces and writes launcher errors to `data/new-build-governance-agent/logs/`.

To also add a shortcut to your Desktop:

```bash
cp ~/.local/share/applications/new-build-governance-agent.desktop ~/Desktop/
chmod +x ~/Desktop/New\ Build\ Agent.desktop
```

---

## macOS

macOS ships with bash 3, which lacks some features used in `new_build.sh` (associative arrays, `mapfile`). Install a current bash first:

```bash
brew install bash
```

Then run scripts explicitly with the Homebrew bash:

```bash
/opt/homebrew/bin/bash automation/new_build.sh
```

tkinter on macOS requires the full Python.org installer or a Homebrew Python built with tk:

```bash
brew install python-tk
python3 automation/new_build_gui.py
```

The `.desktop` launcher is Linux-only. On macOS, create an Automator app or use the terminal command above.

---

## Using with pyenv

If you manage Python with pyenv, point the scripts at your pyenv Python:

```bash
~/.pyenv/versions/3.12.1/bin/python3 automation/new_build_gui.py
```

Or set the version in your project directory:

```bash
cd ~/code/new-build-governance-agent
pyenv local 3.12.1
```

Then `python3` will resolve correctly.

---

## Optional: add to PATH

To run `new_build.sh` from anywhere without a full path, add the automation directory to your shell profile:

**bash (`~/.bashrc` or `~/.bash_profile`):**
```bash
export PATH="$HOME/code/new-build-governance-agent/automation:$PATH"
```

**zsh (`~/.zshrc`):**
```zsh
export PATH="$HOME/code/new-build-governance-agent/automation:$PATH"
```

Then reload your shell and run:
```bash
new_build.sh
```

---

## Updating

```bash
cd ~/code/new-build-governance-agent
git pull
```

Updates to templates only affect new projects — existing projects are not changed.
