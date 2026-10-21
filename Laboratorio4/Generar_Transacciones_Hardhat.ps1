# Laboratorio Hardhat 3 - Generacion de transacciones en un solo bloque
# Ejecutar en Windows PowerShell / PowerShell 7:
#   powershell -ExecutionPolicy Bypass -File .\Generar_Transacciones_Hardhat.ps1
# Requiere nodo Hardhat JSON-RPC local activo en http://127.0.0.1:8545
param(
    [string]$RpcUrl = 'http://127.0.0.1:8545'
)

$ErrorActionPreference = 'Stop'

function Invoke-EthRpc {
    param(
        [Parameter(Mandatory=$true)][string]$Method,
        [object[]]$Parameters = @()
    )

    $payload = @{
        jsonrpc = '2.0'
        id = 1
        method = $Method
        params = $Parameters
    } | ConvertTo-Json -Depth 20 -Compress

    $response = Invoke-RestMethod -Uri $RpcUrl -Method Post -ContentType 'application/json' -Body $payload -TimeoutSec 30
    if ($null -ne $response.error) {
        throw "RPC $Method : $($response.error.message)"
    }
    return $response.result
}

$automineDisabled = $false
$hadError = $false
try {
    Write-Host '=== Laboratorio: transacciones y raices MPT ===' -ForegroundColor Cyan
    $chainId = Invoke-EthRpc -Method 'eth_chainId'
    if ($chainId -ne '0x7a69') {
        throw "La red tiene Chain ID $chainId; se esperaba Hardhat local 0x7a69 (31337)."
    }
    $accounts = @(Invoke-EthRpc -Method 'eth_accounts')
    if ($accounts.Count -lt 8) { throw "Se requieren al menos 8 cuentas; hay $($accounts.Count)." }

    $previous = Invoke-EthRpc -Method 'eth_getBlockByNumber' -Parameters @('latest', $false)
    Write-Host "Bloque anterior: $([Convert]::ToInt64($previous.number.Substring(2),16))"

    # Desactivar automine para agrupar transacciones en un mismo bloque.
    $null = Invoke-EthRpc -Method 'evm_setAutomine' -Parameters @($false)
    $automineDisabled = $true

    # Distintos emisores: evita conflictos de nonce y facilita observar cuatro operaciones.
    $amounts = @(
        '0xDE0B6B3A7640000',  # 1 ETH
        '0x1BC16D674EC80000', # 2 ETH
        '0x6F05B59D3B20000',  # 0.5 ETH
        '0x16345785D8A0000'   # 0.1 ETH
    )
    $hashes = @()
    for ($i = 0; $i -lt 4; $i++) {
        $tx = @{
            from = $accounts[$i]
            to = $accounts[$i+4]
            value = $amounts[$i]
            gas = '0x5208' # 21000 unidades, transferencia simple
        }
        $hash = Invoke-EthRpc -Method 'eth_sendTransaction' -Parameters @($tx)
        $hashes += $hash
        Write-Host "Tx $($i+1): $hash"
    }

    # Minar exactamente un bloque con las transacciones pendientes.
    $null = Invoke-EthRpc -Method 'evm_mine'
    $block = Invoke-EthRpc -Method 'eth_getBlockByNumber' -Parameters @('latest', $true)
    $blockNumber = [Convert]::ToInt64($block.number.Substring(2),16)

    Write-Host "`n=== Bloque generado: $blockNumber ===" -ForegroundColor Green
    Write-Host "Hash:             $($block.hash)"
    Write-Host "Transacciones:    $(@($block.transactions).Count)"
    Write-Host "transactionsRoot: $($block.transactionsRoot)"
    Write-Host "receiptsRoot:     $($block.receiptsRoot)"
    Write-Host "stateRoot:        $($block.stateRoot)"

    Write-Host "`n=== Recibos de las transacciones ===" -ForegroundColor Cyan
    foreach ($hash in $hashes) {
        $receipt = Invoke-EthRpc -Method 'eth_getTransactionReceipt' -Parameters @($hash)
        if ($null -eq $receipt) { throw "No se encontro comprobante de $hash" }
        Write-Host "Hash: $hash | status: $($receipt.status) | block: $($receipt.blockNumber) | gasUsed: $($receipt.gasUsed)"
    }
    $actualHashes = @($block.transactions | ForEach-Object { $_.hash })
    foreach ($hash in $hashes) {
        if ($hash -notin $actualHashes) { throw "La transaccion $hash no esta en el bloque $blockNumber" }
    }
    if (@($block.transactions).Count -ne 4) {
        Write-Warning 'El bloque no contiene exactamente cuatro transacciones; revise el resultado y los logs del nodo.'
    }
    Write-Host "`nConsulta el bloque $blockNumber en http://localhost:3000" -ForegroundColor Green
}
catch {
    $hadError = $true
    Write-Warning "Error durante el laboratorio: $($_.Exception.Message)"
}
finally {
    if ($automineDisabled) {
        try {
            $null = Invoke-EthRpc -Method 'evm_setAutomine' -Parameters @($true)
            Write-Host 'Automine restaurado: true.' -ForegroundColor Yellow
        }
        catch {
            Write-Warning "No se pudo restaurar automine: $($_.Exception.Message). Restablezcalo manualmente."
        }
    }
}

if ($hadError) { exit 1 }
