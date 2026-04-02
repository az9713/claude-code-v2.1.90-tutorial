"""
Windows System Health Report Generator
Reads diagnostics JSON from %TEMP%/windows_diagnostics.json and produces a styled HTML report.
No external dependencies — stdlib only.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_diagnostics():
    json_path = os.path.join(os.environ.get("TEMP", "/tmp"), "windows_diagnostics.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run collect_diagnostics.ps1 first.", file=sys.stderr)
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_section(data, name):
    """Safely get a section's data, returning None if error or missing."""
    section = data.get("sections", {}).get(name, {})
    if section.get("status") == "ok":
        return section.get("data", {})
    return None


def safe_list(val):
    """Ensure a value is a list of dicts, handling PowerShell JSON quirks."""
    if val is None:
        return []
    if isinstance(val, dict):
        return [val]  # Single item serialized as dict
    if isinstance(val, list):
        return [x for x in val if isinstance(x, dict)]
    return []


def classify_findings(data):
    """Apply severity rules and return list of findings."""
    findings = []

    def add(category, severity, title, detail="", recommendation=""):
        findings.append({
            "category": category,
            "severity": severity,
            "title": title,
            "detail": detail,
            "recommendation": recommendation,
        })

    # ── Disk ──
    disk = get_section(data, "disk")
    if disk:
        for d in safe_list(disk.get("drives")):
            free_pct = d.get("free_pct", 100)
            drive = d.get("drive", "?")
            if free_pct < 5:
                add("Disk", "CRITICAL", f"Drive {drive} nearly full ({free_pct}% free)",
                    f"Total: {d.get('total_gb')} GB, Free: {d.get('free_gb')} GB",
                    "Run Disk Cleanup, delete large files, uninstall unused programs")
            elif free_pct < 15:
                add("Disk", "WARNING", f"Drive {drive} low on space ({free_pct}% free)",
                    f"Total: {d.get('total_gb')} GB, Free: {d.get('free_gb')} GB",
                    "Plan cleanup soon")
            else:
                add("Disk", "OK", f"Drive {drive} healthy ({free_pct}% free)",
                    f"Total: {d.get('total_gb')} GB, Free: {d.get('free_gb')} GB")

        for pd in safe_list(disk.get("physical")):
            health = pd.get("HealthStatus", "Unknown")
            if health != "Healthy" and health != "Unknown":
                add("Disk", "CRITICAL", f"Disk '{pd.get('FriendlyName')}' health: {health}",
                    recommendation="Back up data immediately and plan drive replacement")
            elif health == "Healthy":
                add("Disk", "OK", f"Disk '{pd.get('FriendlyName')}' healthy")

        large = safe_list(disk.get("large_files"))
        if large:
            file_list = "\n".join(f"  {f.get('FullName')} ({f.get('SizeMB')} MB)" for f in large[:10])
            add("Disk", "INFO", f"{len(large)} large file(s) found (>500MB)", file_list,
                "Review if these files are still needed")

    # ── Memory ──
    mem = get_section(data, "memory")
    if mem:
        used_pct = mem.get("used_pct", 0)
        if used_pct > 95:
            add("Memory", "CRITICAL", f"Memory critically high ({used_pct}% used)",
                f"Used: {mem.get('used_mb')} MB / {mem.get('total_mb')} MB",
                "Close unnecessary applications, check for memory leaks")
        elif used_pct > 85:
            add("Memory", "WARNING", f"Memory usage high ({used_pct}% used)",
                f"Used: {mem.get('used_mb')} MB / {mem.get('total_mb')} MB",
                "Consider closing some applications")
        else:
            add("Memory", "OK", f"Memory usage normal ({used_pct}% used)",
                f"Used: {mem.get('used_mb')} MB / {mem.get('total_mb')} MB")

        top = safe_list(mem.get("top_consumers"))
        if top:
            top_list = ", ".join(f"{p.get('Name')} ({p.get('MemoryMB')} MB)" for p in top[:5])
            add("Memory", "INFO", "Top memory consumers", top_list)

    # ── CPU ──
    cpu = get_section(data, "cpu")
    if cpu:
        proc = cpu.get("processor", {})
        load = 0
        if isinstance(proc, list) and proc:
            load = proc[0].get("LoadPercentage", 0) or 0
        elif isinstance(proc, dict):
            load = proc.get("LoadPercentage", 0) or 0

        if load > 95:
            add("CPU", "CRITICAL", f"CPU load extremely high ({load}%)",
                recommendation="Investigate top processes immediately")
        elif load > 90:
            add("CPU", "WARNING", f"CPU load high ({load}%)",
                recommendation="Check top CPU consumers")
        else:
            add("CPU", "OK", f"CPU load normal ({load}%)")

        top_procs = safe_list(cpu.get("top_processes"))
        if top_procs:
            top_list = ", ".join(f"{p.get('Name')} ({round(p.get('CPU', 0) or 0, 1)}s)" for p in top_procs[:5])
            add("CPU", "INFO", "Top CPU consumers (cumulative time)", top_list)

    # ── Security ──
    sec = get_section(data, "security")
    if sec:
        defender = sec.get("defender")
        if defender:
            if not defender.get("RealTimeProtectionEnabled", True):
                add("Security", "CRITICAL", "Windows Defender real-time protection DISABLED",
                    recommendation="Enable via Windows Security > Virus & threat protection")
            else:
                add("Security", "OK", "Windows Defender real-time protection active")

            if not defender.get("AntivirusEnabled", True):
                add("Security", "CRITICAL", "Antivirus DISABLED",
                    recommendation="Enable antivirus protection immediately")

            sig_date = defender.get("AntivirusSignatureLastUpdated")
            if sig_date:
                try:
                    if isinstance(sig_date, str):
                        sig_dt = datetime.fromisoformat(sig_date.replace("/Date(", "").replace(")/", ""))
                    add("Security", "INFO", f"Antivirus signatures last updated: {sig_date}")
                except Exception:
                    add("Security", "INFO", f"Antivirus signatures last updated: {sig_date}")
        else:
            add("Security", "WARNING", "Could not read Defender status",
                recommendation="Run as administrator to check Defender status")

        updates = safe_list(sec.get("pending_updates"))
        update_count = sec.get("update_count", 0)
        if update_count > 0:
            critical_updates = [u for u in updates if u.get("Severity") == "Critical"]
            if critical_updates:
                titles = "\n".join(f"  - {u.get('Title')}" for u in critical_updates[:5])
                add("Security", "CRITICAL", f"{len(critical_updates)} critical update(s) pending",
                    titles, "Install via Settings > Windows Update immediately")
            else:
                add("Security", "WARNING", f"{update_count} update(s) pending",
                    recommendation="Install via Settings > Windows Update")
        else:
            add("Security", "OK", "No pending Windows updates")

        secure_boot = sec.get("secure_boot")
        if secure_boot is False:
            add("Security", "WARNING", "Secure Boot is DISABLED",
                recommendation="Enable in BIOS/UEFI settings for better security")
        elif secure_boot is True:
            add("Security", "OK", "Secure Boot enabled")

    else:
        add("Security", "WARNING", "Security data unavailable (may require admin)",
            recommendation="Re-run with administrator privileges")

    # ── Network ──
    net = get_section(data, "network")
    if net:
        fw = safe_list(net.get("firewall_profiles"))
        for profile in fw:
            name = profile.get("Name", "Unknown")
            enabled = profile.get("Enabled", True)
            if not enabled:
                add("Network", "CRITICAL", f"Firewall profile '{name}' is DISABLED",
                    recommendation="Enable via Windows Security > Firewall & network protection")
            else:
                add("Network", "OK", f"Firewall profile '{name}' enabled")

        listening = safe_list(net.get("listening_ports"))
        if listening:
            port_list = ", ".join(
                f"{p.get('LocalPort')} ({p.get('ProcessName', 'unknown')})"
                for p in listening[:15]
            )
            add("Network", "INFO", f"{len(listening)} listening port(s)", port_list,
                "Review for any unexpected services")

        connections = net.get("established_connections", [])
        add("Network", "INFO", f"{len(connections)} established connection(s)")

    # ── Startup ──
    startup = get_section(data, "startup")
    if startup:
        total = startup.get("total_startup_items", 0)
        if total > 25:
            add("Startup", "CRITICAL", f"{total} startup items — significantly impacts boot time",
                recommendation="Disable unnecessary startup items via Task Manager > Startup")
        elif total > 15:
            add("Startup", "WARNING", f"{total} startup items — may slow boot time",
                recommendation="Review and disable items you don't need at boot")
        else:
            add("Startup", "OK", f"{total} startup items")

        reg_items = startup.get("registry_entries", [])
        if reg_items:
            # Only flag entries that are actually ENABLED (not disabled via StartupApproved)
            # enabled_names is populated by collect_diagnostics.ps1 from StartupApproved keys
            enabled_names = set(n.lower() for n in startup.get("enabled_startup_names", []))
            # If enabled_names is empty (older script version), fall back to showing all
            use_filter = len(enabled_names) > 0

            heavyweight_keywords = [
                "docker", "lm studio", "lm-studio", "virtualbox", "vmware",
                "ollama", "cuda", "nvidia share", "shadowplay",
                "steam", "epicgames", "origin", "battle.net", "ubisoft",
                "notion", "slack", "teams", "zoom", "webex",
                "spotify", "discord", "telegram", "whatsapp",
                "crashplan", "backblaze", "carbonite",
            ]
            heavy = []
            for r in reg_items:
                name = r.get("Name") or ""
                if use_filter and name.lower() not in enabled_names:
                    continue  # skip disabled entries
                cmd = (r.get("Command") or "").lower()
                if any(kw in cmd or kw in name.lower() for kw in heavyweight_keywords):
                    heavy.append(name)
            if heavy:
                add("Startup", "WARNING",
                    f"{len(heavy)} heavyweight process(es) enabled at startup: {', '.join(heavy)}",
                    "These consume significant RAM/CPU at boot even when not in use",
                    "Disable from Task Manager > Startup apps or remove from HKCU\\...\\Run registry key")

            items_list = "\n".join(f"  - {r.get('Name')}: {r.get('Command', '')[:80]}" for r in reg_items[:15])
            add("Startup", "INFO", f"{len(reg_items)} registry startup entries", items_list)

        tasks = startup.get("scheduled_tasks", [])
        if tasks:
            add("Startup", "INFO", f"{len(tasks)} non-Microsoft scheduled task(s)")

    # ── Services ──
    svc = get_section(data, "services")
    if svc:
        stopped = svc.get("stopped_auto_count", 0)
        if stopped > 10:
            add("Services", "WARNING", f"{stopped} auto-start services are stopped",
                recommendation="Investigate — some may have crashed")
        elif stopped > 0:
            svc_list = "\n".join(
                f"  - {s.get('DisplayName', s.get('Name'))}"
                for s in (svc.get("stopped_auto_services") or [])[:10]
            )
            add("Services", "INFO", f"{stopped} auto-start service(s) stopped", svc_list)
        else:
            add("Services", "OK", "All auto-start services running")

        add("Services", "INFO",
            f"{svc.get('running_count', 0)} / {svc.get('total_count', 0)} services running")

    # ── System ──
    sys_data = get_section(data, "system")
    if sys_data:
        uptime = sys_data.get("uptime_days", 0)
        if uptime > 60:
            add("System", "CRITICAL", f"System uptime: {uptime} days",
                recommendation="Restart urgently to apply pending updates and free resources")
        elif uptime > 30:
            add("System", "WARNING", f"System uptime: {uptime} days",
                recommendation="Consider restarting to apply updates")
        else:
            add("System", "OK", f"System uptime: {uptime} days")

        sys_errors = sys_data.get("system_error_count", 0)
        app_errors = sys_data.get("app_error_count", 0)
        total_errors = sys_errors + app_errors
        if total_errors > 50:
            add("System", "CRITICAL", f"{total_errors} error events in last 7 days",
                recommendation="Investigate recurring error sources in Event Viewer")
        elif total_errors > 20:
            add("System", "WARNING", f"{total_errors} error events in last 7 days",
                recommendation="Check Event Viewer for patterns")
        elif total_errors > 0:
            add("System", "INFO", f"{total_errors} error event(s) in last 7 days")
        else:
            add("System", "OK", "No error events in last 7 days")

        drivers = safe_list(sys_data.get("driver_issues"))
        if drivers:
            driver_list = "\n".join(f"  - {d.get('Name')}" for d in drivers[:10])
            add("System", "WARNING", f"{len(drivers)} driver issue(s) detected", driver_list,
                "Update or reinstall affected drivers via Device Manager")

    # ── Hardware ──
    hw = get_section(data, "hardware")
    if hw:
        battery = hw.get("battery")
        if battery:
            health = battery.get("HealthPercent")
            charge = battery.get("EstimatedChargeRemaining", "?")
            if health is not None:
                if health < 20:
                    add("Hardware", "CRITICAL", f"Battery health critically low ({health}%)",
                        f"Current charge: {charge}%",
                        "Replace battery soon")
                elif health < 50:
                    add("Hardware", "WARNING", f"Battery health degraded ({health}%)",
                        f"Current charge: {charge}%",
                        "Plan battery replacement")
                else:
                    add("Hardware", "OK", f"Battery health good ({health}%)",
                        f"Current charge: {charge}%")
            else:
                add("Hardware", "INFO", f"Battery charge: {charge}%",
                    "Battery health data unavailable")
        else:
            add("Hardware", "INFO", "No battery detected (desktop or data unavailable)")

        gpu = safe_list(hw.get("gpu"))
        for g in gpu:
            driver_date = g.get("DriverDate")
            add("Hardware", "INFO",
                f"GPU: {g.get('Name', 'Unknown')}",
                f"Driver: {g.get('DriverVersion')}, VRAM: {g.get('VRAM_MB', '?')} MB")

    # ── Software ──
    sw = get_section(data, "software")
    if sw:
        add("Software", "INFO", f"{sw.get('program_count', 0)} programs installed")
        add("Software", "INFO", f"{sw.get('appx_count', 0)} AppX packages")

        bloatware_count = sw.get("bloatware_count", 0)
        if bloatware_count > 5:
            bloat_list = "\n".join(f"  - {b.get('Name')}" for b in safe_list(sw.get("bloatware"))[:15])
            add("Software", "WARNING", f"{bloatware_count} bloatware package(s) found",
                bloat_list, "Remove via Settings > Apps or PowerShell")
        elif bloatware_count > 0:
            bloat_list = "\n".join(f"  - {b.get('Name')}" for b in safe_list(sw.get("bloatware")))
            add("Software", "INFO", f"{bloatware_count} bloatware package(s) found",
                bloat_list, "Can be removed via Settings > Apps or PowerShell")

    # ── Error sections ──
    for section_name in data.get("sections", {}):
        section = data["sections"][section_name]
        if section.get("status") == "error":
            add(section_name.title(), "WARNING",
                f"Could not collect {section_name} data: {section.get('error', 'unknown error')}",
                recommendation="Try running with administrator privileges")

    return findings


