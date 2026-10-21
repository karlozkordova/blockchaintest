
const RPC_URL = process.env.RPC_URL ||
    "http://127.0.0.1:8545";

export async function rpc(method, params = []) {
    const response = await fetch(RPC_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method,
            params,
            id: 1
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
        throw new Error(
            JSON.stringify(data.error)
        );
    }

    return data.result;
}

// Permite ejecutar:
// node scripts/rpc.mjs eth_blockNumber
if (process.argv[1]?.endsWith("rpc.mjs")) {
    const method = process.argv[2] || "eth_blockNumber";
    const params = JSON.parse(process.argv[3] || "[]");

    try {
        const result = await rpc(method, params);
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error(error.message);
        process.exitCode = 1;
    }
}

