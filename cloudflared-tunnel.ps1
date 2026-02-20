param(
    [switch]$Down,
    [switch]$Logs,
    [switch]$Prod,
    [switch]$Build
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$composeFile = if ($Prod) { "docker-compose.prod.yml" } else { "docker-compose.yml" }

Push-Location $root
try {
    $baseArgs = @("--env-file", ".env", "-f", $composeFile, "--profile", "tunnel")

    if ($Down) {
        docker compose @baseArgs down --remove-orphans
        exit $LASTEXITCODE
    }

    if ($Logs) {
        docker compose @baseArgs logs -f cloudflared
        exit $LASTEXITCODE
    }

    $upArgs = @("up", "-d", "--remove-orphans")
    if ($Build) {
        $upArgs += "--build"
    }
    docker compose @baseArgs @upArgs
}
finally {
    Pop-Location
}
