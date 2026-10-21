import fs from "node:fs";
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL || "http://127.0.0.1:8545");
const data = JSON.parse(fs.readFileSync("/app/scripts/deployment.json", "utf8"));
const network = await provider.getNetwork();
if (network.chainId !== 31337n) throw new Error("La red conectada no es Hardhat 31337");
if (data.chainId !== undefined && BigInt(data.chainId) !== network.chainId) {
  throw new Error("El deployment.json corresponde a otra red");
}
const bytecode = await provider.getCode(data.address);
if (bytecode === "0x") throw new Error("No hay contrato en esa direccion. Despliegue nuevamente.");
const receipt = await provider.getTransactionReceipt(data.txHash);
if (!receipt || receipt.status !== 1 || receipt.contractAddress?.toLowerCase() !== data.address.toLowerCase()) {
  throw new Error("No se encontro recibo de despliegue valido en esta cadena");
}
const contract = new ethers.Contract(data.address, data.abi, provider);
console.log("Red:", network.chainId.toString());
console.log("Direccion:", data.address);
console.log("Bloque:", receipt.blockNumber);
console.log("Hash despliegue:", data.txHash);
console.log("Propietario:", await contract.propietario());
console.log("Mensaje:", await contract.mensaje());
console.log("Contador:", (await contract.contador()).toString());
if (data.deployedBytecode) {
  console.log("Bytecode compilado coincide:", bytecode.toLowerCase() === data.deployedBytecode.toLowerCase());
  if (bytecode.toLowerCase() !== data.deployedBytecode.toLowerCase()) {
    throw new Error("El bytecode de la direccion no coincide con el compilado");
  }
} else {
  console.log("No hay bytecode de referencia guardado (despliegue antiguo)");
}
