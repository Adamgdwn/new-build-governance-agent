$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Get-PythonCommand {
    $candidates = @(
        @("py", "-3"),
        @("python"),
        @("python3")
    )

    foreach ($candidate in $candidates) {
        try {
            $exe = $candidate[0]
            $prefix = @()
            if ($candidate.Count -gt 1) {
                $prefix = $candidate[1..($candidate.Count - 1)]
            }
            & $exe @prefix -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)" *> $null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {
            continue
        }
    }

    throw "Unable to find Python 3.8 or newer."
}

function Invoke-Python {
    param(
        [string[]]$PythonCommand,
        [string[]]$Arguments
    )

    $exe = $PythonCommand[0]
    $prefix = @()
    if ($PythonCommand.Count -gt 1) {
        $prefix = $PythonCommand[1..($PythonCommand.Count - 1)]
    }
    & $exe @prefix @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Arguments -join ' ')"
    }
}

function Invoke-PythonCapture {
    param(
        [string[]]$PythonCommand,
        [string[]]$Arguments,
        [int[]]$AllowedExitCodes = @(0)
    )

    $exe = $PythonCommand[0]
    $prefix = @()
    if ($PythonCommand.Count -gt 1) {
        $prefix = $PythonCommand[1..($PythonCommand.Count - 1)]
    }
    $output = & $exe @prefix @Arguments 2>&1
    if (-not ($AllowedExitCodes -contains $LASTEXITCODE)) {
        throw "Python command failed with exit code ${LASTEXITCODE}: $($Arguments -join ' ')`n$($output -join "`n")"
    }
    return (($output | ForEach-Object { $_.ToString() }) -join "`n").Trim()
}

function Test-RequiredFile {
    param([string]$RelativePath)

    $path = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path $path)) {
        throw "Missing required file: $RelativePath"
    }
    Write-Host "PASS: Found $RelativePath"
}

function Test-RequiredDirectory {
    param([string]$RelativePath)

    $path = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path $path -PathType Container)) {
        throw "Missing required directory: $RelativePath"
    }
    Write-Host "PASS: Found $RelativePath"
}

$requiredFiles = @(
    "README.md",
    "START_HERE.md",
    "project-control.yaml",
    "docs/architecture.md",
    "docs/current-build-pathway.md",
    "docs/manual.md",
    "docs/roadmap.md",
    "docs/policy/durable-development-engineering-policy.md",
    "docs/standards/README.md",
    "docs/standards/engineering-governance-by-use-case.md",
    "docs/standards/ship-ready-engineering-standard.md",
    "docs/risks/risk-register.md",
    "docs/deployment-guide.md",
    "docs/runbook.md",
    "docs/CHANGELOG.md",
    "docs/agent-inventory.md",
    "docs/model-registry.md",
    "docs/prompt-register.md",
    "docs/tool-permission-matrix.md",
    "AGENTS.md"
)

foreach ($file in $requiredFiles) {
    Test-RequiredFile $file
}
Test-RequiredDirectory "scripts"

$python = Get-PythonCommand
Invoke-Python -PythonCommand $python -Arguments @((Join-Path $RepoRoot "automation/schema_validation.py"), "--project", $RepoRoot)

$pythonFiles = Get-ChildItem -Path (Join-Path $RepoRoot "automation") -Filter "*.py" -File | Sort-Object FullName
foreach ($file in $pythonFiles) {
    Invoke-Python -PythonCommand $python -Arguments @("-m", "py_compile", $file.FullName)
}

foreach ($tool in @("ruff", "mypy")) {
    try {
        Invoke-PythonCapture -PythonCommand $python -Arguments @("-m", $tool, "--version") | Out-Null
    } catch {
        throw "$tool is required by the validation gate. Install dev tools: python -m pip install ruff mypy"
    }
}
Push-Location $RepoRoot
try {
    Invoke-Python -PythonCommand $python -Arguments @("-m", "ruff", "check", "automation", "tests", "scripts")
    Invoke-Python -PythonCommand $python -Arguments @("-m", "ruff", "format", "--check", "automation", "tests")
    Write-Host "PASS: ruff lint + format"
    Invoke-Python -PythonCommand $python -Arguments @("-m", "mypy", "automation")
    Write-Host "PASS: mypy"
} finally {
    Pop-Location
}

$psFiles = @(
    Get-ChildItem -Path (Join-Path $RepoRoot "automation") -Filter "*.ps1" -File
    Get-ChildItem -Path (Join-Path $RepoRoot "scripts") -Filter "*.ps1" -File
) | Sort-Object FullName
foreach ($file in $psFiles) {
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count -gt 0) {
        throw "PowerShell syntax failed for $($file.FullName): $($errors[0].Message)"
    }
}
Write-Host "PASS: PowerShell syntax"

if (Get-Module -ListAvailable PSScriptAnalyzer) {
    $analyzerFindings = @(Invoke-ScriptAnalyzer -Path (Join-Path $RepoRoot "automation") -Severity Error) +
        @(Invoke-ScriptAnalyzer -Path (Join-Path $RepoRoot "scripts") -Severity Error)
    if ($analyzerFindings.Count -gt 0) {
        $analyzerFindings | Format-Table RuleName, ScriptName, Line -AutoSize | Out-String | Write-Host
        throw "PSScriptAnalyzer found $($analyzerFindings.Count) error-severity finding(s)."
    }
    Write-Host "PASS: PSScriptAnalyzer (error severity)"
} else {
    Write-Host "SKIP: PSScriptAnalyzer not installed locally (enforced in CI)."
}

