# Windows 360° System Diagnostics Collector
# Outputs structured JSON covering 10 diagnostic categories
# Uses parallel background jobs for slow operations to minimize total runtime

$ErrorActionPreference = 'Continue'

$report = @{
    timestamp = (Get-Date -Format 'o')
    hostname  = $env:COMPUTERNAME
    username  = $env:USERNAME
    is_admin  = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    sections  = @{}
}

# ── Launch slow operations as parallel background jobs ──────────────────────────
# These are the bottleneck operations (10-50s each). Running them in parallel
# cuts total time from ~2.5min to ~50s.

$jobPhysDisk = Start-Job -ScriptBlock {
    try { Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus, OperationalStatus, @{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}} } catch { @() }
}

$jobFirewall = Start-Job -ScriptBlock {
    try { Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction } catch { @() }
}

$jobDefender = Start-Job -ScriptBlock {
    try { Get-MpComputerStatus | Select-Object AMRunningMode, AntivirusEnabled, RealTimeProtectionEnabled, AntispywareEnabled, AntivirusSignatureLastUpdated, QuickScanEndTime, FullScanEndTime } catch { $null }
}

$jobNetConn = Start-Job -ScriptBlock {
    try {
        $conns = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | Select-Object -First 30 LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess | ForEach-Object {
            $procName = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name
            $_ | Add-Member -NotePropertyName ProcessName -NotePropertyValue $procName -PassThru
        }
        $listen = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object -First 30 LocalAddress, LocalPort, OwningProcess | ForEach-Object {
            $procName = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name
            $_ | Add-Member -NotePropertyName ProcessName -NotePropertyValue $procName -PassThru
        }
        @{ established = $conns; listening = $listen }
    } catch { @{ established = @(); listening = @() } }
}

$jobUpdates = Start-Job -ScriptBlock {
    try {
        $session = New-Object -ComObject Microsoft.Update.Session
        $searcher = $session.CreateUpdateSearcher()
        $results = $searcher.Search("IsInstalled=0")
        @($results.Updates | ForEach-Object {
            [PSCustomObject]@{ Title = $_.Title; Severity = $_.MsrcSeverity; IsDownloaded = $_.IsDownloaded }
        })
    } catch { @() }
}

$jobCpu = Start-Job -ScriptBlock {
    try { Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, LoadPercentage } catch { $null }
}

# ── Fast sequential operations (run while jobs are pending) ─────────────────────

# ── Memory (8s) ──
try {
    $os = Get-CimInstance Win32_OperatingSystem
    $totalMB = [math]::Round($os.TotalVisibleMemorySize / 1024, 0)
    $freeMB  = [math]::Round($os.FreePhysicalMemory / 1024, 0)
    $usedMB  = $totalMB - $freeMB
    $usedPct = [math]::Round(($usedMB / $totalMB) * 100, 1)
    $pageFile = Get-CimInstance Win32_PageFileUsage -ErrorAction SilentlyContinue | Select-Object Name, AllocatedBaseSize, CurrentUsage, PeakUsage
    $topMem = Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name, Id, @{N='MemoryMB';E={[math]::Round($_.WorkingSet64/1MB,1)}}
    $report.sections['memory'] = @{ status = 'ok'; data = @{
        total_mb = $totalMB; free_mb = $freeMB; used_mb = $usedMB; used_pct = $usedPct
        page_file = $pageFile; top_consumers = $topMem
    }}
} catch { $report.sections['memory'] = @{ status = 'error'; error = $_.Exception.Message } }

