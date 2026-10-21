const el=id=>document.getElementById(id);
const short=(v,n=10)=>!v?'—':`${v.slice(0,n)}…${v.slice(-6)}`;
const eth=(h)=>{const wei=BigInt(h);const whole=wei/10n**18n;const frac=(wei%10n**18n).toString().padStart(18,'0').slice(0,5);return `${whole}.${frac}`;};
const rpc=async(method,params=[])=>{const res=await fetch('/api/rpc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method,params})});const d=await res.json();if(!res.ok||d.error)throw Error(d.error?.message||d.error||d.details||'RPC error');return d.result;};
const text=(tag,str,cl)=>{const n=document.createElement(tag);n.textContent=String(str);if(cl)n.className=cl;return n;};
function row(tbody,values){const tr=document.createElement('tr');for(const v of values){const td=document.createElement('td');if(v instanceof Node)td.append(v);else td.textContent=String(v);tr.append(td);}tbody.append(tr);}
function linkHash(hash){const a=text('a',short(hash),'mono');a.href='#buscar';a.title=hash;a.addEventListener('click',e=>{e.preventDefault();el('hash-input').value=hash;lookup(hash);});return a;}
async function load(){const b=el('refresh');b.disabled=true;try{
 const [chain,latest,accounts,client]=await Promise.all([rpc('eth_chainId'),rpc('eth_blockNumber'),rpc('eth_accounts'),rpc('web3_clientVersion')]);
 el('chain').textContent=Number(BigInt(chain));el('height').textContent=BigInt(latest).toString();el('accounts-total').textContent=accounts.length;el('client').textContent=client.split('/').slice(0,2).join('/');el('client').title=client;
 const n=BigInt(latest), numbers=[];for(let i=n;i>=0n&&numbers.length<12;i--)numbers.push(i);
 const blocks=await Promise.all(numbers.map(i=>rpc('eth_getBlockByNumber',['0x'+i.toString(16),true])));
 const tbody=el('blocks');tbody.replaceChildren();for(const block of blocks){if(!block)continue;const date=new Date(Number(BigInt(block.timestamp))*1000).toLocaleString('es-EC');row(tbody,[BigInt(block.number).toString(),text('span',short(block.hash),'mono'),block.transactions.length,date]);if(block.transactions.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=4;td.append(text('span','Transacciones: '));for(const tx of block.transactions){td.append(linkHash(tx.hash),text('span','  '));}tr.append(td);tbody.append(tr);}}
 const shown=accounts.slice(0,20);const balances=await Promise.all(shown.map(a=>rpc('eth_getBalance',[a,'latest'])));const acctBody=el('accounts');acctBody.replaceChildren();shown.forEach((a,i)=>row(acctBody,[i,text('span',short(a,12),'mono'),eth(balances[i])]));
 el('status').textContent='Nodo conectado';el('status').className='pill ok';
 }catch(e){el('status').textContent='Sin conexión';el('status').className='pill bad';console.error(e);el('tx-result').textContent='No se pudo conectar: '+e.message;}finally{b.disabled=false;}}
async function lookup(hash){const out=el('tx-result');if(!/^0x[a-fA-F0-9]{64}$/.test(hash)){out.textContent='Hash inválido: debe comenzar con 0x y tener 64 caracteres hexadecimales.';return;}out.textContent='Consultando…';try{const [tx,receipt]=await Promise.all([rpc('eth_getTransactionByHash',[hash]),rpc('eth_getTransactionReceipt',[hash])]);if(!tx){out.textContent='Transacción no encontrada en esta blockchain local.';return;}const pairs=[['Hash',tx.hash],['De',tx.from],['Para',tx.to||'Creación de contrato'],['Valor (ETH)',eth(tx.value)],['Bloque',tx.blockNumber?BigInt(tx.blockNumber).toString():'Pendiente'],['Nonce',BigInt(tx.nonce).toString()],['Gas usado',receipt?.gasUsed?BigInt(receipt.gasUsed).toString():'Pendiente'],['Estado',receipt?.status==='0x1'?'Exitosa':receipt?.status==='0x0'?'Fallida':'Pendiente']];const dl=document.createElement('dl');for(const [k,v] of pairs){dl.append(text('dt',k),text('dd',v,k==='Hash'||k==='De'||k==='Para'?'mono':''));}out.replaceChildren(dl);}catch(e){out.textContent='Error: '+e.message;}}
el('refresh').addEventListener('click',load);el('search-form').addEventListener('submit',e=>{e.preventDefault();lookup(el('hash-input').value.trim());});load();setInterval(load,8000);

// Reconstrucción verificada de transactionsRoot del bloque seleccionado.
let currentMerkle=null;
const fullHash=(value)=>{const code=text('code',value||'—','fullhash');return code;};
const card=(label,value)=>{const d=document.createElement('div');d.className='root-card';d.append(text('small',label),fullHash(value));return d;};
async function loadMerkle(number='latest'){
  const status=el('merkle-status');const roots=el('merkle-roots');const txs=el('merkle-txs');const path=el('merkle-path');
  roots.replaceChildren();txs.replaceChildren();path.replaceChildren();currentMerkle=null;
  status.textContent='Reconstruyendo trie y comprobando las pruebas…';
  try {
    const r=await fetch('/api/merkle?block='+encodeURIComponent(number));const data=await r.json();
    if(!r.ok)throw Error(data.error||'Error al reconstruir el trie');
    currentMerkle=data;
    status.textContent=`Bloque ${data.blockNumber} · ${data.transactionCount} transacciones · `+(data.matches?'Raíz verificada: coincide con Hardhat':'ATENCIÓN: raíz diferente a la del bloque');
    status.className='details '+(data.matches?'verified':'unverified');
    roots.append(card('transactionsRoot · Hardhat',data.expectedRoot),card('transactionsRoot · recalculada',data.calculatedRoot),card('receiptsRoot · Hardhat',data.receiptsRoot),card('stateRoot · Hardhat',data.stateRoot));
    if(!data.entries.length){txs.append(text('p','Este bloque no contiene transacciones. El trie vacío también tiene una raíz verificable.'));return;}
    txs.append(text('h3','Transacciones del trie'));
    for(const entry of data.entries){
      const b=document.createElement('button');b.type='button';b.className='tx-choice';
      b.textContent=`#${entry.index}  ${short(entry.hash,18)} · ${entry.bytes} bytes`;
      b.addEventListener('click',()=>showProof(entry.index));txs.append(b);
    }
    showProof(0);
  }catch(e){status.className='details unverified';status.textContent='No se pudo verificar el bloque: '+e.message;}
}
function showProof(index){
  if(!currentMerkle)return;
  const entry=currentMerkle.entries.find(x=>x.index===index);const proof=currentMerkle.proofs.find(x=>x.index===index);
  const area=el('merkle-path');area.replaceChildren();
  area.append(text('h3',`Ruta de inclusión · transacción #${index}`));
  area.append(text('p',`Clave RLP del índice: ${entry.key} · ${proof.nodeCount} nodos de prueba · `+(proof.verified?'Verificación válida':'Verificación fallida')));
  const flow=document.createElement('div');flow.className='proof-flow';
  flow.append(card('Raíz del trie',currentMerkle.calculatedRoot));
  proof.nodes.forEach(node=>{
    flow.append(text('div','↓','proof-arrow'));
    flow.append(card(`Nodo de prueba ${node.level+1} · ${node.bytes} bytes`,node.hash));
  });
  flow.append(text('div','↓','proof-arrow'));
  flow.append(card('Transacción incluida',entry.hash));
  area.append(flow);
  area.append(text('p','Cada caja identifica un nodo RLP de la prueba de inclusión. La representación es una ruta verificable, no el árbol binario de Bitcoin.'));
}
el('merkle-form').addEventListener('submit',e=>{e.preventDefault();const n=el('merkle-block').value.trim();loadMerkle(n===''?'latest':n);});
