# Remediation Workflows

After diagnosing issues, offer to execute these workflows. Each entry includes both a **UI path** (step-by-step for the user to do themselves) and a **CLI sequence** (commands you can run or paste for them). Always confirm before running destructive actions like uninstalls.

---

## 1. Security: Defender Disabled / Antivirus Gap

**When to use:** Defender real-time protection is OFF and no third-party AV is confirmed active.

### UI Path
1. Open **Windows Security** (search Start menu)
2. Click **Virus & threat protection**
3. Under "Virus & threat protection settings" click **Manage settings**
4. Toggle **Real-time protection** ON
5. If a third-party AV (e.g. Malwarebytes) is active, Windows Defender defers to it automatically — verify Malwarebytes shows "Protected" on its dashboard

### CLI — Check AV status
```powershell
Get-MpComputerStatus | Select-Object -Property RealTimeProtectionEnabled, AntivirusEnabled, AMServiceEnabled, AntispywareEnabled
```

### CLI — Force enable Defender real-time protection
```powershell
Set-MpPreference -DisableRealtimeMonitoring $false
```

### CLI — Check if Malwarebytes service is running
```powershell
Get-Service -Name "MBAMService" | Select-Object Status, StartType
```

### CLI — Verify registered security products
```powershell
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName, productState
```

---

## 2. HP Bloatware: Remove Hanging HP Utilities

**When to use:** Event log shows `HPSystemEventUtilityBackground.exe` hanging, `hp-one-agent-service` timing out, or `HP Display Control Service` MSI install errors repeating on every boot.

### Why this matters
- `hp-one-agent-service` adds ~30 seconds to every boot when it times out waiting for a transaction response
- `HPSystemEventUtilityBackground.exe` hangs and is force-killed by Windows, wasting RAM
- `HP Display Control Service` fails MSI install on every startup (unsupported device), generating noise and consuming CPU

