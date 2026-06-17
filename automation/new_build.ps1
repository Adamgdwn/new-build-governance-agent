param(
    [switch]$Version,
    [switch]$CheckUpdates,
    [switch]$SelfUpdate,
    [string]$ProjectName = "",
    [string]$BuildType = "",
    [string]$GovernanceType = "",
    [string]$PrimaryBuilder = "",
    [string]$Stack = "",
    [string]$GovernanceLevel = "",
    [string]$ScopeProblem = "",
    [string]$ScopeUser = "",
    [string]$ScopeMvp = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Headless = Join-Path $RepoRoot "automation/new_build_headless.py"
$VersionScript = Join-Path $RepoRoot "automation/version.py"
$UpdateCheckScript = Join-Path $RepoRoot "automation/update_check.py"
$SelfUpdateScript = Join-Path $RepoRoot "automation/self_update.py"

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

    throw "Unable to find Python 3.8 or newer. Install Python from https://www.python.org/downloads/windows/ and enable the launcher."
}

function Read-Required {
    param([string]$Prompt, [string]$Value)

    while ([string]::IsNullOrWhiteSpace($Value)) {
        $Value = Read-Host $Prompt
    }
    return $Value.Trim()
}

function Read-Choice {
    param(
        [string]$Prompt,
        [string[]]$Choices,
        [string]$Value
    )

    while ([string]::IsNullOrWhiteSpace($Value) -or -not ($Choices -contains $Value)) {
        $shown = $Choices -join "/"
        $Value = Read-Host "$Prompt ($shown)"
    }
    return $Value
}

function ConvertTo-Slug {
    param([string]$Value)

    $slug = $Value.ToLowerInvariant()
    $slug = $slug -replace "[ _/]+", "-"
    $slug = $slug -replace "[^a-z0-9-]", ""
    $slug = $slug -replace "-+", "-"
    return $slug.Trim("-")
}

$python = Get-PythonCommand
$pythonExe = $python[0]
$pythonPrefix = @()
if ($python.Count -gt 1) {
    $pythonPrefix = $python[1..($python.Count - 1)]
}

if ($Version) {
    & $pythonExe @pythonPrefix $VersionScript
    exit $LASTEXITCODE
}

if ($CheckUpdates) {
    & $pythonExe @pythonPrefix $UpdateCheckScript
    exit $LASTEXITCODE
}

if ($SelfUpdate) {
    & $pythonExe @pythonPrefix $SelfUpdateScript
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "New Build Governance Agent"
Write-Host "Scope -> Classify -> Scaffold"
Write-Host ""

$ProjectName = Read-Required "Project name" $ProjectName
$BuildType = Read-Choice "Build type" @("app", "agent", "tool", "other") $BuildType

if ($BuildType -eq "other" -and [string]::IsNullOrWhiteSpace($GovernanceType)) {
    Write-Host ""
    Write-Host "Supported governance types: website, service, internal-tool, automation, infrastructure, documentation"
    $GovernanceType = Read-Required "Governance project type" $GovernanceType
}

if ([string]::IsNullOrWhiteSpace($Stack)) {
    $Stack = Read-Host "Expected stack [not specified]"
    if ([string]::IsNullOrWhiteSpace($Stack)) {
        $Stack = "not specified"
    }
}

$PrimaryBuilder = Read-Choice "Primary builder" @("claude", "codex", "local", "hybrid") $PrimaryBuilder

Write-Host ""
Write-Host "Governance level scale:"
Write-Host "  0 = full autonomy"
Write-Host "  1 = light guardrails"
Write-Host "  2 = standard supervised"
Write-Host "  3 = strict review"
Write-Host "  4 = critical controls"
$GovernanceLevel = Read-Choice "Governance level" @("0", "1", "2", "3", "4") $GovernanceLevel

$captureScope = Read-Choice "Capture scope brief now?" @("yes", "no") ""
if ($captureScope -eq "yes") {
    $ScopeProblem = Read-Required "What problem does this solve" $ScopeProblem
    $ScopeUser = Read-Required "Who is the primary user or consumer" $ScopeUser
    $ScopeMvp = Read-Required "What does the MVP look like" $ScopeMvp
}

$slug = ConvertTo-Slug $ProjectName
$reservedSlugs = @("con","prn","aux","nul","com1","com2","com3","com4","com5","com6","com7","com8","com9","lpt1","lpt2","lpt3","lpt4","lpt5","lpt6","lpt7","lpt8","lpt9")
if ([string]::IsNullOrEmpty($slug) -or $slug.Length -lt 2) {
    Write-Error "Project name '$ProjectName' produced an invalid slug '$slug'. Use ASCII letters, digits, or hyphens (minimum 2 characters)."
    exit 1
}
if ($reservedSlugs -contains $slug.ToLowerInvariant()) {
    Write-Error "Slug '$slug' is a reserved OS name. Choose a different project name."
    exit 1
}
$codeRoot = Join-Path $HOME "code"
if ($BuildType -eq "agent" -or $GovernanceType -eq "agent") {
    $targetDir = Join-Path (Join-Path $codeRoot "agents") $slug
} else {
    $targetDir = Join-Path (Join-Path $codeRoot "Applications") $slug
}

Write-Host ""
Write-Host "Plan"
Write-Host "  Name:       $ProjectName"
Write-Host "  Slug:       $slug"
Write-Host "  Type:       $BuildType"
Write-Host "  Governance: $GovernanceLevel"
Write-Host "  Builder:    $PrimaryBuilder"
Write-Host "  Stack:      $Stack"
Write-Host "  Location:   $targetDir"
if (Test-Path $targetDir) {
    Write-Host "  Warning: location already exists. Existing files will not be overwritten."
}
$confirm = Read-Choice "Create this project?" @("yes", "no") ""
if ($confirm -ne "yes") {
    Write-Host "Aborted."
    exit 0
}

$params = @{
    project_name = $ProjectName
    build_type = $BuildType
    governance_level = $GovernanceLevel
    primary_builder = $PrimaryBuilder
    stack = $Stack
    scope_problem = $ScopeProblem
    scope_user = $ScopeUser
    scope_mvp = $ScopeMvp
}
if (-not [string]::IsNullOrWhiteSpace($GovernanceType)) {
    $params["governance_type"] = $GovernanceType
}

$json = $params | ConvertTo-Json -Depth 5 -Compress
$json | & $pythonExe @pythonPrefix $Headless
exit $LASTEXITCODE