$shellcheck = Get-Command shellcheck -ErrorAction SilentlyContinue
if ($shellcheck) {
    $shellFilesForLint = @(
        Get-ChildItem -Path (Join-Path $RepoRoot "automation") -Filter "*.sh" -File
        Get-ChildItem -Path (Join-Path $RepoRoot "scripts") -Filter "*.sh" -File
        Get-ChildItem -Path (Join-Path $RepoRoot "templates/project/scripts") -Filter "*.sh" -File
    ) | Sort-Object FullName | ForEach-Object { $_.FullName }
    & $shellcheck.Source @shellFilesForLint
    if ($LASTEXITCODE -ne 0) {
        throw "shellcheck reported findings."
    }
    Write-Host "PASS: shellcheck"
} else {
    Write-Host "SKIP: shellcheck not installed locally (enforced in CI)."
}

$bash = Get-Command bash -ErrorAction SilentlyContinue
if ($bash) {
    $shellFiles = @(
        Get-ChildItem -Path (Join-Path $RepoRoot "automation") -Filter "*.sh" -File
        Get-ChildItem -Path (Join-Path $RepoRoot "scripts") -Filter "*.sh" -File
        Get-ChildItem -Path (Join-Path $RepoRoot "templates/project/scripts") -Filter "*.sh" -File
    ) | Sort-Object FullName
    foreach ($file in $shellFiles) {
        $shellPath = $file.FullName
        if ($bash.Source -like "*\WindowsApps\bash.exe") {
            $shellPath = (Resolve-Path -Path $file.FullName -Relative).Replace("\", "/")
        }
        & $bash.Source -n $shellPath
        if ($LASTEXITCODE -ne 0) {
            throw "Shell syntax failed for $($file.FullName)"
        }
    }
    Write-Host "PASS: Shell syntax"
} else {
    Write-Host "SKIP: Shell syntax check requires bash."
}

Write-Host "Running secret-hygiene scan (tests/test_secret_hygiene.py)"
Invoke-Python -PythonCommand $python -Arguments @("-m", "unittest", "discover", "-s", (Join-Path $RepoRoot "tests"), "-p", "test_secret_hygiene*.py")

Invoke-Python -PythonCommand $python -Arguments @("-m", "unittest", "discover", "-s", (Join-Path $RepoRoot "tests"), "-p", "test_*.py")

$version = (Get-Content -Path (Join-Path $RepoRoot "VERSION") -Raw).Trim()
$plainVersion = Invoke-PythonCapture -PythonCommand $python -Arguments @((Join-Path $RepoRoot "automation/version.py"), "--plain")
if ($plainVersion -ne $version) {
    throw "Version helper returned '$plainVersion', expected '$version'."
}

$versionJson = Invoke-PythonCapture -PythonCommand $python -Arguments @((Join-Path $RepoRoot "automation/version.py"), "--json") | ConvertFrom-Json
if ($versionJson.version -ne $version -or $versionJson.slug -ne "new-build-governance-agent") {
    throw "Version JSON did not match expected product metadata."
}

$headlessVersion = Invoke-PythonCapture -PythonCommand $python -Arguments @((Join-Path $RepoRoot "automation/new_build_headless.py"), "--version")
if ($headlessVersion -ne "New Build Governance Agent $version") {
    throw "Headless version output was '$headlessVersion'."
}

$launcherVersion = & (Join-Path $RepoRoot "automation/new_build.ps1") -Version 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "PowerShell new build launcher -Version failed: $($launcherVersion -join "`n")"
}
if ((($launcherVersion | ForEach-Object { $_.ToString() }) -join "`n") -notmatch [regex]::Escape($version)) {
    throw "PowerShell new build launcher -Version did not include $version."
}

$updateJson = Invoke-PythonCapture -PythonCommand $python -Arguments @((Join-Path $RepoRoot "automation/update_check.py"), "--json", "--timeout", "0.001")
$update = $updateJson | ConvertFrom-Json
$allowedUpdateStatuses = @("current", "behind", "ahead", "unable_to_check")
if (-not ($allowedUpdateStatuses -contains $update.status)) {
    throw "Unexpected update check status: $($update.status)"
}

$missingRepo = Join-Path $RepoRoot ".not-a-real-self-update-repo"
$selfUpdateJson = Invoke-PythonCapture -PythonCommand $python -Arguments @((Join-Path $RepoRoot "automation/self_update.py"), "--repo", $missingRepo, "--dry-run", "--json") -AllowedExitCodes @(2)
$selfUpdate = $selfUpdateJson | ConvertFrom-Json
if ($selfUpdate.status -ne "failed") {
    throw "Expected self-update missing-repo smoke test to report failed, got $($selfUpdate.status)."
}

Write-Host "PASS: Windows launcher smoke tests"

& (Join-Path $RepoRoot "scripts/build-windows-launcher.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Windows executable launcher build failed."
}

$launcherExe = Join-Path $RepoRoot "dist/windows/NewBuildGovernanceAgent.exe"
$launcherPackage = Join-Path $RepoRoot "dist/NewBuildGovernanceAgent-Windows.zip"
if (-not (Test-Path $launcherExe)) {
    throw "Missing built Windows launcher executable: $launcherExe"
}
if (-not (Test-Path $launcherPackage)) {
    throw "Missing Windows launcher package: $launcherPackage"
}
Write-Host "PASS: Windows executable launcher build"

Write-Host "Validation complete."
exit 0
