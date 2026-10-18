# ==============================================================================
#  VIBOT ONE-LINE INSTALLER FOR WINDOWS VPS (POWERSHELL)
#  Repository: https://github.com/AbyanZainZ/Vibot
# ==============================================================================
$ErrorActionPreference = 'Continue'

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " 🎬 MEMASANG VIBOT (VIDARA & DOODSTREAM BOT) DI WINDOWS VPS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$TargetDir = "$env:USERPROFILE\Desktop\Vibot"
if (-not (Test-Path "$env:USERPROFILE\Desktop")) {
    $TargetDir = "C:\Vibot"
}

Write-Host "[*] Memeriksa Python..." -ForegroundColor Yellow
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "[!] Python belum terpasang. Mengunduh installer Python resmi..." -ForegroundColor Yellow
    $pyUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $pyInstaller = "$env:TEMP\python_installer.exe"
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item -Force $pyInstaller
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host "[*] Mengunduh repository Vibot..." -ForegroundColor Yellow
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    if (-not (Test-Path $TargetDir)) {
        git clone https://github.com/AbyanZainZ/Vibot.git $TargetDir
    } else {
        Set-Location $TargetDir
        git pull
    }
} else {
    $zipUrl = "https://github.com/AbyanZainZ/Vibot/archive/refs/heads/main.zip"
    $zipPath = "$env:TEMP\vibot.zip"
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\vibot_extracted" -Force
    if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force }
    Copy-Item -Path "$env:TEMP\vibot_extracted\Vibot-main\*" -Destination $TargetDir -Recurse -Force
    Remove-Item -Force $zipPath
    Remove-Item -Recurse -Force "$env:TEMP\vibot_extracted"
}

Set-Location $TargetDir
Write-Host "[*] Memasang dependensi Python..." -ForegroundColor Yellow
pip install -r requirements.txt
playwright install chromium firefox

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host " ✅ INSTALASI VIBOT WINDOWS SELESAI!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host " 📁 Lokasi Bot: $TargetDir"
Write-Host " 🚀 Cara Jalankan: Double-click file START_BOT.bat di dalam folder tersebut"
Write-Host "======================================================================" -ForegroundColor Green
