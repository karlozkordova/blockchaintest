
import { rpc } from "./rpc.mjs";

const latestHex = await rpc("eth_blockNumber");
const latest = BigInt(latestHex);

console.log("EXPLORADOR DE BLOQUES");
console.log("======================");
console.log("Ultimo bloque:", latest.toString());

for (let n = latest; n >= 0n; n--) {
    const block = await rpc(
        "eth_getBlockByNumber",
        [`0x${n.toString(16)}`, true]
    );

    if (!block) continue;

    console.log("----------------------");
    console.log("Bloque:", Number(n));
    console.log("Hash:", block.hash);
    console.log("Fecha:",
        new Date(Number(BigInt(block.timestamp)) * 1000)
            .toISOString()
    );
    console.log("Transacciones:",
        block.transactions.length
    );
}


