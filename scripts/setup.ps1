$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$aiRoot = Join-Path $HOME 'AI'

Write-Host '[1/5] Checking Python availability...'
$pythonVersion = $null
try {
	$pythonVersion = (python --version) 2>&1
} catch {
	Write-Error 'Python is not available on PATH. Install Python 3.11+ and re-run this script.'
}
Write-Host "Detected: $pythonVersion"

Write-Host '[2/5] Creating runtime folders...'
$dirs = @(
	'AIAgentCoder\IN',
	'AIAgentCoder\PROCESSING',
	'AIAgentCoder\SUCCESS',
	'AIAgentCoder\FAILURE',
	'AIAgentQA\IN',
	'AIAgentQA\PROCESSING',
	'AIAgentQA\SUCCESS',
	'AIAgentQA\FAILURE',
	'Tasks',
	'Data'
)
foreach ($d in $dirs) {
	New-Item -ItemType Directory -Path (Join-Path $aiRoot $d) -Force | Out-Null
}

Write-Host '[3/5] Installing Python dependencies...'
python -m pip install --upgrade pip
python -m pip install -r (Join-Path $repoRoot 'requirements.txt')

Write-Host '[4/5] Running unit/integration tests...'
python -m pytest (Join-Path $repoRoot 'tests\unit') (Join-Path $repoRoot 'tests\integration') -q

Write-Host '[5/5] Setup complete.'
Write-Host 'Run coder agent: python -m src.aia_coder.agent'
Write-Host 'Run qa agent:    python -m src.aia_qa.agent'
