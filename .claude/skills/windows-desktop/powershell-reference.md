# PowerShell Command Reference — Windows Desktop Control

Full command reference for all 16 operation categories. All commands use `powershell.exe -Command "..."` syntax for Bash compatibility.

**REMINDER: File and directory operations are STRICTLY READ-ONLY. See SKILL.md for prohibited commands.**

---

## 1. Window Management

### List All Visible Windows
```powershell
powershell.exe -Command "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object Id, ProcessName, MainWindowTitle | Format-Table -AutoSize"
```

### Get Active (Foreground) Window
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\", CharSet=CharSet.Auto)] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count); [DllImport(\"user32.dll\")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId); }'; $hwnd = [Win32]::GetForegroundWindow(); $sb = New-Object System.Text.StringBuilder 256; [Win32]::GetWindowText($hwnd, $sb, 256); $pid = 0; [Win32]::GetWindowThreadProcessId($hwnd, [ref]$pid); Write-Output \"Window: $($sb.ToString()) (PID: $pid, HWND: $hwnd)\""
```

### Minimize a Window by Process Name
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }'; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::ShowWindow($proc.MainWindowHandle, 6); Write-Output 'Minimized' } else { Write-Output 'Window not found' }"
```

### Maximize a Window
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }'; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::ShowWindow($proc.MainWindowHandle, 3); Write-Output 'Maximized' } else { Write-Output 'Window not found' }"
```

### Restore a Window
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }'; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::ShowWindow($proc.MainWindowHandle, 9); Write-Output 'Restored' } else { Write-Output 'Window not found' }"
```

### Move and Resize a Window
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint); }'; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::MoveWindow($proc.MainWindowHandle, 100, 100, 800, 600, $true); Write-Output 'Moved to (100,100) size 800x600' } else { Write-Output 'Window not found' }"
```

### Snap Window to Left Half
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint); [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }'; $screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::ShowWindow($proc.MainWindowHandle, 9); [Win32]::MoveWindow($proc.MainWindowHandle, $screen.Left, $screen.Top, $screen.Width/2, $screen.Height, $true); Write-Output 'Snapped to left half' } else { Write-Output 'Window not found' }"
```

### Snap Window to Right Half
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint); [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }'; $screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::ShowWindow($proc.MainWindowHandle, 9); [Win32]::MoveWindow($proc.MainWindowHandle, $screen.Width/2, $screen.Top, $screen.Width/2, $screen.Height, $true); Write-Output 'Snapped to right half' } else { Write-Output 'Window not found' }"
```

### Set Window Always-On-Top
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags); }'; $HWND_TOPMOST = [IntPtr](-1); $SWP_NOMOVE = 0x0002; $SWP_NOSIZE = 0x0001; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::SetWindowPos($proc.MainWindowHandle, $HWND_TOPMOST, 0, 0, 0, 0, $SWP_NOMOVE -bor $SWP_NOSIZE); Write-Output 'Set always-on-top' } else { Write-Output 'Window not found' }"
```

### Close Window Gracefully (WM_CLOSE)
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam); }'; $WM_CLOSE = 0x0010; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::SendMessage($proc.MainWindowHandle, $WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero); Write-Output 'Sent WM_CLOSE' } else { Write-Output 'Window not found' }"
```

### Bring Window to Foreground
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr hWnd); [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }'; $proc = Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::ShowWindow($proc.MainWindowHandle, 9); [Win32]::SetForegroundWindow($proc.MainWindowHandle); Write-Output 'Brought to foreground' } else { Write-Output 'Window not found' }"
```

---

## 2. Application Management

### Launch an Application
```powershell
powershell.exe -Command "Start-Process 'notepad.exe'"
```

### Launch with Arguments
```powershell
powershell.exe -Command "Start-Process 'code' -ArgumentList 'C:\path\to\project'"
```

### Launch a UWP/Store App
```powershell
powershell.exe -Command "Start-Process 'shell:AppsFolder\Microsoft.WindowsCalculator_8wekyb3d8bbwe!App'"
```

