# Known Bloatware / Unnecessary AppX Packages

Pre-installed packages commonly considered bloatware on Windows 10/11. These consume resources and can be safely removed.

## Safe to Remove

### Games & Entertainment
- `Microsoft.XboxApp` / `Microsoft.Xbox*` — Xbox companion apps (unless you game on PC)
- `Microsoft.ZuneMusic` — Groove Music (replaced by Media Player)
- `Microsoft.ZuneVideo` — Movies & TV
- `Microsoft.MicrosoftSolitaireCollection` — Solitaire (contains ads)
- `Microsoft.GamingApp` — Xbox Game Bar launcher
- `king.com.CandyCrushSaga` / `king.com.CandyCrush*` — Candy Crush (ad-installed)
- `Disney.*` — Disney+ promotional app
- `SpotifyAB.SpotifyMusic` — Spotify (if not used)

### Social & Communication
- `Microsoft.SkypeApp` — Skype (if not used)
- `Microsoft.People` — People app
- `Microsoft.LinkedIn*` — LinkedIn promotional app
- `BytedancePte.Ltd.TikTok` — TikTok
- `Facebook.*` / `Meta.*` — Facebook/Instagram

### News & Info
- `Microsoft.BingNews` — Bing News
- `Microsoft.BingWeather` — Bing Weather
- `Microsoft.BingFinance` — Bing Finance / Money
- `Microsoft.GetHelp` — Get Help app
- `Microsoft.Getstarted` — Tips app

### Productivity (if not used)
- `Clipchamp.Clipchamp` — Video editor (if not used)
- `Microsoft.MicrosoftOfficeHub` — Office hub (if you have Office installed separately)
- `Microsoft.Todos` — Microsoft To Do (if not used)
- `Microsoft.OneConnect` — Mobile Plans
- `Microsoft.MixedReality.Portal` — Mixed Reality (if no VR headset)

### OEM Bloatware (varies by manufacturer)
- Dell: `DellInc.*`, `Dell.*`
- HP: `AD2F1837.*`, `HP.*`
- Lenovo: `LenovoCorporation.*`, `E046963F.*`
- Acer: `AcerIncorporated.*`
- ASUS: `ASUSTeK.*`

## DO NOT Remove
These packages are essential for Windows to function properly:

- `Microsoft.WindowsStore` — Windows Store (needed for app updates)
- `Microsoft.StorePurchaseApp` — Store purchasing infrastructure
- `Microsoft.DesktopAppInstaller` — Winget / App Installer
- `Microsoft.Windows.*` (most) — Core Windows components
- `Microsoft.NET.*` — .NET runtime packages
- `Microsoft.VCLibs.*` — Visual C++ runtime
- `Microsoft.UI.*` — UI framework packages
- `Microsoft.WindowsCalculator` — Calculator
- `Microsoft.WindowsCamera` — Camera
- `Microsoft.ScreenSketch` — Snipping Tool
- `Microsoft.WindowsTerminal` — Terminal
- `Microsoft.WindowsNotepad` — Notepad
- `Microsoft.Paint` — Paint

## Removal Commands

To remove a single package:
```powershell
Get-AppxPackage -Name "Microsoft.BingNews" | Remove-AppxPackage
```

To remove for all users (requires admin):
```powershell
Get-AppxPackage -AllUsers -Name "Microsoft.BingNews" | Remove-AppxPackage -AllUsers
```

To prevent reinstallation on new user accounts (requires admin):
```powershell
Get-AppxProvisionedPackage -Online | Where-Object {$_.PackageName -match "BingNews"} | Remove-AppxProvisionedPackage -Online
```
