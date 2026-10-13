#Requires -Version 5.1
# Prepares the local .venv used by run.bat. Launched by windows_setup.bat.

$ErrorActionPreference = 'Stop'

$PythonVersion = '3.14'
$AppDir = Split-Path -Parent $PSScriptRoot
$VenvDir = Join-Path $AppDir '.venv'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
$VenvPythonw = Join-Path $VenvDir 'Scripts\pythonw.exe'
$Requirements = Join-Path $AppDir 'requirements.txt'

function Write-Step([string]$Message) {
    Write-Host ''
    Write-Host "==> $Message" -ForegroundColor Cyan
}

# Runs a native command and returns its exit code. Windows PowerShell 5.1
# turns redirected stderr into terminating errors under 'Stop', so native
# calls run with 'Continue' and are checked through their exit code.
function Invoke-Native {
    param(
        [Parameter(Mandatory)][string]$FilePath,
        [string[]]$Arguments = @(),
        [switch]$Quiet
    )
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        if ($Quiet) {
            & $FilePath @Arguments *> $null
        } else {
            & $FilePath @Arguments | Out-Host
        }
        return $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
}

function Assert-Native([string]$FilePath, [string[]]$Arguments, [string]$FailureMessage) {
    $exitCode = Invoke-Native -FilePath $FilePath -Arguments $Arguments
    if ($exitCode -ne 0) {
        throw "$FailureMessage (exit code $exitCode)."
    }
}

function Update-SessionPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $uvDefaultDir = Join-Path $env:USERPROFILE '.local\bin'
    $env:Path = (@($uvDefaultDir, $userPath, $machinePath, $env:Path) | Where-Object { $_ }) -join ';'
}

function Test-VenvReady {
    if (-not ((Test-Path -LiteralPath $VenvPython) -and (Test-Path -LiteralPath $VenvPythonw))) {
        return $false
    }
    $major, $minor = $PythonVersion.Split('.')
    $check = "import sys; sys.exit(0 if sys.version_info[:2] == ($major, $minor) else 1)"
    return (Invoke-Native -FilePath $VenvPython -Arguments @('-c', $check) -Quiet) -eq 0
}

try {
    Write-Host 'LabPBR to Bedrock Converter - Windows setup'

    Write-Step 'Checking uv'
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Host 'uv is already installed.'
    } else {
        Write-Host 'uv was not found. Installing it from https://astral.sh/uv ...'
        $installCommand = '[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression'
        Assert-Native 'powershell.exe' @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $installCommand) 'The uv installer failed'
        Update-SessionPath
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
            throw 'uv was installed but could not be found. Open a new terminal and run windows_setup.bat again.'
        }
    }

    Write-Step "Checking Python $PythonVersion"
    if ((Invoke-Native -FilePath 'uv' -Arguments @('python', 'find', '--system', $PythonVersion) -Quiet) -eq 0) {
        Write-Host "Python $PythonVersion is already available."
    } else {
        Write-Host "Python $PythonVersion was not found. Downloading it with uv ..."
        Assert-Native 'uv' @('python', 'install', $PythonVersion) "Unable to install Python $PythonVersion"
    }

    Write-Step 'Checking the virtual environment'
    if (Test-VenvReady) {
        Write-Host "The .venv environment already uses Python $PythonVersion."
    } else {
        if (Test-Path -LiteralPath $VenvDir) {
            Write-Host "The existing .venv is incomplete or does not use Python $PythonVersion. Recreating it ..."
        } else {
            Write-Host 'Creating the .venv environment ...'
        }
        Assert-Native 'uv' @('venv', '--clear', '--python', $PythonVersion, $VenvDir) 'Unable to create the .venv environment'
        if (-not (Test-VenvReady)) {
            throw "The .venv environment was created but does not use Python $PythonVersion."
        }
    }

    Write-Step 'Installing dependencies from requirements.txt'
    Assert-Native 'uv' @('pip', 'install', '--python', $VenvPython, '-r', $Requirements) 'Unable to install the dependencies'

    Write-Step 'Verifying the installation'
    Assert-Native $VenvPython @('-c', 'import PySide6, PIL, numpy') 'The dependencies could not be imported'

    Write-Host ''
    Write-Host 'Setup complete. Run run.bat to start the application.' -ForegroundColor Green
    exit 0
} catch {
    Write-Host ''
    Write-Host "Setup failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
