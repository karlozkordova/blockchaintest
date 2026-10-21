import fs from "node:fs";
import solc from "solc";
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL || "http://127.0.0.1:8545");
const network = await provider.getNetwork();
if (network.chainId !== 31337n) throw new Error("Solo se permite Hardhat local (31337)");
const accounts = await provider.listAccounts();
if (accounts.length < 2) throw new Error("Se requieren al menos dos cuentas de prueba");
const signer = await provider.getSigner(0);
const sourceFile = "RegistroAcademicoVulnerable.sol";
const source = fs.readFileSync(`/app/contracts/${sourceFile}`, "utf8");
const input = {
  language: "Solidity",
  sources: { [sourceFile]: { content: source } },
  settings: { outputSelection: { "*": { "*": ["abi", "evm.bytecode.object", "evm.deployedBytecode.object"] } } }
};
const output = JSON.parse(solc.compile(JSON.stringify(input)));
for (const issue of output.errors || []) console.log(issue.formattedMessage);
if ((output.errors || []).some(issue => issue.severity === "error")) throw new Error("Error compilando contrato");
const compiled = output.contracts[sourceFile].RegistroAcademicoVulnerable;
const factory = new ethers.ContractFactory(compiled.abi, `0x${compiled.evm.bytecode.object}`, signer);
const contract = await factory.deploy();
const tx = contract.deploymentTransaction();
const receipt = await tx.wait();
if (receipt.status !== 1) throw new Error("Despliegue fallido");
const address = await contract.getAddress();
const bytecode = await provider.getCode(address);
if (bytecode === "0x") throw new Error("No existe bytecode desplegado");
const deployment = {
  contractName: "RegistroAcademicoVulnerable", address,
  chainId: Number(network.chainId), deployer: await signer.getAddress(),
  txHash: tx.hash, blockNumber: receipt.blockNumber,
  compilerVersion: solc.version(), compilerSettings: input.settings, sourceFile,
  deployedBytecode: `0x${compiled.evm.deployedBytecode.object}`, abi: compiled.abi
};
fs.writeFileSync("/app/scripts/deployment-vulnerable.json", JSON.stringify(deployment, null, 2));
console.log("Contrato vulnerable:", address);
console.log("Desplegado en bloque:", receipt.blockNumber);
console.log("TX:", tx.hash);
console.log("Registro: /app/scripts/deployment-vulnerable.json");
