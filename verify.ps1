$ErrorActionPreference = 'Stop'

Push-Location (Join-Path $PSScriptRoot 'frontend')
try {
    npm test
    if ($LASTEXITCODE -ne 0) { throw 'Frontend tests failed.' }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build/typecheck failed.' }
    npm audit --omit=dev
    if ($LASTEXITCODE -ne 0) { throw 'Frontend production dependency audit failed.' }
} finally {
    Pop-Location
}

Push-Location (Join-Path $PSScriptRoot 'backend')
try {
    python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally {
    Pop-Location
}
