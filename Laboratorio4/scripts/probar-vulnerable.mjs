import fs from "node:fs";
import { ethers } from "ethers";
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL || "http://127.0.0.1:8545");
if ((await provider.getNetwork()).chainId !== 31337n) throw new Error("Solo Hardhat local (31337)");
const deployment = JSON.parse(fs.readFileSync("/app/scripts/deployment-vulnerable.json", "utf8"));
const code = await provider.getCode(deployment.address);
if (code === "0x") throw new Error("El contrato ya no esta desplegado. Vuelve a desplegarlo.");
if (code.toLowerCase() !== deployment.deployedBytecode.toLowerCase()) throw new Error("Bytecode distinto al esperado");
const signer = await provider.getSigner(1); // Cuenta distinta a la que desplego
const contract = new ethers.Contract(deployment.address, deployment.abi, signer);
const propietario = await contract.propietario();
const actor = await signer.getAddress();
if (actor.toLowerCase() === propietario.toLowerCase()) throw new Error("La cuenta de prueba debe ser distinta del propietario");
console.log("Propietario:", propietario);
console.log("Cuenta no propietaria:", actor);
console.log("Antes:", await contract.mensaje());
const tx = await contract.actualizarMensaje("Modificado por una cuenta NO propietaria");
const receipt = await tx.wait();
if (receipt.status !== 1) throw new Error("La escritura no fue exitosa");
console.log("TX:", tx.hash, "Bloque:", receipt.blockNumber);
console.log("Despues:", await contract.mensaje());
console.log("Contador:", (await contract.contador()).toString());
for (const log of receipt.logs) {
  try { const evt = contract.interface.parseLog(log);
    if (evt?.name === "MensajeActualizado") console.log("Evento:", evt.name, "Autor:", evt.args.usuario);
  } catch { /* otros logs */ }
}
