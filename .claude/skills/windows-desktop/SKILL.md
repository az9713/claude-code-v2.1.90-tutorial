---
name: windows-desktop
description: Use when performing Windows Desktop operations like window management, launching apps, taking screenshots, controlling volume, reading system info, or listing files. Enforces READ-ONLY for all file and directory operations.
allowed-tools: Bash(powershell.exe *), Bash(powershell *), Bash(rundll32.exe *), Read, Glob, Grep
---

# Windows Desktop Control

Control the Windows desktop via PowerShell. **All file and directory operations are STRICTLY READ-ONLY.**

## Safety Rules — ABSOLUTE CONSTRAINTS

### READ-ONLY File Policy

**You MUST NOT modify, create, move, rename, or delete any file or directory on the user's system.**
The ONLY exception is screenshot capture, which creates a new image file.

### PROHIBITED Commands — NEVER Execute These

| Category | Prohibited Commands | Reason |
|----------|-------------------|--------|
| **File Write/Delete** | `Remove-Item`, `Delete`, `Move-Item`, `Rename-Item`, `Set-Content`, `Add-Content`, `Out-File`, `New-Item`, `Copy-Item` (to new location), `rm`, `del`, `ren`, `move`, `rd`, `rmdir`, `mkdir` (use `New-Item` only for screenshots) | Files are READ-ONLY |
| **Process Kill** | `Stop-Process`, `Kill`, `taskkill`, `End-Process` | No process killing |
| **Shutdown/Restart** | `Restart-Computer`, `Stop-Computer`, `shutdown`, `shutdown.exe` | No shutdown/restart |
| **Registry Write** | `Set-ItemProperty` on HKLM/HKCU, `New-ItemProperty`, `Remove-ItemProperty`, `New-Item` on Registry | No registry writes |
| **Service Control** | `Start-Service`, `Stop-Service`, `Set-Service`, `Restart-Service` | No service control |
| **Network Changes** | `Set-NetAdapter`, `Disable-NetAdapter`, `Enable-NetAdapter`, `Set-DnsClientServerAddress`, `netsh` (write ops) | No network changes |
| **User/Security** | `Set-LocalUser`, `New-LocalUser`, `Remove-LocalUser`, `Add-LocalGroupMember`, `Remove-LocalGroupMember`, `icacls` (write), `takeown` | No user/security changes |
| **Execution Policy** | `Set-ExecutionPolicy` | No policy changes |
| **Firewall** | `Set-NetFirewallRule`, `New-NetFirewallRule`, `Remove-NetFirewallRule` | No firewall changes |
| **Scheduled Tasks** | `Register-ScheduledTask`, `Unregister-ScheduledTask`, `Set-ScheduledTask` | No task scheduling |

### Additional Safety Rules

- **Never pipe output to files** — No `> file`, `>> file`, `| Out-File`, `| Set-Content`
- **Never use `Invoke-Expression`** on untrusted input
- **Never download or execute remote scripts** — No `Invoke-WebRequest` to download executables
- **Never modify environment variables** — No `[Environment]::SetEnvironmentVariable`, no `$env:VAR = ...` persistently
- **Always prefer `-WhatIf`** when unsure about a command's side effects
- **Screenshot exception**: You MAY use `[System.Drawing.Bitmap]::new()` or similar to save a screenshot file. State the save path to the user first.

## Operation Categories

| # | Category | Read-Only? | Key Operations |
|---|----------|-----------|----------------|
| 1 | Window Management | No | List, minimize, maximize, restore, move, resize, snap, close |
| 2 | Application Management | Mixed | List processes (read), launch/switch apps (allowed) |
| 3 | Clipboard | No | Read clipboard, copy text to clipboard |
| 4 | Display Info | **READ-ONLY** | Resolution, monitors, brightness, DPI |
| 5 | Audio/Volume | No | Get/set volume, mute/unmute, list devices |
| 6 | System Info | **READ-ONLY** | CPU, RAM, disk, battery, OS, uptime |
| 7 | Network Info | **READ-ONLY** | WiFi, IP, adapters, DNS, gateway |
| 8 | File/Directory | **STRICTLY READ-ONLY** | List, search, read, properties, size |
| 9 | Virtual Desktops | No | List, create, switch |
| 10 | Screenshot | No | Full screen, active window, region (creates file) |
| 11 | Power Management | No | Lock screen, sleep (NOT shutdown/restart) |
| 12 | Notifications | No | Send toast notification |
| 13 | Services | **READ-ONLY** | List services, get status |
| 14 | Installed Software | **READ-ONLY** | List installed programs |
| 15 | Environment Variables | **READ-ONLY** | List all, get specific |
| 16 | Keyboard/Mouse | No | Send keystrokes, move mouse, click |