### UI Path — Uninstall via Settings
1. Open **Settings > Apps > Installed apps**
2. Search for and uninstall each of these (only the ones present):
   - **HP Support Assistant** — most bloated, phones home constantly
   - **HP System Event Utility** — the hanging process
   - **myHP** — HP's promotional hub
   - **HP Audio Control** (keep if you use HP's audio presets)
   - **HP Display Control** (keep if you use HP's display color profiles)
   - **HP Smart** (keep if you print via HP printers)

### CLI — List all HP-related installed apps
```powershell
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
                  "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" |
  Where-Object { $_.DisplayName -match "^HP" } |
  Select-Object DisplayName, DisplayVersion |
  Sort-Object DisplayName
```

### CLI — Remove HP AppX packages (OEM bloat)
```powershell
# List HP AppX packages
Get-AppxPackage | Where-Object { $_.Name -match "AD2F1837" } | Select-Object Name, Version

# Remove each (run separately, confirm before executing)
Get-AppxPackage -Name "AD2F1837.HPPrinterControl" | Remove-AppxPackage
Get-AppxPackage -Name "AD2F1837.myHP" | Remove-AppxPackage
Get-AppxPackage -Name "AD2F1837.BOAudioControl" | Remove-AppxPackage
```

### CLI — Stop and disable hp-one-agent-service
```powershell
Stop-Service -Name "hp-one-agent-service" -Force -ErrorAction SilentlyContinue
Set-Service -Name "hp-one-agent-service" -StartupType Disabled
```

### CLI — Stop HP Display Control from installing at every boot
The MSI installer is triggered by a scheduled task. List and disable it:
```powershell
# Find the task
Get-ScheduledTask | Where-Object { $_.TaskName -match "HP" } | Select-Object TaskName, State

# Disable a specific task (replace TaskName as found above)
Disable-ScheduledTask -TaskName "HPDisplayControlInstall" -ErrorAction SilentlyContinue
```

---

## 3. Startup Programs: Reduce Boot Load

**When to use:** More than 15 startup items detected.

### UI Path
1. Right-click taskbar > **Task Manager** (or `Ctrl+Shift+Esc`)
2. Click **Startup apps** tab
3. Sort by **Startup impact** (High first)
4. Right-click any non-essential app > **Disable**

**Safe to disable (generally):**
- Microsoft Teams (launches on demand when you open it)
- OneDrive (starts sync when needed; can re-enable if you need instant sync)
- Xbox Game Bar / Xbox services
- Microsoft Copilot
- Spotify
- Discord (if not always-on)
- HP utilities (any remaining)
- Adobe updaters
- Slack (if not always-on)

**Keep enabled:**
- Windows Security / Defender
- Your VPN client (if used daily)
- Bluetooth/audio drivers
- Malwarebytes tray

### CLI — List all startup items with their status
```powershell
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Sort-Object Name
```

### CLI — List startup items via registry (more complete)
```powershell
$paths = @(
  "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
  "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
)
foreach ($p in $paths) {
  Get-ItemProperty $p | Select-Object -Property * -ExcludeProperty PS* |
    Get-Member -MemberType NoteProperty |
    ForEach-Object { [PSCustomObject]@{Key=$_.Name; Path=$p} }
}
```

### CLI — Disable a specific startup registry entry (HKCU, no admin needed)
```powershell
# Example: disable OneDrive from running at startup
Remove-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "OneDrive" -ErrorAction SilentlyContinue
```

### CLI — Disable a startup task via Task Scheduler
```powershell
# Example: Teams
Disable-ScheduledTask -TaskName "TeamsMachineUninstallerLocalAppData" -ErrorAction SilentlyContinue
```

---

## 4. Memory Pressure: Free Up RAM

**When to use:** RAM usage consistently above 85%.

### UI Path — Find memory hogs
1. Open **Task Manager** (`Ctrl+Shift+Esc`)
2. Click **Processes** tab
3. Click **Memory** column header to sort descending
4. Close any apps you don't need
5. For Chrome: right-click its entry > **End task** on individual tabs (or use Chrome's built-in Memory Saver: Settings > Performance > Memory Saver)

### CLI — Show top 15 processes by RAM
```powershell
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 15 Name, Id,
  @{N="RAM_MB";E={[math]::Round($_.WorkingSet64/1MB,1)}} | Format-Table -AutoSize
```

### CLI — Show total and available memory
```powershell
$os = Get-CimInstance Win32_OperatingSystem
[PSCustomObject]@{
  Total_GB   = [math]::Round($os.TotalVisibleMemorySize/1MB, 2)
  Free_GB    = [math]::Round($os.FreePhysicalMemory/1MB, 2)
  Used_Pct   = [math]::Round((1 - $os.FreePhysicalMemory/$os.TotalVisibleMemorySize)*100, 1)
}
```

### CLI — Enable Chrome Memory Saver via registry (if Edge/Chrome is the offender)
```powershell
# For Chrome — set tab discarding (Memory Saver) via policy
# This requires admin and creates a policy key
New-Item -Path "HKLM:\SOFTWARE\Policies\Google\Chrome" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Google\Chrome" -Name "TabDiscardingEnabled" -Value 1
```

### CLI — Clear standby memory (flushes file cache — safe, instant effect)
```powershell
# Requires admin. Uses RAMMap-style empty working set.
# Native approach: use EmptyWorkingSet on svchost
$processes = Get-Process | Where-Object { $_.WorkingSet64 -gt 100MB -and $_.Name -ne "System" }
foreach ($p in $processes) {
  try { [System.Diagnostics.Process]::GetProcessById($p.Id).MinWorkingSet = [System.IntPtr]::Zero } catch {}
}
```

---

## 5. Disk Cleanup: Free Up Space

**When to use:** System drive free space below 15%.

### UI Path
1. Press `Win+R`, type `cleanmgr`, press Enter
2. Select drive C:, click OK
3. Check all boxes (especially: **Temporary files**, **Recycle Bin**, **Thumbnails**, **Windows Update Cleanup**)
4. Click **Clean up system files** for deeper cleanup (requires admin)
5. Also check: **Settings > System > Storage > Temporary files**

### CLI — Run Disk Cleanup silently (all safe categories)
```powershell
# Set all standard cleanup flags
$regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches"
$categories = @("Temporary Files","Recycle Bin","Thumbnails","Downloaded Program Files","Temporary Internet Files","Old ChkDsk Files")
foreach ($cat in $categories) {
  $key = Join-Path $regPath $cat
  if (Test-Path $key) { Set-ItemProperty -Path $key -Name "StateFlags0064" -Value 2 -Type DWord }
}
# Run cleanmgr with those flags
Start-Process cleanmgr -ArgumentList "/sagerun:64" -Wait
```

### CLI — Find largest files in common locations
```powershell
$paths = @("$env:USERPROFILE\Downloads", "$env:USERPROFILE\Documents",
           "$env:USERPROFILE\Desktop", "$env:USERPROFILE\Videos")
Get-ChildItem -Path $paths -Recurse -File -ErrorAction SilentlyContinue |
  Sort-Object Length -Descending | Select-Object -First 20
  FullName, @{N="Size_MB";E={[math]::Round($_.Length/1MB,1)}} | Format-Table -AutoSize
```

### CLI — Check what's eating the most space (top folders)
```powershell
Get-ChildItem C:\ -Directory -ErrorAction SilentlyContinue | ForEach-Object {
  $size = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
    Measure-Object Length -Sum).Sum
  [PSCustomObject]@{Folder=$_.Name; Size_GB=[math]::Round($size/1GB,2)}
} | Sort-Object Size_GB -Descending | Select-Object -First 10
```

### CLI — Delete Windows Update cache (requires admin, frees significant space)
```powershell
Stop-Service wuauserv -Force
Remove-Item "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service wuauserv
Write-Host "Windows Update download cache cleared."
```

### CLI — Empty Recycle Bin
```powershell
Clear-RecycleBin -Force -ErrorAction SilentlyContinue
```

### CLI — Delete temp files
```powershell
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## 6. Startup Errors: Stop HP Display Control MSI from Repeating

**When to use:** Event log shows repeated `HP Display Control Service` MSI install failures (Event IDs 1013, 10005) at every boot.

This is HP attempting to reinstall a service that is incompatible with this device. It generates errors every boot and wastes resources.

### CLI — Find and disable the triggering scheduled task
```powershell
# Find HP-related scheduled tasks
Get-ScheduledTask | Where-Object { $_.TaskName -match "HP|hpone|HPDisplay" } |
  Select-Object TaskName, TaskPath, State

# Disable whichever task triggers the installer (adjust TaskName/TaskPath as found):
Disable-ScheduledTask -TaskPath "\HP\" -TaskName "HP*" -ErrorAction SilentlyContinue
```

### CLI — Remove HP Display Control via winget (if available)
```powershell
winget uninstall --name "HP Display Control" --silent
```

### CLI — Remove HP Display Control via msiexec (if above fails)
```powershell
# Get the product code
$prod = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" |
  Where-Object { $_.DisplayName -match "HP Display" } | Select-Object PSChildName, DisplayName
$prod
# Then uninstall:
# Start-Process msiexec -ArgumentList "/x $($prod.PSChildName) /qn" -Wait
```

---

## 7. System Errors: Secure Boot SBAT Update Failing

**When to use:** Repeated Event ID 1796 from `Microsoft-Windows-TPM-WMI` — "Secure Boot update failed to update SBAT".

This is a UEFI firmware issue, not a Windows issue. The fix is a BIOS update.

### UI Path
1. Open **HP Support Assistant** (if still installed) and check for BIOS/firmware updates
2. Or go to **support.hp.com**, enter your model number, and download the latest BIOS update
3. BIOS updates from HP come as `.exe` files that install automatically and reboot

### CLI — Check current BIOS version and date
```powershell
Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate
```

### CLI — Check your HP model for the download
```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, SystemSKUNumber
```

---

## 8. General Performance Tune-Up (Full Workflow)

Run this sequence as a standard tune-up to address sluggishness without a full diagnostic.

```powershell
# ── 1. Show top RAM consumers
Write-Host "`n=== TOP RAM CONSUMERS ===" -ForegroundColor Cyan
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name,
  @{N="RAM_MB";E={[math]::Round($_.WorkingSet64/1MB,1)}} | Format-Table -AutoSize

# ── 2. Show top CPU consumers
Write-Host "`n=== TOP CPU CONSUMERS ===" -ForegroundColor Cyan
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, Id,
  @{N="CPU_s";E={[math]::Round($_.CPU,1)}} | Format-Table -AutoSize

# ── 3. Disk free space summary
Write-Host "`n=== DISK SPACE ===" -ForegroundColor Cyan
Get-PSDrive -PSProvider FileSystem | Select-Object Name,
  @{N="Used_GB";E={[math]::Round(($_.Used/1GB),1)}},
  @{N="Free_GB";E={[math]::Round(($_.Free/1GB),1)}},
  @{N="Free_Pct";E={if($_.Used+$_.Free -gt 0){[math]::Round(($_.Free/($_.Used+$_.Free)*100),1)}else{"N/A"}}}

# ── 4. Memory summary
Write-Host "`n=== MEMORY ===" -ForegroundColor Cyan
$os = Get-CimInstance Win32_OperatingSystem
[PSCustomObject]@{
  Total_GB = [math]::Round($os.TotalVisibleMemorySize/1MB, 2)
  Free_GB  = [math]::Round($os.FreePhysicalMemory/1MB, 2)
  Used_Pct = "$([math]::Round((1 - $os.FreePhysicalMemory/$os.TotalVisibleMemorySize)*100,1))%"
} | Format-List

# ── 5. Startup program count
Write-Host "`n=== STARTUP ITEMS ===" -ForegroundColor Cyan
$startupCount = (Get-CimInstance Win32_StartupCommand).Count
Write-Host "$startupCount startup items registered"

# ── 6. Quick temp cleanup
Write-Host "`n=== CLEANING TEMP FILES ===" -ForegroundColor Cyan
$before = (Get-ChildItem $env:TEMP -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
$after = (Get-ChildItem $env:TEMP -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
Write-Host "Freed: $([math]::Round(($before-$after)/1MB,1)) MB from user temp"

Write-Host "`nDone. Restart recommended if many changes were made." -ForegroundColor Green
```

---

## Workflow Selection Guide

| Finding | Workflow to Use |
|---|---|
| Defender/AV disabled | §1 Security |
| HP processes hanging/timing out | §2 HP Bloatware |
| >15 startup items | §3 Startup Programs |
| RAM >85% used | §4 Memory Pressure |
| Disk <15% free | §5 Disk Cleanup |
| HP Display Control MSI errors in event log | §6 HP Display Control |
| Secure Boot SBAT errors in event log | §7 BIOS Update |
| General sluggishness (no specific finding) | §8 General Tune-Up |