# ── Disk space + large files (5s) ──
try {
    $drives = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
        $totalGB = [math]::Round($_.Size / 1GB, 2)
        $freeGB  = [math]::Round($_.FreeSpace / 1GB, 2)
        $usedGB  = [math]::Round(($_.Size - $_.FreeSpace) / 1GB, 2)
        $freePct = if ($_.Size -gt 0) { [math]::Round(($_.FreeSpace / $_.Size) * 100, 1) } else { 0 }
        [PSCustomObject]@{ drive = $_.DeviceID; total_gb = $totalGB; free_gb = $freeGB; used_gb = $usedGB; free_pct = $freePct; filesystem = $_.FileSystem }
    }
    $largeFiles = @()
    foreach ($dir in @("$env:USERPROFILE\Desktop","$env:USERPROFILE\Documents","$env:USERPROFILE\Downloads","$env:USERPROFILE\Videos")) {
        if (Test-Path $dir) {
            $largeFiles += Get-ChildItem -Path $dir -Depth 3 -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Length -gt 500MB -and $_.FullName -notmatch '(node_modules|\.git|\.venv)' } |
                Select-Object FullName, @{N='SizeMB';E={[math]::Round($_.Length/1MB,1)}}
        }
    }
    $largeFiles = $largeFiles | Sort-Object SizeMB -Descending | Select-Object -First 20
    # Physical disk data will be merged from job later
    $report.sections['disk'] = @{ status = 'ok'; data = @{ drives = $drives; physical = @(); large_files = $largeFiles } }
} catch { $report.sections['disk'] = @{ status = 'error'; error = $_.Exception.Message } }

# ── Services (5s) ──
try {
    $allSvc = Get-Service
    $stoppedAuto = $allSvc | Where-Object { $_.StartType -eq 'Automatic' -and $_.Status -ne 'Running' } | Select-Object Name, DisplayName, Status, StartType
    $runningCount = ($allSvc | Where-Object { $_.Status -eq 'Running' }).Count
    $report.sections['services'] = @{ status = 'ok'; data = @{
        stopped_auto_services = $stoppedAuto; stopped_auto_count = @($stoppedAuto).Count
        running_count = $runningCount; total_count = $allSvc.Count
    }}
} catch { $report.sections['services'] = @{ status = 'error'; error = $_.Exception.Message } }

# ── Startup (6s) ──
try {
    $regStartup = @()
    foreach ($path in @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run','HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run','HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce','HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce')) {
        try {
            $items = Get-ItemProperty $path -ErrorAction SilentlyContinue
            if ($items) {
                $items.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                    $regStartup += [PSCustomObject]@{ Name = $_.Name; Command = $_.Value; Location = $path }
                }
            }
        } catch {}
    }
    $startupFolders = @()
    foreach ($fp in @("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup","C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup")) {
        if (Test-Path $fp) { $startupFolders += Get-ChildItem $fp -ErrorAction SilentlyContinue | Select-Object Name, FullName }
    }
    $tasks = @()
    try { $tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { $_.State -ne 'Disabled' -and $_.TaskPath -notmatch '\\Microsoft\\' } | Select-Object -First 30 TaskName, TaskPath, State, Author } catch {}
    # Read StartupApproved to know which entries are actually enabled vs disabled by Task Manager
    $enabledNames = @()
    foreach ($approvedPath in @('HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run','HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run')) {
        try {
            $approved = Get-ItemProperty $approvedPath -ErrorAction SilentlyContinue
            if ($approved) {
                $approved.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                    # Value is binary; first byte 02 = enabled, 03 = disabled
                    $firstByte = $_.Value[0]
                    if ($firstByte -eq 2) { $enabledNames += $_.Name }
                }
            }
        } catch {}
    }
    $report.sections['startup'] = @{ status = 'ok'; data = @{
        registry_entries = $regStartup; startup_folders = $startupFolders; scheduled_tasks = $tasks
        total_startup_items = $regStartup.Count + $startupFolders.Count
        enabled_startup_names = $enabledNames
    }}
} catch { $report.sections['startup'] = @{ status = 'error'; error = $_.Exception.Message } }

