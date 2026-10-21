
import { rpc } from "./rpc.mjs";

const accounts = await rpc("eth_accounts");

console.log("CUENTAS ETHEREUM");
console.log("=================");

for (let i = 0; i < accounts.length; i++) {
    const address = accounts[i];

    const balanceHex = await rpc(
        "eth_getBalance",
        [address, "latest"]
    );

    const balanceWei = BigInt(balanceHex);
    const unit = 10n ** 18n;

    const integer = balanceWei / unit;
    const fraction = (balanceWei % unit)
        .toString()
        .padStart(18, "0")
        .slice(0, 6);

    console.log(`Cuenta ${i}: ${address}`);
    console.log(`Saldo: ${integer}.${fraction} ETH`);
    console.log("---------------------------");
}

