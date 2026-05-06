# =============================================================================
# build-all.ps1 — render every .tex under docs/figures/ to .svg
# =============================================================================
# Usage (from the docs/figures/ directory):
#     .\build-all.ps1
#
# Requires:
#   - MiKTeX (pdflatex on PATH)
#   - Poppler (pdftocairo on PATH)
#
# Recursively finds every .tex (skipping the style/ subdirectory), runs
# pdflatex -> pdftocairo per file, and cleans up intermediate files.
# =============================================================================

$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$figDirs = @("system-design", "modules", "chassis")

function Build-OneFigure {
    param([string]$texPath)

    $dir  = Split-Path $texPath -Parent
    $base = [System.IO.Path]::GetFileNameWithoutExtension($texPath)

    Push-Location $dir
    try {
        Write-Host "Building $base..." -ForegroundColor Cyan

        # Run pdflatex twice in case TikZ needs the second pass for
        # remembered positions (overlays, fit nodes referencing later content).
        & pdflatex -interaction=nonstopmode -halt-on-error "$base.tex" | Out-Null
        & pdflatex -interaction=nonstopmode -halt-on-error "$base.tex" | Out-Null

        if (-not (Test-Path "$base.pdf")) {
            Write-Host "  pdflatex failed for $base" -ForegroundColor Red
            return
        }

        & pdftocairo -svg "$base.pdf" "$base.svg"

        if (Test-Path "$base.svg") {
            Write-Host "  $base.svg" -ForegroundColor Green
        }

        # Clean up LaTeX intermediate artifacts (keep .tex and .svg)
        Get-ChildItem -Filter "$base.aux" | Remove-Item -ErrorAction SilentlyContinue
        Get-ChildItem -Filter "$base.log" | Remove-Item -ErrorAction SilentlyContinue
        Get-ChildItem -Filter "$base.out" | Remove-Item -ErrorAction SilentlyContinue
        Get-ChildItem -Filter "$base.pdf" | Remove-Item -ErrorAction SilentlyContinue
    }
    finally {
        Pop-Location
    }
}

foreach ($subdir in $figDirs) {
    $path = Join-Path $here $subdir
    if (-not (Test-Path $path)) { continue }

    Get-ChildItem -Path $path -Filter "*.tex" -Recurse | ForEach-Object {
        Build-OneFigure $_.FullName
    }
}

Write-Host "`nDone." -ForegroundColor Cyan
