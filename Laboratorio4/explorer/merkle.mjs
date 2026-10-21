import { Trie } from '@ethereumjs/trie';
import { Transaction, encodeRlp, getBytes, hexlify, keccak256 } from 'ethers';

// Ethereum indexes transaction values by RLP(transactionIndex), not their hashes.
function keyFor(index) {
  const n = BigInt(index);
  return getBytes(encodeRlp(n === 0n ? '0x' : '0x' + n.toString(16).padStart(n.toString(16).length + n.toString(16).length % 2, '0')));
}

function serializeRpcTransaction(tx) {
  const type = Number(BigInt(tx.type ?? '0x0'));
  if (![0, 1, 2].includes(type)) throw Error(`Tipo de transacción ${type} aún no compatible para reconstrucción`);
  const options = {
    type,
    chainId: BigInt(tx.chainId),
    nonce: Number(BigInt(tx.nonce)),
    gasLimit: BigInt(tx.gas),
    to: tx.to || null,
    value: BigInt(tx.value),
    data: tx.input ?? '0x',
    signature: {r: tx.r, s: tx.s, yParity: Number(BigInt(tx.yParity ?? (BigInt(tx.v) % 2n)))}
  };
  if (type === 0 || type === 1) options.gasPrice = BigInt(tx.gasPrice);
  if (type === 1 || type === 2) options.accessList = tx.accessList ?? [];
  if (type === 2) {
    options.maxFeePerGas = BigInt(tx.maxFeePerGas);
    options.maxPriorityFeePerGas = BigInt(tx.maxPriorityFeePerGas);
  }
  const raw = Transaction.from(options).serialized;
  if (keccak256(raw).toLowerCase() !== tx.hash.toLowerCase()) {
    throw Error(`Serialización no coincide con el hash de la transacción ${tx.hash}`);
  }
  return getBytes(raw);
}

export async function inspectTransactions(block, getRaw) {
  if (!block?.transactions || !Array.isArray(block.transactions)) throw Error('Bloque inválido');
  if (block.transactions.length > 200) throw Error('Límite didáctico: máximo 200 transacciones por bloque');
  const trie = new Trie();
  const entries = [];
  for (let index = 0; index < block.transactions.length; index++) {
    const tx = block.transactions[index];
    let bytes;
    let source = 'RPC serializado';
    try {
      const raw = await getRaw(tx.hash);
      if (typeof raw === 'string' && /^0x[\da-f]+$/i.test(raw) && keccak256(raw).toLowerCase() === tx.hash.toLowerCase()) {
        bytes = getBytes(raw);
        source = 'RPC raw';
      }
    } catch { /* Algunas versiones de Hardhat no admiten eth_getRawTransactionByHash */ }
    if (!bytes) bytes = serializeRpcTransaction(tx);
    const key = keyFor(index);
    await trie.put(key, bytes);
    entries.push({index,hash:tx.hash, key:hexlify(key), bytes:bytes.length, type:tx.type, source});
  }
  const computed = hexlify(trie.root());
  const expected = block.transactionsRoot;
  const matches = computed.toLowerCase() === expected.toLowerCase();
  const proofs = [];
  for (const entry of entries) {
    const key = getBytes(entry.key);
    const proof = await trie.createProof(key);
    const verifiedValue = await trie.verifyProof(trie.root(), key, proof);
    const verified = Boolean(verifiedValue) && keccak256(verifiedValue).toLowerCase() === entry.hash.toLowerCase();
    proofs.push({index:entry.index, hash:entry.hash, nodeCount:proof.length, verified, nodes:proof.map((node,i)=>({level:i,hash:keccak256(node),bytes:node.length}))});
  }
  return {
    blockNumber: Number(BigInt(block.number)),blockHash:block.hash,
    transactionCount:entries.length, expectedRoot:expected, calculatedRoot:computed, matches,
    receiptsRoot:block.receiptsRoot,stateRoot:block.stateRoot,
    entries,proofs,notes:'Solo se reconstruye transactionsRoot. receiptsRoot y stateRoot son raíces RPC observadas, no recalculadas.'
  };
}
