# Severity Classification Rules

These rules determine how diagnostic findings are classified. Use them when interpreting results and presenting recommendations.

## Severity Levels

- **CRITICAL** — Immediate action required. System security or stability at risk.
- **WARNING** — Should be addressed soon. Performance or reliability impact.
- **INFO** — Awareness item. Optimization opportunity, no immediate risk.
- **OK** — Healthy. No action needed.

## Rules by Category

### Disk
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| Free space < 5% | CRITICAL | Run Disk Cleanup, delete large files, uninstall unused programs |
| Free space 5-15% | WARNING | Plan cleanup soon, check large files list |
| Free space > 15% | OK | — |
| HealthStatus != Healthy | CRITICAL | Back up data immediately, plan drive replacement |
| Large files found (>500MB) | INFO | Review if these files are still needed |

### Security
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| Defender RealTimeProtection off | CRITICAL | Enable via Windows Security > Virus & threat protection |
| Any firewall profile disabled | CRITICAL | Enable via Windows Security > Firewall & network protection |
| Critical pending updates | CRITICAL | Install via Settings > Windows Update immediately |
| Non-critical pending updates | WARNING | Install at next convenient time |
| Antivirus signatures > 7 days old | WARNING | Force update via Windows Security |
| Secure Boot disabled | WARNING | Enable in BIOS/UEFI settings |
| Accounts without passwords | WARNING | Set passwords for all accounts |

### CPU
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| Load > 90% | WARNING | Check top processes, kill or investigate runaway processes |
| Load > 95% sustained | CRITICAL | System likely unresponsive, investigate immediately |
| Load < 90% | OK | — |

### Memory
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| Used > 95% | CRITICAL | Close unnecessary apps, check for memory leaks |
| Used 85-95% | WARNING | Consider closing some applications |
| Used < 85% | OK | — |
| Page file heavily used | WARNING | May indicate insufficient RAM |

### Startup
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| > 25 startup items | CRITICAL | Significantly impacts boot time, disable unnecessary items |
| 15-25 startup items | WARNING | Review and disable items you don't need at boot |
| < 15 startup items | OK | — |

### Services
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| > 10 auto-start services stopped | WARNING | Some services may have crashed, investigate |
| 1-10 auto-start services stopped | INFO | Normal for some services, check if any are important |
| 0 stopped | OK | — |

### System
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| Uptime > 30 days | WARNING | Restart to apply pending updates and free resources |
| Uptime > 60 days | CRITICAL | Restart urgently — many updates likely pending |
| > 20 error events in 7 days | WARNING | Investigate recurring error sources |
| > 50 error events in 7 days | CRITICAL | Significant system instability |
| Driver issues found | WARNING | Update or reinstall affected drivers |

### Hardware
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| Battery health < 20% | CRITICAL | Replace battery soon |
| Battery health 20-50% | WARNING | Battery degrading, plan replacement |
| Battery health > 50% | OK | — |
| GPU driver > 1 year old | INFO | Consider updating for performance/security |

### Software
| Condition | Severity | Recommendation |
|-----------|----------|----------------|
| Known bloatware found | INFO | Can be removed via Settings > Apps or PowerShell |
| > 5 bloatware apps | WARNING | Consider cleanup to free resources |