### List Running Processes (Top 20 by CPU)
```powershell
powershell.exe -Command "Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 Id, ProcessName, @{N='CPU(s)';E={[math]::Round($_.CPU,2)}}, @{N='Mem(MB)';E={[math]::Round($_.WorkingSet64/1MB,2)}} | Format-Table -AutoSize"
```

### List Running Processes (Top 20 by Memory)
```powershell
powershell.exe -Command "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 20 Id, ProcessName, @{N='CPU(s)';E={[math]::Round($_.CPU,2)}}, @{N='Mem(MB)';E={[math]::Round($_.WorkingSet64/1MB,2)}} | Format-Table -AutoSize"
```

### Find a Specific Process
```powershell
powershell.exe -Command "Get-Process -Name '*chrome*' -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, MainWindowTitle, @{N='Mem(MB)';E={[math]::Round($_.WorkingSet64/1MB,2)}} | Format-Table -AutoSize"
```

### Switch to Application (Bring to Front)
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr hWnd); [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); }'; $proc = Get-Process -Name 'chrome' -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; if ($proc) { [Win32]::ShowWindow($proc.MainWindowHandle, 9); [Win32]::SetForegroundWindow($proc.MainWindowHandle); Write-Output 'Switched to app' } else { Write-Output 'App not found' }"
```

---

## 3. Clipboard

### Read Clipboard Text
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::GetText()"
```

### Copy Text to Clipboard
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetText('Hello, World!')"
```

### Check Clipboard Content Type
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; $d = [System.Windows.Forms.Clipboard]::GetDataObject(); $d.GetFormats() | ForEach-Object { Write-Output $_ }"
```

---

## 4. Display Info (READ-ONLY)