def compute_score(findings):
    """Compute overall health score (0-100)."""
    if not findings:
        return 100
    severity_weights = {"CRITICAL": 15, "WARNING": 5, "INFO": 0, "OK": 0}
    deductions = sum(severity_weights.get(f["severity"], 0) for f in findings)
    return max(0, 100 - deductions)


def severity_color(severity):
    return {
        "CRITICAL": "#dc3545",
        "WARNING": "#fd7e14",
        "INFO": "#0d6efd",
        "OK": "#198754",
    }.get(severity, "#6c757d")


def severity_bg(severity):
    return {
        "CRITICAL": "#f8d7da",
        "WARNING": "#fff3cd",
        "INFO": "#cfe2ff",
        "OK": "#d1e7dd",
    }.get(severity, "#e2e3e5")


def generate_html(data, findings, score):
    timestamp = data.get("timestamp", datetime.now().isoformat())
    hostname = data.get("hostname", "Unknown")
    is_admin = data.get("is_admin", False)

    counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0, "OK": 0}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    # Score color
    if score >= 80:
        score_color = "#198754"
    elif score >= 60:
        score_color = "#fd7e14"
    else:
        score_color = "#dc3545"

    # Group findings by category
    categories = {}
    for f in findings:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f)

    # Sort categories by worst severity
    severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2, "OK": 3}
    sorted_cats = sorted(categories.items(),
                         key=lambda x: min(severity_order.get(f["severity"], 4) for f in x[1]))

    # Build category sections
    category_html = ""
    for cat_name, cat_findings in sorted_cats:
        worst = min(cat_findings, key=lambda f: severity_order.get(f["severity"], 4))
        worst_severity = worst["severity"]
        border_color = severity_color(worst_severity)

        findings_html = ""
        for f in sorted(cat_findings, key=lambda x: severity_order.get(x["severity"], 4)):
            detail_html = ""
            if f["detail"]:
                detail_html = f'<pre style="margin:8px 0 0 0;padding:8px;background:#f8f9fa;border-radius:4px;font-size:12px;overflow-x:auto;white-space:pre-wrap;">{escape_html(f["detail"])}</pre>'
            rec_html = ""
            if f["recommendation"]:
                rec_html = f'<div style="margin-top:6px;padding:6px 10px;background:#e8f4fd;border-left:3px solid #0d6efd;border-radius:2px;font-size:13px;"><strong>Recommendation:</strong> {escape_html(f["recommendation"])}</div>'

            findings_html += f'''
            <div style="padding:10px 14px;margin:6px 0;background:{severity_bg(f['severity'])};border-left:4px solid {severity_color(f['severity'])};border-radius:4px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="background:{severity_color(f['severity'])};color:white;padding:2px 8px;border-radius:3px;font-size:11px;font-weight:bold;">{f['severity']}</span>
                    <span style="font-weight:500;">{escape_html(f['title'])}</span>
                </div>
                {detail_html}
                {rec_html}
            </div>'''

        category_html += f'''
        <details open style="margin-bottom:16px;">
            <summary style="cursor:pointer;padding:12px 16px;background:white;border:2px solid {border_color};border-radius:8px;font-size:16px;font-weight:600;list-style:none;display:flex;align-items:center;gap:10px;">
                <span style="display:inline-block;width:12px;height:12px;background:{border_color};border-radius:50%;"></span>
                {escape_html(cat_name)}
                <span style="margin-left:auto;font-size:13px;color:#6c757d;">{len(cat_findings)} finding(s)</span>
            </summary>
            <div style="padding:8px 12px;">
                {findings_html}
            </div>
        </details>'''

    # System info
    sys_data = get_section(data, "system")
    os_info = ""
    if sys_data:
        osi = sys_data.get("os_info", {})
        if isinstance(osi, list) and osi:
            osi = osi[0]
        os_info = f"{osi.get('Caption', 'Windows')} (Build {osi.get('BuildNumber', '?')}) {osi.get('OSArchitecture', '')}"

    cpu_data = get_section(data, "cpu")
    cpu_name = ""
    if cpu_data:
        proc = cpu_data.get("processor", {})
        if isinstance(proc, list) and proc:
            proc = proc[0]
        cpu_name = proc.get("Name", "Unknown")

    mem_data = get_section(data, "memory")
    mem_info = ""
    if mem_data:
        mem_info = f"{round(mem_data.get('total_mb', 0) / 1024, 1)} GB RAM"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Health Report — {escape_html(hostname)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; line-height: 1.5; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header .meta {{ font-size: 13px; opacity: 0.8; }}
        .score-ring {{ display: flex; align-items: center; gap: 20px; margin-top: 16px; }}
        .score-number {{ font-size: 48px; font-weight: 700; color: {score_color}; }}
        .score-label {{ font-size: 14px; opacity: 0.9; }}
        .summary-bar {{ display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }}
        .summary-item {{ flex: 1; min-width: 120px; padding: 14px 16px; background: white; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .summary-count {{ font-size: 28px; font-weight: 700; }}
        .summary-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #6c757d; }}
        details > summary {{ user-select: none; }}
        details > summary::-webkit-details-marker {{ display: none; }}
        pre {{ font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #6c757d; }}
        @media print {{
            body {{ background: white; }}
            .container {{ max-width: 100%; }}
            details {{ break-inside: avoid; }}
            details[open] > summary {{ break-after: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>System Health Report</h1>
            <div class="meta">
                <strong>{escape_html(hostname)}</strong> &middot; {escape_html(timestamp[:19])} &middot; {escape_html(os_info)}<br>
                {escape_html(cpu_name)} &middot; {escape_html(mem_info)} &middot; {"Admin" if is_admin else "Standard user (some checks may be limited)"}
            </div>
            <div class="score-ring">
                <div class="score-number">{score}</div>
                <div>
                    <div class="score-label">Health Score</div>
                    <div style="font-size:12px;opacity:0.7;">{"Excellent" if score >= 90 else "Good" if score >= 75 else "Fair" if score >= 60 else "Needs Attention" if score >= 40 else "Critical"}</div>
                </div>
            </div>
        </div>

        <div class="summary-bar">
            <div class="summary-item">
                <div class="summary-count" style="color:{severity_color('CRITICAL')}">{counts['CRITICAL']}</div>
                <div class="summary-label">Critical</div>
            </div>
            <div class="summary-item">
                <div class="summary-count" style="color:{severity_color('WARNING')}">{counts['WARNING']}</div>
                <div class="summary-label">Warning</div>
            </div>
            <div class="summary-item">
                <div class="summary-count" style="color:{severity_color('INFO')}">{counts['INFO']}</div>
                <div class="summary-label">Info</div>
            </div>
            <div class="summary-item">
                <div class="summary-count" style="color:{severity_color('OK')}">{counts['OK']}</div>
                <div class="summary-label">OK</div>
            </div>
        </div>

        {category_html}

        <div class="footer">
            Generated by Windows 360&deg; Diagnostics Skill &middot; {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
    </div>
</body>
</html>'''

    return html


def escape_html(text):
    if text is None:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def main():
    data = load_diagnostics()
    findings = classify_findings(data)
    score = compute_score(findings)
    html = generate_html(data, findings, score)

    # Determine output path — default to current working directory
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = os.path.join(os.getcwd(), f"SystemHealthReport_{date_str}.html")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report saved to: {output_path}")

    # Print summary to stdout
    print(f"\nHealth Score: {score}/100")
    counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0, "OK": 0}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    print(f"CRITICAL: {counts['CRITICAL']} | WARNING: {counts['WARNING']} | INFO: {counts['INFO']} | OK: {counts['OK']}")

    if counts["CRITICAL"] > 0:
        print("\nCRITICAL issues:")
        for f in findings:
            if f["severity"] == "CRITICAL":
                print(f"  - [{f['category']}] {f['title']}")


if __name__ == "__main__":
    main()