# ── System (3s) ──
try {
    $osInfo = Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture, LastBootUpTime, InstallDate
    $uptime = (Get-Date) - $osInfo.LastBootUpTime
    $sysErrors = @(); $appErrors = @()
    try { $sysErrors = Get-WinEvent -FilterHashtable @{LogName='System';Level=2;StartTime=(Get-Date).AddDays(-7)} -MaxEvents 20 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, ProviderName, @{N='Message';E={$_.Message.Substring(0,[Math]::Min($_.Message.Length,200))}} } catch {}
    try { $appErrors = Get-WinEvent -FilterHashtable @{LogName='Application';Level=2;StartTime=(Get-Date).AddDays(-7)} -MaxEvents 20 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, ProviderName, @{N='Message';E={$_.Message.Substring(0,[Math]::Min($_.Message.Length,200))}} } catch {}
    $driverIssues = @()
    try { $driverIssues = Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue | Where-Object { $_.ConfigManagerErrorCode -ne 0 } | Select-Object Name, DeviceID, ConfigManagerErrorCode } catch {}
    $bios = Get-CimInstance Win32_BIOS -ErrorAction SilentlyContinue | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate
    $report.sections['system'] = @{ status = 'ok'; data = @{
        os_info = $osInfo; uptime_days = [math]::Round($uptime.TotalDays,1)
        system_errors = $sysErrors; app_errors = $appErrors
        system_error_count = @($sysErrors).Count; app_error_count = @($appErrors).Count
        driver_issues = $driverIssues; bios = $bios
    }}
} catch { $report.sections['system'] = @{ status = 'error'; error = $_.Exception.Message } }

# ── Hardware (fast parts) ──
try {
    $battery = $null
    try {
        $battery = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | Select-Object Name, Status, EstimatedChargeRemaining, BatteryStatus, DesignCapacity, FullChargeCapacity
        if ($battery -and $battery.DesignCapacity -gt 0 -and $battery.FullChargeCapacity -gt 0) {
            $battery | Add-Member -NotePropertyName HealthPercent -NotePropertyValue ([math]::Round(($battery.FullChargeCapacity / $battery.DesignCapacity) * 100, 1)) -Force
        }
    } catch {}
    $gpu = @()
    try { $gpu = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue | Select-Object Name, DriverVersion, DriverDate, @{N='VRAM_MB';E={[math]::Round($_.AdapterRAM/1MB,0)}}, Status } catch {}
    $thermal = @()
    try { $thermal = Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace 'root/wmi' -ErrorAction SilentlyContinue | ForEach-Object { [PSCustomObject]@{ Zone=$_.InstanceName; TempCelsius=[math]::Round(($_.CurrentTemperature-2732)/10,1) } } } catch {}
    $powerPlan = $null
    try { $powerPlan = powercfg /getactivescheme 2>$null } catch {}
    $report.sections['hardware'] = @{ status = 'ok'; data = @{ battery=$battery; gpu=$gpu; thermal=$thermal; power_plan=$powerPlan } }
} catch { $report.sections['hardware'] = @{ status = 'error'; error = $_.Exception.Message } }

# ── Software (1s) ──
try {
    $programs = @()
    foreach ($path in @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*')) {
        try { $programs += Get-ItemProperty $path -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName } | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate } catch {}
    }
    $programs = $programs | Sort-Object DisplayName -Unique
    $appx = @()
    try { $appx = Get-AppxPackage -ErrorAction SilentlyContinue | Where-Object { $_.Name -notmatch '^(Microsoft\.(Windows\.|NET\.|VCLibs|UI\.|DesktopAppInstaller|WindowsStore|StorePurchaseApp)|windows\.)' } | Select-Object Name, Version, NonRemovable | Sort-Object Name } catch {}
    $bloatwarePatterns = 'CandyCrush|Facebook|Twitter|TikTok|Netflix|Spotify|Disney|LinkedIn|Clipchamp|BingNews|BingWeather|BingFinance|GetHelp|Getstarted|MicrosoftOfficeHub|MicrosoftSolitaire|MixedReality|OneConnect|People|SkypeApp|Todos|ZuneMusic|ZuneVideo|Xbox|Gamebar'
    $foundBloatware = @()
    try { $foundBloatware = Get-AppxPackage -ErrorAction SilentlyContinue | Where-Object { $_.Name -match $bloatwarePatterns } | Select-Object Name, @{N='NonRemovable';E={$_.NonRemovable}} } catch {}
    $report.sections['software'] = @{ status = 'ok'; data = @{
        installed_programs=$programs; program_count=$programs.Count; appx_packages=$appx; appx_count=$appx.Count
        bloatware=$foundBloatware; bloatware_count=@($foundBloatware).Count
    }}
} catch { $report.sections['software'] = @{ status = 'error'; error = $_.Exception.Message } }

