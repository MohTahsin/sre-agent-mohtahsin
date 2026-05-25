<#
.SYNOPSIS
    Resets the Factory CI/CD remediation demo to its pristine baseline.

.DESCRIPTION
    Run this from the repo root after a demo run. It:
      1. Closes any open PRs on the demo branches (requires `gh`).
      2. Deletes the remote feat/lambda-scaling-recommendation branch.
      3. Deletes any remote docs/factory-update-* branches created by the docs workflow.
      4. Hard-resets local main to the demo-baseline-main tag and force-pushes.
      5. Recreates the local feat/lambda-scaling-recommendation branch from demo-baseline-buggy.

    Does NOT push the buggy feat branch. You push it live during the next demo
    as step 1 of the kickoff so the "watch CI fail" moment stays real.

    Refuses to run with uncommitted changes.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$BaselineMain = "demo-baseline-main"
$BaselineBuggy = "demo-baseline-buggy"
$FeatBranch = "feat/lambda-scaling-recommendation"
$Remote = "origin"

function Write-Step($msg) { Write-Host "[reset] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[reset] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[reset] $msg" -ForegroundColor Yellow }

# Wraps git so PowerShell 5.1 does not raise NativeCommandError when git writes
# informational messages (e.g. "[deleted] foo") to stderr. Throws on non-zero exit.
function Invoke-Git {
    [CmdletBinding()]
    param([Parameter(ValueFromRemainingArguments = $true)] [string[]] $GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = & git @GitArgs 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    if ($code -ne 0) {
        throw "git $($GitArgs -join ' ') failed (exit $code):`n$output"
    }
    return $output
}

# Same as Invoke-Git but never throws; returns the exit code so the caller can
# treat "not found" / "already absent" cases as no-ops.
function Invoke-GitQuiet {
    [CmdletBinding()]
    param([Parameter(ValueFromRemainingArguments = $true)] [string[]] $GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & git @GitArgs 2>&1 | Out-Null
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    return $code
}

if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
    throw "Not a git repository: $RepoRoot"
}

$dirty = Invoke-Git status --porcelain
if ($dirty) {
    throw "Working tree is not clean. Commit or stash changes before resetting:`n$dirty"
}

Invoke-Git fetch --tags --prune $Remote | Out-Null

foreach ($tag in @($BaselineMain, $BaselineBuggy)) {
    $code = Invoke-GitQuiet rev-parse --verify "refs/tags/$tag"
    if ($code -ne 0) {
        throw "Required tag '$tag' not found locally. Run 'git fetch --tags' or recreate the baseline."
    }
}

Write-Step "Closing open demo PRs (if any)..."
$ghAvailable = (Get-Command gh -ErrorAction SilentlyContinue) -ne $null
if ($ghAvailable) {
    $heads = @($FeatBranch)
    $remoteDocsRefs = Invoke-Git ls-remote --heads $Remote 'docs/factory-update-*'
    if ($remoteDocsRefs) {
        $heads += ($remoteDocsRefs | ForEach-Object { ($_ -split '\s+')[1] -replace '^refs/heads/','' })
    }

    foreach ($head in $heads) {
        if (-not $head) { continue }
        $prev = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $prs = gh pr list --head $head --state open --json number --jq '.[].number' 2>&1
        $ErrorActionPreference = $prev
        foreach ($n in $prs) {
            if ($n -match '^\d+$') {
                Write-Step "  closing PR #$n (head: $head)"
                $prev = $ErrorActionPreference
                $ErrorActionPreference = 'Continue'
                gh pr close $n --delete-branch=false 2>&1 | Out-Null
                $ErrorActionPreference = $prev
            }
        }
    }
} else {
    Write-Warn "  'gh' CLI not found; skipping PR close. Close any open demo PRs manually."
}

Write-Step "Deleting remote demo branches..."
[void](Invoke-GitQuiet push $Remote --delete $FeatBranch)

$remoteDocsRefs = Invoke-Git ls-remote --heads $Remote 'docs/factory-update-*'
if ($remoteDocsRefs) {
    $docsBranches = $remoteDocsRefs | ForEach-Object { ($_ -split '\s+')[1] -replace '^refs/heads/','' }
    foreach ($b in $docsBranches) {
        if ($b) {
            Write-Step "  deleting $Remote/$b"
            [void](Invoke-GitQuiet push $Remote --delete $b)
        }
    }
}

Write-Step "Resetting local main to $BaselineMain and force-pushing..."
Invoke-Git checkout main | Out-Null
Invoke-Git reset --hard "refs/tags/$BaselineMain" | Out-Null
Invoke-Git push --force-with-lease $Remote main | Out-Null

Write-Step "Recreating local $FeatBranch from $BaselineBuggy..."
[void](Invoke-GitQuiet branch -D $FeatBranch)
Invoke-Git branch $FeatBranch "refs/tags/$BaselineBuggy" | Out-Null

$mainSha = (Invoke-Git rev-parse --short main).ToString().Trim()
$featSha = (Invoke-Git rev-parse --short $FeatBranch).ToString().Trim()

Write-Ok ""
Write-Ok "Demo reset complete."
Write-Ok "  main          -> $mainSha"
Write-Ok "  $FeatBranch  -> $featSha"
Write-Ok ""
Write-Ok "Next demo run:"
Write-Ok "  git push -u origin $FeatBranch"
Write-Ok "  Then open the PR on GitHub and follow DEMO.md."