## Quick Reference

### Window Management
```powershell
# List all visible windows
powershell.exe -Command "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object Id, ProcessName, MainWindowTitle | Format-Table -AutoSize"

# Get active window title
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\", CharSet=CharSet.Auto)] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count); }'; $sb = New-Object System.Text.StringBuilder 256; [Win32]::GetWindowText([Win32]::GetForegroundWindow(), $sb, 256); $sb.ToString()"
```

### Application Management
```powershell
# Launch an application
powershell.exe -Command "Start-Process 'notepad.exe'"

# List running processes (top 20 by CPU)
powershell.exe -Command "Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 Id, ProcessName, CPU, WorkingSet64 | Format-Table -AutoSize"
```

### System Info
```powershell
# CPU, RAM, OS summary
powershell.exe -Command "$os = Get-CimInstance Win32_OperatingSystem; $cpu = Get-CimInstance Win32_Processor; Write-Output \"OS: $($os.Caption) $($os.Version)\"; Write-Output \"CPU: $($cpu.Name)\"; Write-Output \"RAM: $([math]::Round($os.TotalVisibleMemorySize/1MB, 2)) GB total, $([math]::Round($os.FreePhysicalMemory/1MB, 2)) GB free\"; Write-Output \"Uptime: $((Get-Date) - $os.LastBootUpTime)\""
```

### File/Directory (READ-ONLY)
```powershell
# List directory contents
powershell.exe -Command "Get-ChildItem -Path 'C:\Users' | Format-Table Name, LastWriteTime, Length, Mode -AutoSize"

# Search for files by name
powershell.exe -Command "Get-ChildItem -Path 'C:\Users' -Recurse -Filter '*.txt' -ErrorAction SilentlyContinue | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize"

# Get file properties
powershell.exe -Command "Get-ItemProperty -Path 'C:\path\to\file' | Select-Object FullName, Length, CreationTime, LastWriteTime, LastAccessTime"

# Get directory size
powershell.exe -Command "(Get-ChildItem -Path 'C:\path' -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB"
```

### Audio/Volume
```powershell
# Get current volume (requires AudioDeviceCmdlets or nircmd approach)
powershell.exe -Command "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; [Guid(\"5CDF2C82-841E-4546-9722-0CF74078229A\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IAudioEndpointVolume { int _0(); int _1(); int _2(); int _3(); int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext); int _5(); int GetMasterVolumeLevelScalar(out float pfLevel); int SetMute(bool bMute, System.Guid pguidEventContext); int GetMute(out bool pbMute); } [Guid(\"D666063F-1587-4E43-81F1-B948E807363F\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDevice { int Activate(ref System.Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface); } [Guid(\"A95664D2-9614-4F35-A746-DE8DB63617E6\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDeviceEnumerator { int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice); } [ComImport, Guid(\"BCDE0395-E52F-467C-8E3D-C4579291692E\")] class MMDeviceEnumerator {} '; $enumerator = New-Object MMDeviceEnumerator; $device = $null; $enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device); $iid = [Guid]'5CDF2C82-841E-4546-9722-0CF74078229A'; $volume = $null; $device.Activate([ref]$iid, 1, [IntPtr]::Zero, [ref]$volume); $level = 0.0; $volume.GetMasterVolumeLevelScalar([ref]$level); [math]::Round($level * 100)"
```

### Screenshot
```powershell
# Full screen screenshot
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size); $path = \"$env:TEMP\screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png\"; $bmp.Save($path); $g.Dispose(); $bmp.Dispose(); Write-Output \"Screenshot saved: $path\""
```

### Network Info
```powershell
# IP addresses and network info
powershell.exe -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne '127.0.0.1'} | Select-Object InterfaceAlias, IPAddress, PrefixLength | Format-Table -AutoSize"
```

## Common Mistakes to Avoid

1. **DO NOT** use `>` or `Out-File` to redirect output to files — display output in terminal only
2. **DO NOT** use `Remove-Item` even if the user asks — explain the read-only policy
3. **DO NOT** use `Stop-Process` to close apps — use graceful window close via `SendMessage(WM_CLOSE)` instead
4. **DO NOT** use `shutdown` or `Restart-Computer` — only `Lock-Workstation` and sleep are allowed
5. **DO NOT** modify registry, services, or firewall rules
6. **DO NOT** use `Set-ExecutionPolicy` — work within current policy using `-Command` parameter
7. **ALWAYS** use `powershell.exe -Command "..."` syntax for Bash tool compatibility
8. **ALWAYS** use `-ErrorAction SilentlyContinue` for recursive file searches to avoid permission errors flooding output

## Full Command Reference

See [powershell-reference.md](./powershell-reference.md) for detailed commands for all 16 operation categories.