# ── Collect results from parallel jobs (with timeouts) ──────────────────────────
$jobTimeout = 30

# CPU
$cpuResult = $null
if (Wait-Job $jobCpu -Timeout $jobTimeout) { $cpuResult = Receive-Job $jobCpu }
Remove-Job $jobCpu -Force -ErrorAction SilentlyContinue
try {
    $topProcs = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, Id, CPU, @{N='MemoryMB';E={[math]::Round($_.WorkingSet64/1MB,1)}}
    $report.sections['cpu'] = @{ status = 'ok'; data = @{ processor = $cpuResult; top_processes = $topProcs } }
} catch { $report.sections['cpu'] = @{ status = 'error'; error = $_.Exception.Message } }

# Physical disk → merge into disk section
$physResult = @()
if (Wait-Job $jobPhysDisk -Timeout $jobTimeout) { $physResult = @(Receive-Job $jobPhysDisk) }
Remove-Job $jobPhysDisk -Force -ErrorAction SilentlyContinue
if ($report.sections['disk'].status -eq 'ok') { $report.sections['disk'].data.physical = $physResult }

# Firewall → merge into network section
$fwResult = @()
if (Wait-Job $jobFirewall -Timeout $jobTimeout) { $fwResult = @(Receive-Job $jobFirewall) }
Remove-Job $jobFirewall -Force -ErrorAction SilentlyContinue

# Network connections
$netResult = @{ established = @(); listening = @() }
if (Wait-Job $jobNetConn -Timeout $jobTimeout) { $netResult = Receive-Job $jobNetConn }
Remove-Job $jobNetConn -Force -ErrorAction SilentlyContinue

$adapters = @()
try { $adapters = Get-NetAdapter -ErrorAction SilentlyContinue | Select-Object Name, Status, LinkSpeed, MacAddress } catch {}

$report.sections['network'] = @{ status = 'ok'; data = @{
    established_connections = $netResult.established; listening_ports = $netResult.listening
    firewall_profiles = $fwResult; adapters = $adapters
}}

# Defender + Updates → security section
$defenderResult = $null
if (Wait-Job $jobDefender -Timeout $jobTimeout) { $defenderResult = Receive-Job $jobDefender }
Remove-Job $jobDefender -Force -ErrorAction SilentlyContinue

$pendingUpdates = @()
if (Wait-Job $jobUpdates -Timeout 20) { $pendingUpdates = @(Receive-Job $jobUpdates) }
Remove-Job $jobUpdates -Force -ErrorAction SilentlyContinue

$users = @()
try { $users = Get-LocalUser -ErrorAction SilentlyContinue | Select-Object Name, Enabled, LastLogon, PasswordRequired, PasswordExpires } catch {}
$secureBoot = $null
try { $secureBoot = Confirm-SecureBootUEFI -ErrorAction SilentlyContinue } catch {}

$report.sections['security'] = @{ status = 'ok'; data = @{
    defender = $defenderResult; pending_updates = $pendingUpdates; update_count = $pendingUpdates.Count
    users = $users; secure_boot = $secureBoot
}}

# ── Output ──────────────────────────────────────────────────────────────────────
$json = $report | ConvertTo-Json -Depth 6 -Compress
$tempPath = Join-Path $env:TEMP 'windows_diagnostics.json'
[System.IO.File]::WriteAllText($tempPath, $json, [System.Text.UTF8Encoding]::new($false))
Write-Output $json
