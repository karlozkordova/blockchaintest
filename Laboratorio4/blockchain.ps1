
function RPC($metodo, $parametros = @()) {
    $body = @{
        jsonrpc = "2.0"
        method = $metodo
        params = @($parametros)
        id = 1
    } | ConvertTo-Json -Depth 20

    $respuesta = Invoke-RestMethod `
        -Uri "http://127.0.0.1:8545" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body

    if ($respuesta.error) {
        throw ($respuesta.error | ConvertTo-Json)
    }

    return $respuesta.result
}


