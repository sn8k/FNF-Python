[CmdletBinding()]
param(
    [ValidateSet("release", "debug", "all")]
    [string]$Configuration = "release",

    [switch]$Clean,
    [switch]$SkipInstall,
    [switch]$NoArchive
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

function Write-Step {
    param([string]$Message)
    Write-Host "[build] $Message"
}

function Remove-RepoPath {
    param([string]$RelativePath)

    $target = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $target)) {
        return
    }

    $resolved = (Resolve-Path -LiteralPath $target).Path
    $repoPrefix = $RepoRoot.TrimEnd("\") + "\"
    if ($resolved -ne $RepoRoot -and -not $resolved.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refus de supprimer un chemin hors depot: $resolved"
    }

    Remove-Item -LiteralPath $resolved -Recurse -Force
}

function Invoke-Python {
    param([string[]]$Arguments)

    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "La commande python a echoue: python $($Arguments -join ' ')"
    }
}

function Compress-ArchiveWithRetry {
    param(
        [string]$SourcePattern,
        [string]$DestinationPath
    )

    $maxAttempts = 5
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        try {
            Compress-Archive -Path $SourcePattern -DestinationPath $DestinationPath -Force
            return
        } catch {
            if ($attempt -eq $maxAttempts) {
                throw
            }
            Write-Step "Archive verrouillee, nouvelle tentative $($attempt + 1)/$maxAttempts"
            Start-Sleep -Seconds 2
        }
    }
}

function Invoke-Build {
    param([ValidateSet("release", "debug")][string]$Name)

    $specPath = Join-Path $RepoRoot "packaging\pyinstaller\fnf_$Name.spec"
    Write-Step "Generation PyInstaller $Name"
    Invoke-Python @("-m", "PyInstaller", "--noconfirm", "--clean", $specPath)

    if (-not $NoArchive) {
        $distPath = Join-Path $RepoRoot "dist\FNF-Python-$Name"
        $artifactPath = Join-Path $RepoRoot "artifacts"
        $zipPath = Join-Path $artifactPath "FNF-Python-$Name.zip"

        if (-not (Test-Path -LiteralPath $distPath)) {
            throw "Dossier dist absent apres build: $distPath"
        }

        New-Item -ItemType Directory -Force -Path $artifactPath | Out-Null
        if (Test-Path -LiteralPath $zipPath) {
            Remove-Item -LiteralPath $zipPath -Force
        }

        Write-Step "Creation de l'archive $zipPath"
        Compress-ArchiveWithRetry -SourcePattern (Join-Path $distPath "*") -DestinationPath $zipPath
    }
}

if (-not $SkipInstall) {
    Write-Step "Installation des dependances runtime et build"
    Invoke-Python @("-m", "pip", "install", "--upgrade", "-r", "requirements.txt", "-r", "requirements-dev.txt")
}

if ($Clean) {
    Write-Step "Nettoyage des anciens artefacts"
    Remove-RepoPath "build"
    Remove-RepoPath "dist"
    Remove-RepoPath "artifacts"
}

if ($Configuration -eq "all") {
    Invoke-Build "release"
    Invoke-Build "debug"
} else {
    Invoke-Build $Configuration
}

Write-Step "Build termine"