### Get Screen Resolution
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::AllScreens | ForEach-Object { Write-Output \"$($_.DeviceName): $($_.Bounds.Width)x$($_.Bounds.Height) (Working: $($_.WorkingArea.Width)x$($_.WorkingArea.Height)) Primary: $($_.Primary)\" }"
```

### List All Monitors
```powershell
powershell.exe -Command "Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | Select-Object InstanceName, @{N='HSize(cm)';E={$_.MaxHorizontalImageSize}}, @{N='VSize(cm)';E={$_.MaxVerticalImageSize}}, Active | Format-Table -AutoSize"
```

### Get DPI Scaling
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class DPI { [DllImport(\"gdi32.dll\")] public static extern int GetDeviceCaps(IntPtr hdc, int nIndex); [DllImport(\"user32.dll\")] public static extern IntPtr GetDC(IntPtr hWnd); [DllImport(\"user32.dll\")] public static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC); }'; $hdc = [DPI]::GetDC([IntPtr]::Zero); $dpiX = [DPI]::GetDeviceCaps($hdc, 88); $dpiY = [DPI]::GetDeviceCaps($hdc, 90); [DPI]::ReleaseDC([IntPtr]::Zero, $hdc); Write-Output \"DPI: ${dpiX}x${dpiY} (Scale: $([math]::Round($dpiX/96*100))%)\""
```

### Get Display Brightness
```powershell
powershell.exe -Command "(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness -ErrorAction SilentlyContinue).CurrentBrightness"
```

---

## 5. Audio/Volume

### Get Current Volume Level
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; [Guid(\"5CDF2C82-841E-4546-9722-0CF74078229A\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IAudioEndpointVolume { int _0(); int _1(); int _2(); int _3(); int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext); int _5(); int GetMasterVolumeLevelScalar(out float pfLevel); int SetMute(bool bMute, System.Guid pguidEventContext); int GetMute(out bool pbMute); } [Guid(\"D666063F-1587-4E43-81F1-B948E807363F\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDevice { int Activate(ref System.Guid iid, int dwClsCtx, System.IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface); } [Guid(\"A95664D2-9614-4F35-A746-DE8DB63617E6\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDeviceEnumerator { int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice); } [ComImport, Guid(\"BCDE0395-E52F-467C-8E3D-C4579291692E\")] class MMDeviceEnumerator {} '; $enumerator = New-Object MMDeviceEnumerator; $device = $null; $enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device); $iid = [Guid]'5CDF2C82-841E-4546-9722-0CF74078229A'; $volume = $null; $device.Activate([ref]$iid, 1, [IntPtr]::Zero, [ref]$volume); $level = 0.0; $volume.GetMasterVolumeLevelScalar([ref]$level); $muted = $false; $volume.GetMute([ref]$muted); Write-Output \"Volume: $([math]::Round($level * 100))% Muted: $muted\""
```

### Set Volume Level
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; [Guid(\"5CDF2C82-841E-4546-9722-0CF74078229A\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IAudioEndpointVolume { int _0(); int _1(); int _2(); int _3(); int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext); int _5(); int GetMasterVolumeLevelScalar(out float pfLevel); int SetMute(bool bMute, System.Guid pguidEventContext); int GetMute(out bool pbMute); } [Guid(\"D666063F-1587-4E43-81F1-B948E807363F\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDevice { int Activate(ref System.Guid iid, int dwClsCtx, System.IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface); } [Guid(\"A95664D2-9614-4F35-A746-DE8DB63617E6\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDeviceEnumerator { int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice); } [ComImport, Guid(\"BCDE0395-E52F-467C-8E3D-C4579291692E\")] class MMDeviceEnumerator {} '; $enumerator = New-Object MMDeviceEnumerator; $device = $null; $enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device); $iid = [Guid]'5CDF2C82-841E-4546-9722-0CF74078229A'; $volume = $null; $device.Activate([ref]$iid, 1, [IntPtr]::Zero, [ref]$volume); $volume.SetMasterVolumeLevelScalar(0.50, [Guid]::Empty); Write-Output 'Volume set to 50%'"
```

### Mute/Unmute
```powershell
# Mute
powershell.exe -Command "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; [Guid(\"5CDF2C82-841E-4546-9722-0CF74078229A\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IAudioEndpointVolume { int _0(); int _1(); int _2(); int _3(); int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext); int _5(); int GetMasterVolumeLevelScalar(out float pfLevel); int SetMute(bool bMute, System.Guid pguidEventContext); int GetMute(out bool pbMute); } [Guid(\"D666063F-1587-4E43-81F1-B948E807363F\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDevice { int Activate(ref System.Guid iid, int dwClsCtx, System.IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface); } [Guid(\"A95664D2-9614-4F35-A746-DE8DB63617E6\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDeviceEnumerator { int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice); } [ComImport, Guid(\"BCDE0395-E52F-467C-8E3D-C4579291692E\")] class MMDeviceEnumerator {} '; $enumerator = New-Object MMDeviceEnumerator; $device = $null; $enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device); $iid = [Guid]'5CDF2C82-841E-4546-9722-0CF74078229A'; $volume = $null; $device.Activate([ref]$iid, 1, [IntPtr]::Zero, [ref]$volume); $volume.SetMute($true, [Guid]::Empty); Write-Output 'Muted'"

# Unmute
powershell.exe -Command "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; [Guid(\"5CDF2C82-841E-4546-9722-0CF74078229A\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IAudioEndpointVolume { int _0(); int _1(); int _2(); int _3(); int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext); int _5(); int GetMasterVolumeLevelScalar(out float pfLevel); int SetMute(bool bMute, System.Guid pguidEventContext); int GetMute(out bool pbMute); } [Guid(\"D666063F-1587-4E43-81F1-B948E807363F\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDevice { int Activate(ref System.Guid iid, int dwClsCtx, System.IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface); } [Guid(\"A95664D2-9614-4F35-A746-DE8DB63617E6\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMMDeviceEnumerator { int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppDevice); } [ComImport, Guid(\"BCDE0395-E52F-467C-8E3D-C4579291692E\")] class MMDeviceEnumerator {} '; $enumerator = New-Object MMDeviceEnumerator; $device = $null; $enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device); $iid = [Guid]'5CDF2C82-841E-4546-9722-0CF74078229A'; $volume = $null; $device.Activate([ref]$iid, 1, [IntPtr]::Zero, [ref]$volume); $volume.SetMute($false, [Guid]::Empty); Write-Output 'Unmuted'"
```

### List Audio Devices
```powershell
powershell.exe -Command "Get-CimInstance Win32_SoundDevice | Select-Object Name, Status, Manufacturer | Format-Table -AutoSize"
```

---

## 6. System Info (READ-ONLY)

### Full System Summary
```powershell
powershell.exe -Command "$os = Get-CimInstance Win32_OperatingSystem; $cpu = Get-CimInstance Win32_Processor; $batt = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue; Write-Output '=== OS ==='; Write-Output \"$($os.Caption) $($os.Version) Build $($os.BuildNumber)\"; Write-Output \"Computer: $($os.CSName)\"; Write-Output '=== CPU ==='; Write-Output \"$($cpu.Name)\"; Write-Output \"Cores: $($cpu.NumberOfCores) Logical: $($cpu.NumberOfLogicalProcessors)\"; Write-Output '=== Memory ==='; Write-Output \"Total: $([math]::Round($os.TotalVisibleMemorySize/1MB, 2)) GB\"; Write-Output \"Free: $([math]::Round($os.FreePhysicalMemory/1MB, 2)) GB\"; Write-Output \"Used: $([math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/1MB, 2)) GB\"; Write-Output '=== Uptime ==='; Write-Output \"$((Get-Date) - $os.LastBootUpTime)\"; if ($batt) { Write-Output '=== Battery ==='; Write-Output \"Charge: $($batt.EstimatedChargeRemaining)% Status: $($batt.BatteryStatus)\" }"
```

### Disk Usage
```powershell
powershell.exe -Command "Get-CimInstance Win32_LogicalDisk -Filter \"DriveType=3\" | Select-Object DeviceID, @{N='Size(GB)';E={[math]::Round($_.Size/1GB,2)}}, @{N='Free(GB)';E={[math]::Round($_.FreeSpace/1GB,2)}}, @{N='Used%';E={[math]::Round(($_.Size-$_.FreeSpace)/$_.Size*100,1)}} | Format-Table -AutoSize"
```

### CPU Usage (Snapshot)
```powershell
powershell.exe -Command "Get-CimInstance Win32_Processor | Select-Object Name, LoadPercentage | Format-Table -AutoSize"
```

### Battery Status
```powershell
powershell.exe -Command "$b = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue; if ($b) { Write-Output \"Charge: $($b.EstimatedChargeRemaining)%\"; Write-Output \"Status: $($b.BatteryStatus)\"; Write-Output \"Time Remaining: $($b.EstimatedRunTime) min\" } else { Write-Output 'No battery detected (desktop)' }"
```

### GPU Info
```powershell
powershell.exe -Command "Get-CimInstance Win32_VideoController | Select-Object Name, @{N='VRAM(GB)';E={[math]::Round($_.AdapterRAM/1GB,2)}}, DriverVersion, VideoModeDescription | Format-Table -AutoSize"
```

---

## 7. Network Info (READ-ONLY)

### IP Addresses
```powershell
powershell.exe -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne '127.0.0.1'} | Select-Object InterfaceAlias, IPAddress, PrefixLength | Format-Table -AutoSize"
```

### WiFi Status
```powershell
powershell.exe -Command "netsh wlan show interfaces"
```

### Network Adapters
```powershell
powershell.exe -Command "Get-NetAdapter | Select-Object Name, Status, MacAddress, LinkSpeed | Format-Table -AutoSize"
```

### DNS Servers
```powershell
powershell.exe -Command "Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object {$_.ServerAddresses} | Select-Object InterfaceAlias, ServerAddresses | Format-Table -AutoSize"
```

### Default Gateway
```powershell
powershell.exe -Command "Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object InterfaceAlias, NextHop, RouteMetric | Format-Table -AutoSize"
```

### Public IP Address
```powershell
powershell.exe -Command "(Invoke-RestMethod -Uri 'https://api.ipify.org?format=json' -TimeoutSec 5).ip"
```

### Connection Test
```powershell
powershell.exe -Command "Test-Connection -ComputerName 'google.com' -Count 4 | Select-Object Address, Latency, Status | Format-Table -AutoSize"
```

---

## 8. File/Directory (STRICTLY READ-ONLY)

**WARNING: NEVER use write, delete, move, rename, or create operations on files/directories.**

### List Directory Contents
```powershell
powershell.exe -Command "Get-ChildItem -Path 'C:\Users' | Format-Table Name, LastWriteTime, Length, Mode -AutoSize"
```

### List with Hidden Files
```powershell
powershell.exe -Command "Get-ChildItem -Path 'C:\Users' -Force | Format-Table Name, LastWriteTime, Length, Mode -AutoSize"
```

### List Recursively (One Level)
```powershell
powershell.exe -Command "Get-ChildItem -Path 'C:\Users' -Depth 1 | Select-Object FullName, Length, Mode | Format-Table -AutoSize"
```

### Search Files by Name Pattern
```powershell
powershell.exe -Command "Get-ChildItem -Path 'C:\Users' -Recurse -Filter '*.txt' -ErrorAction SilentlyContinue | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize"
```

### Search Files by Content (grep-like)
```powershell
powershell.exe -Command "Get-ChildItem -Path 'C:\Users\simon\Documents' -Recurse -Filter '*.txt' -ErrorAction SilentlyContinue | Select-String -Pattern 'search term' | Select-Object Path, LineNumber, Line | Format-Table -AutoSize"
```

### Get File Properties
```powershell
powershell.exe -Command "Get-ItemProperty -Path 'C:\path\to\file.txt' | Select-Object FullName, Length, CreationTime, LastWriteTime, LastAccessTime, Attributes"
```

### Get Directory Size
```powershell
powershell.exe -Command "$size = (Get-ChildItem -Path 'C:\Users\simon\Documents' -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; Write-Output \"Size: $([math]::Round($size/1MB, 2)) MB ($([math]::Round($size/1GB, 2)) GB)\""
```

### Get File Hash
```powershell
powershell.exe -Command "Get-FileHash -Path 'C:\path\to\file' -Algorithm SHA256 | Select-Object Algorithm, Hash, Path"
```

### Read File Content (first 50 lines)
```powershell
powershell.exe -Command "Get-Content -Path 'C:\path\to\file.txt' -TotalCount 50"
```

### Count Files by Extension
```powershell
powershell.exe -Command "Get-ChildItem -Path 'C:\Users\simon' -Recurse -File -ErrorAction SilentlyContinue | Group-Object Extension | Sort-Object Count -Descending | Select-Object -First 20 Count, Name | Format-Table -AutoSize"
```

---

## 9. Virtual Desktops

### List Virtual Desktops
```powershell
powershell.exe -Command "Get-CimInstance -Namespace 'root\Microsoft\Windows\DesktopManager' -ClassName 'Win32_VirtualDesktop' -ErrorAction SilentlyContinue | Select-Object Id, Name"
```

### Create New Virtual Desktop (via keyboard shortcut)
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class KeySend { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); public static void KeyDown(byte vk) { keybd_event(vk, 0, 0, UIntPtr.Zero); } public static void KeyUp(byte vk) { keybd_event(vk, 0, 2, UIntPtr.Zero); } }'; [KeySend]::KeyDown(0x5B); [KeySend]::KeyDown(0x11); [KeySend]::KeyDown(0x44); Start-Sleep -Milliseconds 100; [KeySend]::KeyUp(0x44); [KeySend]::KeyUp(0x11); [KeySend]::KeyUp(0x5B); Write-Output 'Created new virtual desktop (Win+Ctrl+D)'"
```

### Switch to Next Virtual Desktop
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class KeySend { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); public static void KeyDown(byte vk) { keybd_event(vk, 0, 0, UIntPtr.Zero); } public static void KeyUp(byte vk) { keybd_event(vk, 0, 2, UIntPtr.Zero); } }'; [KeySend]::KeyDown(0x5B); [KeySend]::KeyDown(0x11); [KeySend]::KeyDown(0x27); Start-Sleep -Milliseconds 100; [KeySend]::KeyUp(0x27); [KeySend]::KeyUp(0x11); [KeySend]::KeyUp(0x5B); Write-Output 'Switched to next desktop (Win+Ctrl+Right)'"
```

### Switch to Previous Virtual Desktop
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class KeySend { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); public static void KeyDown(byte vk) { keybd_event(vk, 0, 0, UIntPtr.Zero); } public static void KeyUp(byte vk) { keybd_event(vk, 0, 2, UIntPtr.Zero); } }'; [KeySend]::KeyDown(0x5B); [KeySend]::KeyDown(0x11); [KeySend]::KeyDown(0x25); Start-Sleep -Milliseconds 100; [KeySend]::KeyUp(0x25); [KeySend]::KeyUp(0x11); [KeySend]::KeyUp(0x5B); Write-Output 'Switched to previous desktop (Win+Ctrl+Left)'"
```

---

## 10. Screenshot

### Full Screen Screenshot
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size); $path = \"$env:TEMP\screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png\"; $bmp.Save($path); $g.Dispose(); $bmp.Dispose(); Write-Output \"Screenshot saved: $path\""
```

### Active Window Screenshot
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Drawing; Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; using System.Drawing; public class WinCapture { [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect); [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; } }'; $hwnd = [WinCapture]::GetForegroundWindow(); $rect = New-Object WinCapture+RECT; [WinCapture]::GetWindowRect($hwnd, [ref]$rect); $w = $rect.Right - $rect.Left; $h = $rect.Bottom - $rect.Top; $bmp = New-Object System.Drawing.Bitmap($w, $h); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size($w, $h))); $path = \"$env:TEMP\window_$(Get-Date -Format 'yyyyMMdd_HHmmss').png\"; $bmp.Save($path); $g.Dispose(); $bmp.Dispose(); Write-Output \"Window screenshot saved: $path\""
```

### Screenshot Specific Region
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Drawing; $x=0; $y=0; $w=800; $h=600; $bmp = New-Object System.Drawing.Bitmap($w, $h); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size($w, $h))); $path = \"$env:TEMP\region_$(Get-Date -Format 'yyyyMMdd_HHmmss').png\"; $bmp.Save($path); $g.Dispose(); $bmp.Dispose(); Write-Output \"Region screenshot saved: $path\""
```

### Multi-Monitor Full Screenshot
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $bounds = [System.Windows.Forms.Screen]::AllScreens | ForEach-Object { $_.Bounds }; $minX = ($bounds | Measure-Object -Property X -Minimum).Minimum; $minY = ($bounds | Measure-Object -Property Y -Minimum).Minimum; $maxX = ($bounds | ForEach-Object { $_.X + $_.Width } | Measure-Object -Maximum).Maximum; $maxY = ($bounds | ForEach-Object { $_.Y + $_.Height } | Measure-Object -Maximum).Maximum; $w = $maxX - $minX; $h = $maxY - $minY; $bmp = New-Object System.Drawing.Bitmap($w, $h); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($minX, $minY, 0, 0, (New-Object System.Drawing.Size($w, $h))); $path = \"$env:TEMP\multimon_$(Get-Date -Format 'yyyyMMdd_HHmmss').png\"; $bmp.Save($path); $g.Dispose(); $bmp.Dispose(); Write-Output \"Multi-monitor screenshot saved: $path\""
```

---

## 11. Power Management

### Lock Screen
```powershell
powershell.exe -Command "rundll32.exe user32.dll,LockWorkStation; Write-Output 'Screen locked'"
```

### Sleep
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Power { [DllImport(\"powrprof.dll\")] public static extern bool SetSuspendState(bool hibernate, bool forceCritical, bool disableWakeEvent); }'; [Power]::SetSuspendState($false, $false, $false); Write-Output 'Sleep initiated'"
```

### Turn Off Monitor
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Monitor { [DllImport(\"user32.dll\")] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam); }'; [Monitor]::SendMessage(0xFFFF, 0x0112, 0xF170, 2); Write-Output 'Monitor off'"
```

**PROHIBITED: `Restart-Computer`, `Stop-Computer`, `shutdown`, `shutdown.exe`**

---

## 12. Notifications

### Send Toast Notification
```powershell
powershell.exe -Command "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null; $template = '<toast><visual><binding template=\"ToastText02\"><text id=\"1\">Title Here</text><text id=\"2\">Message body here</text></binding></visual></toast>'; $xml = New-Object Windows.Data.Xml.Dom.XmlDocument; $xml.LoadXml($template); $toast = [Windows.UI.Notifications.ToastNotification]::new($xml); [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Claude Desktop Control').Show($toast); Write-Output 'Notification sent'"
```

### Fallback: BurntToast Module (if installed)
```powershell
powershell.exe -Command "if (Get-Module -ListAvailable -Name BurntToast) { New-BurntToastNotification -Text 'Title', 'Message body'; Write-Output 'Notification sent via BurntToast' } else { Write-Output 'BurntToast not installed. Use WinRT method or install: Install-Module -Name BurntToast' }"
```

---

## 13. Services (READ-ONLY)

### List All Services
```powershell
powershell.exe -Command "Get-Service | Select-Object Status, Name, DisplayName | Sort-Object Status, Name | Format-Table -AutoSize"
```

### List Running Services
```powershell
powershell.exe -Command "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, DisplayName | Sort-Object Name | Format-Table -AutoSize"
```

### Get Specific Service Status
```powershell
powershell.exe -Command "Get-Service -Name 'wuauserv' | Select-Object Name, DisplayName, Status, StartType"
```

### Search Services by Name
```powershell
powershell.exe -Command "Get-Service | Where-Object {$_.DisplayName -like '*update*'} | Select-Object Status, Name, DisplayName | Format-Table -AutoSize"
```

**PROHIBITED: `Start-Service`, `Stop-Service`, `Set-Service`, `Restart-Service`**

---

## 14. Installed Software (READ-ONLY)

### List Installed Programs (64-bit)
```powershell
powershell.exe -Command "Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where-Object {$_.DisplayName} | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | Sort-Object DisplayName | Format-Table -AutoSize"
```

### List All (32-bit + 64-bit)
```powershell
powershell.exe -Command "$paths = @('HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'); $paths | ForEach-Object { Get-ItemProperty $_ -ErrorAction SilentlyContinue } | Where-Object {$_.DisplayName} | Select-Object DisplayName, DisplayVersion, Publisher | Sort-Object DisplayName -Unique | Format-Table -AutoSize"
```

### Search for Specific Software
```powershell
powershell.exe -Command "$paths = @('HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'); $paths | ForEach-Object { Get-ItemProperty $_ -ErrorAction SilentlyContinue } | Where-Object {$_.DisplayName -like '*chrome*'} | Select-Object DisplayName, DisplayVersion, Publisher | Format-Table -AutoSize"
```

### List UWP/Store Apps
```powershell
powershell.exe -Command "Get-AppxPackage | Select-Object Name, Version, Publisher | Sort-Object Name | Format-Table -AutoSize"
```

---

## 15. Environment Variables (READ-ONLY)

### List All Environment Variables
```powershell
powershell.exe -Command "Get-ChildItem Env: | Sort-Object Name | Format-Table Name, Value -AutoSize -Wrap"
```

### Get Specific Variable
```powershell
powershell.exe -Command "Write-Output $env:PATH"
```

### Get PATH as List
```powershell
powershell.exe -Command "$env:PATH -split ';' | ForEach-Object { Write-Output $_ }"
```

### Show System vs User Variables
```powershell
powershell.exe -Command "Write-Output '=== System Variables ==='; [Environment]::GetEnvironmentVariables('Machine').GetEnumerator() | Sort-Object Name | Format-Table Name, Value -AutoSize -Wrap; Write-Output '=== User Variables ==='; [Environment]::GetEnvironmentVariables('User').GetEnumerator() | Sort-Object Name | Format-Table Name, Value -AutoSize -Wrap"
```

**PROHIBITED: `[Environment]::SetEnvironmentVariable(...)`, `$env:VAR = ...` (persistent)**

---

## 16. Keyboard/Mouse Input

### Send Keystrokes
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('Hello World')"
```

### Send Special Keys
```powershell
# Enter key
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')"

# Tab key
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{TAB}')"

# Escape key
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{ESC}')"
```

### Send Keyboard Shortcut (Ctrl+C)
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^c')"
```

### Send Alt+Tab
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class KeySend { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo); public static void KeyDown(byte vk) { keybd_event(vk, 0, 0, UIntPtr.Zero); } public static void KeyUp(byte vk) { keybd_event(vk, 0, 2, UIntPtr.Zero); } }'; [KeySend]::KeyDown(0x12); [KeySend]::KeyDown(0x09); Start-Sleep -Milliseconds 100; [KeySend]::KeyUp(0x09); [KeySend]::KeyUp(0x12); Write-Output 'Alt+Tab sent'"
```

### Move Mouse to Position
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(500, 300); Write-Output 'Mouse moved to (500, 300)'"
```

### Mouse Click at Current Position
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Mouse { [DllImport(\"user32.dll\")] public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo); }'; [Mouse]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero); [Mouse]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero); Write-Output 'Left click performed'"
```

### Move Mouse and Click
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Mouse { [DllImport(\"user32.dll\")] public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo); }'; [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(500, 300); Start-Sleep -Milliseconds 100; [Mouse]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero); [Mouse]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero); Write-Output 'Clicked at (500, 300)'"
```

### Right Click
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Mouse { [DllImport(\"user32.dll\")] public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo); }'; [Mouse]::mouse_event(0x0008, 0, 0, 0, [UIntPtr]::Zero); [Mouse]::mouse_event(0x0010, 0, 0, 0, [UIntPtr]::Zero); Write-Output 'Right click performed'"
```

### Double Click
```powershell
powershell.exe -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Mouse { [DllImport(\"user32.dll\")] public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo); }'; [Mouse]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero); [Mouse]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 50; [Mouse]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero); [Mouse]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero); Write-Output 'Double click performed'"
```

### Get Current Mouse Position
```powershell
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; $pos = [System.Windows.Forms.Cursor]::Position; Write-Output \"Mouse at: ($($pos.X), $($pos.Y))\""
```

---

## SendKeys Reference

Common `SendKeys` codes for keyboard input:

| Key | Code |
|-----|------|
| Enter | `{ENTER}` |
| Tab | `{TAB}` |
| Escape | `{ESC}` |
| Backspace | `{BS}` |
| Delete | `{DEL}` |
| Arrow Up | `{UP}` |
| Arrow Down | `{DOWN}` |
| Arrow Left | `{LEFT}` |
| Arrow Right | `{RIGHT}` |
| Home | `{HOME}` |
| End | `{END}` |
| Page Up | `{PGUP}` |
| Page Down | `{PGDN}` |
| F1-F12 | `{F1}` to `{F12}` |
| Ctrl + key | `^key` (e.g., `^c` for Ctrl+C) |
| Alt + key | `%key` (e.g., `%{F4}` for Alt+F4) |
| Shift + key | `+key` (e.g., `+{TAB}` for Shift+Tab) |

---

## Virtual Key Codes Reference

Common virtual key codes for `keybd_event`:

| Key | Hex Code |
|-----|----------|
| Left Win | `0x5B` |
| Right Win | `0x5C` |
| Ctrl | `0x11` |
| Alt | `0x12` |
| Shift | `0x10` |
| Tab | `0x09` |
| Enter | `0x0D` |
| Escape | `0x1B` |
| Space | `0x20` |
| Left Arrow | `0x25` |
| Up Arrow | `0x26` |
| Right Arrow | `0x27` |
| Down Arrow | `0x28` |
| D | `0x44` |
| F4 | `0x73` |
