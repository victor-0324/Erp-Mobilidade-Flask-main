# Caminho para o diretório onde você deseja criar o ambiente virtual
$Path = "C:\Users\G4 Mobile\Documents\Programas\Erp-Mobilidade-Flask\"
$venvPath = "$Path\.venv"
$pythonScriptPath = "$Path\wsgi.py"
$requirementsPath = "$Path\requirements.txt"

# Caminho para o executável do Chrome
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome_proxy.exe"

# Parâmetros para o Chrome
$chromeParams = "--profile-directory=Default --app-id=dpckklemgligkjpihmopkkknllapmclp"

# Função para verificar se a porta 5000 está ocupada
function Test-PortOccupied {
    param (
        [int]$port
    )

    $connection = Test-NetConnection -ComputerName "localhost" -Port $port
    return $connection.TcpTestSucceeded
}

# Verificar se a porta 5000 está ocupada
$port = 5000
Start-Process -FilePath $chromePath -ArgumentList $chromeParams

if (-not (Test-PortOccupied -port $port)) {
    # Verifica se o ambiente virtual já existe, senão cria um novo
    if (-not (Test-Path $venvPath)) {
        python -m venv $venvPath
    }

    # Ativa o ambiente virtual
    . "$venvPath\Scripts\Activate.ps1"

    # Instala as dependências (substitua este trecho pelo comando real, se necessário)
    pip install -r $requirementsPath

    # Inicia o Chrome
    pip freeze
    # Executa o script Python
    python $pythonScriptPath

    # Desativa o ambiente virtual ao término do script
    . "$venvPath\Scripts\deactivate"
} else {
    Write-Host "A porta $port está ocupada. O script Python não será iniciado."
}