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

if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
    throw "Not a git repository: $RepoRoot"
}

$dirty = git status --porcelain
if ($dirty) {
    throw "Working tree is not clean. Commit or stash changes before resetting:`n$dirty"
}

git fetch --tags --prune $Remote | Out-Null

foreach ($tag in @($BaselineMain, $BaselineBuggy)) {
    git rev-parse --verify "refs/tags/$tag" 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Required tag '$tag' not found locally. Run 'git fetch --tags' or recreate the baseline."
    }
}

Write-Step "Closing open demo PRs (if any)..."
$ghAvailable = (Get-Command gh -ErrorAction SilentlyContinue) -ne $null
if ($ghAvailable) {
    $heads = @($FeatBranch)
    $heads += (git ls-remote --heads $Remote 'docs/factory-update-*' |
        ForEach-Object { ($_ -split '\s+')[1] -replace '^refs/heads/','' })

    foreach ($head in $heads) {
        if (-not $head) { continue }
        $prs = gh pr list --head $head --state open --json number --jq '.[].number' 2>$null
        foreach ($n in $prs) {
            if ($n) {
                Write-Step "  closing PR #$n (head: $head)"
                gh pr close $n --delete-branch=false 2>$null | Out-Null
            }
        }
    }
} else {
    Write-Warn "  'gh' CLI not found; skipping PR close. Close any open demo PRs manually."
}

Write-Step "Deleting remote demo branches..."
git push $Remote --delete $FeatBranch 2>$null | Out-Null
$docsBranches = git ls-remote --heads $Remote 'docs/factory-update-*' |
    ForEach-Object { ($_ -split '\s+')[1] -replace '^refs/heads/','' }
foreach ($b in $docsBranches) {
    if ($b) {
        Write-Step "  deleting $Remote/$b"
        git push $Remote --delete $b 2>$null | Out-Null
    }
}

Write-Step "Resetting local main to $BaselineMain and force-pushing..."
git checkout main | Out-Null
git reset --hard "refs/tags/$BaselineMain"
git push --force-with-lease $Remote main

Write-Step "Recreating local $FeatBranch from $BaselineBuggy..."
git branch -D $FeatBranch 2>$null | Out-Null
git branch $FeatBranch "refs/tags/$BaselineBuggy"

Write-Ok ""
Write-Ok "Demo reset complete."
Write-Ok "  main          -> $(git rev-parse --short main)"
Write-Ok "  $FeatBranch  -> $(git rev-parse --short $FeatBranch)"
Write-Ok ""
Write-Ok "Next demo run:"
Write-Ok "  git push -u origin $FeatBranch"
Write-Ok "  Then open the PR on GitHub and follow DEMO.md."
