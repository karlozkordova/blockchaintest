
import fs from "node:fs";
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider(
    process.env.RPC_URL || "http://127.0.0.1:8545"
);

const signer = await provider.getSigner(0);

const deployment = JSON.parse(
    fs.readFileSync(
        "/app/scripts/deployment.json",
        "utf8"
    )
);

const network = await provider.getNetwork();
if (network.chainId !== 31337n) throw new Error("Red incorrecta: se esperaba 31337");
if (deployment.chainId !== undefined && BigInt(deployment.chainId) !== network.chainId) {
    throw new Error("deployment.json corresponde a otra red");
}

const contract = new ethers.Contract(
    deployment.address,
    deployment.abi,
    signer
);

// Comprobar que el contrato existe
const code = await provider.getCode(deployment.address);

if (code === "0x") {
    throw new Error(
        "Contrato no encontrado. Despliegalo nuevamente."
    );
}

// Leer el estado actual
console.log("Mensaje actual:", await contract.mensaje());
console.log("Contador:", String(await contract.contador()));

// Modificar el mensaje
const tx = await contract.actualizarMensaje(
    "TX desde Docker"
);

const receipt = await tx.wait();

console.log("Hash de transaccion:", receipt.hash);
console.log("Bloque:", receipt.blockNumber);
console.log("Gas utilizado:", String(receipt.gasUsed));

// Consultar el nuevo estado
console.log("Nuevo mensaje:", await contract.mensaje());
console.log("Nuevo contador:", String(await contract.contador()));


// Decodificar evento emitido por este contrato.
for (const log of receipt.logs) {
    if (log.address.toLowerCase() !== deployment.address.toLowerCase()) continue;
    const evento = contract.interface.parseLog(log);
    if (evento?.name === "MensajeActualizado") {
        console.log("Evento:", evento.name);
        console.log("Usuario:", evento.args.usuario);
        console.log("Mensaje emitido:", evento.args.nuevoMensaje);
        console.log("Contador del evento:", String(evento.args.contador));
    }
}
