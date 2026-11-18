<#
.SYNOPSIS
  Diagnose the Cursor <-> Magpie bridge, and optionally restart it.

.DESCRIPTION
  Checks, in order:
    1. the bridge's own status.json
    2. the proxy port the bridge published (default 52407)
    3. Cursor's settings.json proxy keys
    4. the local CA in the Windows Root store
    5. the Magpie gateway on 127.0.0.1:3425

  Read-only by default. -Fix re-runs the plugin setup, starts the supervisor
  when it is missing, and re-checks.

  Exit code 0 means every check passed after the run, 1 means something is
  still failing (or Magpie itself is down, which this script cannot start).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\cursor-bridge-check.ps1

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\cursor-bridge-check.ps1 -Fix
#>

param(
    [switch]$Fix
)

$ErrorActionPreference = 'Stop'

$bridgeRoot = Join-Path $env:USERPROFILE '.config\magpie-cursor-bridge'
$statusPath = Join-Path $bridgeRoot 'status.json'
$settingsPath = Join-Path $env:APPDATA 'Cursor\User\settings.json'
$pluginDir = Join-Path $env:USERPROFILE '.config\magpie\plugins\node_modules\magpie-agent-cursor-bridge'
$gatewayPort = 3425
$defaultProxyPort = 52407

$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
    param([string]$Step, [string]$State, [string]$Detail)
    $results.Add([pscustomobject]@{ Step = $Step; State = $State; Detail = $Detail })
}

function Test-Port {
    param([int]$Port)
    $listening = @()
    try {
        $listening = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction Stop
    }
    catch {
        $line = netstat -ano | Select-String -Pattern ":$Port\s+.*LISTENING"
        $listening = @($line)
    }
    return [bool]($listening | Where-Object { $_ })
}

function Get-Status {
    if (-not (Test-Path $statusPath)) { return $null }
    try { return Get-Content $statusPath -Raw | ConvertFrom-Json } catch { return $null }
}

function Get-ProxyPort {
    param($Status)
    if ($Status -and $Status.proxy -match ':(\d+)') { return [int]$Matches[1] }
    return $defaultProxyPort
}

function Invoke-Checks {
    $results.Clear()

    $status = Get-Status
    if ($status) {
        $detail = "state=$($status.state) model=$($status.model) models=$($status.models)"
        $state = if ($status.state -eq 'connected') { 'OK' } else { 'FAIL' }
        Add-Result 'status.json' $state $detail
    }
    else {
        Add-Result 'status.json' 'FAIL' "missing or unreadable: $statusPath"
    }

    $proxyPort = Get-ProxyPort $status
    if (Test-Port $proxyPort) {
        Add-Result "proxy :$proxyPort" 'OK' 'LISTENING'
    }
    else {
        Add-Result "proxy :$proxyPort" 'FAIL' 'nothing is listening; the bridge supervisor is not running'
    }

    if (Test-Path $settingsPath) {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
        $proxy = $settings.'http.proxy'
        if ($proxy -and $proxy -match ":$proxyPort") {
            Add-Result 'cursor settings.json' 'OK' "http.proxy=$proxy"
        }
        else {
            Add-Result 'cursor settings.json' 'FAIL' "http.proxy is '$proxy', expected port $proxyPort"
        }
    }
    else {
        Add-Result 'cursor settings.json' 'FAIL' "missing: $settingsPath"
    }

    $caFound = $false
    try {
        $caFound = [bool](certutil -store Root 2>$null | Select-String -Pattern 'Cursor BYOK Local CA' -Quiet)
    }
    catch {
        $caFound = $false
    }
    if ($caFound) {
        Add-Result 'local CA' 'OK' 'Cursor BYOK Local CA is in the Windows Root store'
    }
    else {
        Add-Result 'local CA' 'WARN' 'not found in the Root store; TLS interception will fail'
    }

    if (Test-Port $gatewayPort) {
        Add-Result "magpie :$gatewayPort" 'OK' 'LISTENING'
    }
    else {
        Add-Result "magpie :$gatewayPort" 'FAIL' 'gateway down; start Magpie'
    }

    return $proxyPort
}

function Show-Results {
    $results | ForEach-Object {
        "{0,-22} {1,-5} {2}" -f $_.Step, $_.State, $_.Detail
    }
    $failed = @($results | Where-Object { $_.State -eq 'FAIL' })
    if ($failed.Count -eq 0) {
        'VERDICT: OK - Cursor is bridged to Magpie'
    }
    else {
        "VERDICT: BROKEN - $($failed.Count) check(s) failed"
    }
}

function Start-Supervisor {
    $releases = Join-Path $env:USERPROFILE '.local\share\magpie-cursor-bridge\releases'
    if (-not (Test-Path $releases)) {
        throw "bridge releases not found: $releases (run the plugin setup first)"
    }
    $release = Get-ChildItem $releases -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $runtime = Join-Path $release.FullName 'bin\runtime.exe'
    $bridge = Join-Path $release.FullName 'bridge.js'
    if (-not (Test-Path $runtime) -or -not (Test-Path $bridge)) {
        throw "runtime.exe or bridge.js missing under $($release.FullName)"
    }
    $proc = Start-Process -FilePath $runtime -ArgumentList "`"$bridge`"", 'supervise' -WindowStyle Hidden -PassThru
    "started supervisor from $($release.Name) (pid $($proc.Id))"
}

function Get-BridgeFailures {
    @($results | Where-Object { $_.State -eq 'FAIL' -and $_.Step -notlike 'magpie*' })
}

$proxyPort = Invoke-Checks
Show-Results

if ($Fix) {
    $bridgeFailures = Get-BridgeFailures
    if ($bridgeFailures.Count -eq 0) {
        'Nothing to fix.'
    }
    elseif (-not (Test-Port $gatewayPort)) {
        'Magpie gateway :3425 is down. Start Magpie, wait for it to finish loading, then re-run this script.'
    }
    else {
        if (Test-Path (Join-Path $pluginDir 'setup.ps1')) {
            "running plugin setup..."
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pluginDir 'setup.ps1') | Out-Host
        }

        Start-Sleep -Seconds 3
        $status = Get-Status
        if (-not (Test-Port (Get-ProxyPort $status))) {
            Start-Supervisor
        }

        for ($i = 0; $i -lt 12; $i++) {
            Start-Sleep -Seconds 2
            $status = Get-Status
            if ($status -and $status.state -eq 'connected' -and (Test-Port (Get-ProxyPort $status))) { break }
        }

        ''
        'After fix:'
        $proxyPort = Invoke-Checks
        Show-Results

        if (@(Get-BridgeFailures).Count -gt 0) {
            ''
            'Still failing: in Cursor run "Developer: Reload Window" (the proxy key is read at startup), then re-run this script.'
        }
    }
}

$final = @($results | Where-Object { $_.State -eq 'FAIL' })
if ($final.Count -gt 0) { exit 1 }
exit 0
