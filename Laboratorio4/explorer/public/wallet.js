(() => {
const q=id=>document.getElementById(id);
const select=q('wallet-account'), status=q('wallet-state'), message=q('wallet-message'), result=q('wallet-result');
let context;const selected=()=>q('contract-selector').value;
const setStatus=(s)=>{status.textContent=s};
function renderAccounts(data){
 context=data; select.replaceChildren();
 for(const a of data.accounts){const opt=document.createElement('option');opt.value=a.address;opt.textContent=`${a.isOwner?'[Propietario] ':'[Otra cuenta] '}${a.address} · ${a.balanceEth} ETH`;select.append(opt)}
 const owner=data.accounts.find(a=>a.isOwner);if(owner)select.value=owner.address;
 balance();setStatus(`Red ${data.network} · ${data.accounts.length} cuentas ficticias`);
}
function balance(){const a=context?.accounts.find(a=>a.address===select.value);q('wallet-balance').textContent=a?`Saldo ${a.balanceEth} ETH · ${a.isOwner?'Propietario':context.restricted?'Sin autorización: el contrato seguro debe rechazar':'Puede escribir: contrato sin control de acceso'}`:'Sin cuentas';q('wallet-submit').disabled=!a;}
async function refresh(){q('wallet-refresh').disabled=true;setStatus('Consultando...');try{const r=await fetch('/api/wallet?contract='+encodeURIComponent(selected()),{cache:'no-store'});const d=await r.json();if(!r.ok)throw Error(d.details||d.error);renderAccounts(d)}catch(e){setStatus(`Error: ${e.message}`)}finally{q('wallet-refresh').disabled=false}}
q('wallet-refresh').addEventListener('click',refresh);select.addEventListener('change',balance);
q('wallet-form').addEventListener('submit',async ev=>{
 ev.preventDefault();if(!context)return;
 const a=context.accounts.find(a=>a.address===select.value);
 if(!a){result.textContent='Selecciona una cuenta';return;}
 const val=message.value;
 if(!val.trim()||new TextEncoder().encode(val).length>256){result.textContent='Mensaje obligatorio de hasta 256 bytes UTF-8.';return;}
 if(!confirm(`LABORATORIO LOCAL · Hardhat 31337\n\nDesde: ${a.address}\nContrato: ${context.contract} (${context.contractId})\nFunción: actualizarMensaje\nMensaje: ${val}\n\n¿Confirmas enviar la transacción?`))return;
 q('wallet-submit').disabled=true;result.textContent='Enviando transacción de prueba…';
 try{const r=await fetch('/api/wallet/update?contract='+encodeURIComponent(selected()),{method:'POST',headers:{'Content-Type':'application/json','X-Lab-Action':'confirm'},body:JSON.stringify({cuenta:a.address,mensaje:val})});const d=await r.json();if(!r.ok)throw Error(`${d.error||'Error'} ${d.details||''}${d.txHash?' · Hash: '+d.txHash:''}`);result.textContent=`${d.status===1?'CONFIRMADA':'REVERTIDA'} en bloque ${d.blockNumber} · TX: ${d.txHash} · ${d.explanation} · Mensaje: ${d.mensaje} · Contador: ${d.contador} · Eventos: ${d.events?.length??0}`;message.value='';await Promise.all([refresh(),typeof window.loadContract==='function'?window.loadContract():Promise.resolve()]);}
 catch(e){result.textContent=`Error: ${e.message}`;}finally{balance()}
});
window.refreshWallet=refresh;refresh();
})();
