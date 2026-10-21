
import fs from "node:fs";
import path from "node:path";
import solc from "solc";
import { ethers } from "ethers";

const RPC_URL = process.env.RPC_URL ||
    "http://127.0.0.1:8545";

const provider = new ethers.JsonRpcProvider(RPC_URL);
const network = await provider.getNetwork();

if (network.chainId !== 31337n) {
    throw new Error("Red incorrecta");
}

// Utilizar cuenta desbloqueada de Hardhat
const signer = await provider.getSigner(0);

console.log("Red:", network.chainId.toString());
console.log("Cuenta:", await signer.getAddress());

// Leer contrato Solidity
const source = fs.readFileSync(
    "/app/contracts/RegistroAcademico.sol",
    "utf8"
);

const input = {
    language: "Solidity",
    sources: {
        "RegistroAcademico.sol": { content: source }
    },
    settings: {
        outputSelection: {
            "*": {
                "*": ["abi", "evm.bytecode.object", "evm.deployedBytecode.object"]
            }
        }
    }
};

// Compilar
const output = JSON.parse(
    solc.compile(JSON.stringify(input))
);

const errors = output.errors || [];

for (const error of errors) {
    console.log(error.formattedMessage);
}

if (errors.some(e => e.severity === "error")) {
    throw new Error("Compilacion fallida");
}

const compiled =
    output.contracts["RegistroAcademico.sol"]
        ["RegistroAcademico"];

const factory = new ethers.ContractFactory(
    compiled.abi,
    "0x" + compiled.evm.bytecode.object,
    signer
);

// Desplegar en la red local
console.log("Desplegando contrato...");

const contract = await factory.deploy();
await contract.waitForDeployment();

const address = await contract.getAddress();

const tx = contract.deploymentTransaction();
const receipt = await tx.wait();

console.log("Contrato:", address);
console.log("Hash TX:", tx.hash);
console.log("Bloque:", receipt.blockNumber);

// Guardar informacion para usar despues
const deployment = {
    address,
    chainId: Number(network.chainId),
    deployer: await signer.getAddress(),
    txHash: tx.hash,
    blockNumber: receipt.blockNumber,
    compilerVersion: solc.version(),
    compilerSettings: input.settings,
    sourceFile: "RegistroAcademico.sol",
    deployedBytecode: "0x" + compiled.evm.deployedBytecode.object,
    abi: compiled.abi
};

fs.writeFileSync(
    path.resolve("/app/scripts/deployment.json"),
    JSON.stringify(deployment, null, 2)
);

if (receipt.status !== 1) throw new Error("Transaccion de despliegue fallida");
if ((await provider.getCode(address)) === "0x") throw new Error("La direccion no contiene bytecode");
console.log("Despliegue completado.");

