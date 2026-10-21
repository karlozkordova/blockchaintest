import { inspectTransactions } from './merkle.mjs';
import { ethers } from 'ethers';
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const port = Number(process.env.PORT || 8080);
const CONTRACTS = Object.freeze({
  seguro: {deploymentPath:'/data/scripts/deployment.json',sourcePath:'/data/contracts/RegistroAcademico.sol'},
  vulnerable: {deploymentPath:'/data/scripts/deployment-vulnerable.json',sourcePath:'/data/contracts/RegistroAcademicoVulnerable.sol'}
});
function selectedContract(url){
  const id=url.searchParams.get('contract') || 'seguro';
  if(!Object.hasOwn(CONTRACTS,id))throw Error('Contrato no permitido');
  return {id,...CONTRACTS[id]};
}
function checkLocal(req,isWrite=false){
 const host=String(req.headers.host||'').toLowerCase();
 if(!['localhost:3000','127.0.0.1:3000'].includes(host))return 'Acceso solo desde localhost:3000';
 if(isWrite && (!['http://localhost:3000','http://127.0.0.1:3000'].includes(req.headers.origin)||req.headers['x-lab-action']!=='confirm'))return 'Origen o confirmación no válidos';
 return null;
}
const rpcUrl = process.env.RPC_URL || 'http://blockchain:8545';
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), 'public');
const mime = {'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8'};
const allowed = new Set(['eth_chainId','eth_blockNumber','eth_accounts','eth_getBalance','eth_getBlockByNumber','eth_getTransactionByHash','eth_getTransactionReceipt','web3_clientVersion','eth_getTransactionCount']);
function json(res,status,payload){res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(payload));}
const server=http.createServer(async(req,res)=>{
  const url=new URL(req.url||'/', 'http://localhost');
  if(url.pathname==='/api/contract') {
    if(req.method!=='GET')return json(res,405,{error:'Solo GET'});
    try {
      const target=selectedContract(url);
      const deployment=JSON.parse(await readFile(target.deploymentPath,'utf8'));
      if(!ethers.isAddress(deployment.address) || !Array.isArray(deployment.abi))throw Error('deployment.json inválido');
      const provider=new ethers.JsonRpcProvider(rpcUrl);
      const network=await provider.getNetwork();
      if(network.chainId!==31337n)throw Error('Este panel solo admite Hardhat local (31337)');
      if(deployment.chainId!=null && Number(deployment.chainId)!==31337)throw Error('El despliegue pertenece a otra red');
      const code=await provider.getCode(deployment.address);
      if(code==='0x')return json(res,409,{error:'No hay contrato en esa dirección. Hardhat pudo haberse reiniciado; vuelve a desplegar.'});
      const receipt=deployment.txHash?await provider.getTransactionReceipt(deployment.txHash):null;
      if(!receipt || receipt.contractAddress?.toLowerCase()!==deployment.address.toLowerCase()) {
        return json(res,409,{error:'La dirección no corresponde al despliegue registrado en esta cadena; actualiza deployment.json.'});
      }
      const iface=new ethers.Interface(deployment.abi);
      const contract=new ethers.Contract(deployment.address,deployment.abi,provider);
      const functions={};
      for(const name of ['propietario','mensaje','contador']){
        if(!iface.hasFunction(name))continue;
        const value=await contract[name]();
        functions[name]=typeof value==='bigint'?value.toString():value;
      }
      const latest=await provider.getBlockNumber();
      const start=Math.max(Number(receipt.blockNumber),latest-2000);
      const event=iface.hasEvent('MensajeActualizado')?iface.getEvent('MensajeActualizado'):null;
      const logs=event?await provider.getLogs({address:deployment.address,topics:[event.topicHash],fromBlock:start,toBlock:latest}):[];
      const events=logs.slice(-50).reverse().map(log=>{
        const parsed=iface.parseLog(log);
        return {transactionHash:log.transactionHash,blockNumber:log.blockNumber,usuario:String(parsed.args[0]),nuevoMensaje:String(parsed.args[1]),contador:String(parsed.args[2])};
      });
      let source=null;
      try{source=await readFile(target.sourcePath,'utf8');}catch{}
      const functionsABI=deployment.abi.filter(item=>item.type==='function');
      const eventsABI=deployment.abi.filter(item=>item.type==='event');
      return json(res,200,{
        contractId:target.id,network:31337,address:deployment.address,blockNumber:receipt.blockNumber,txHash:receipt.hash,
        deployer:deployment.deployer||null,functions,functionsABI,eventsABI,events,
        latestBlock:latest,source,sourceLabel:'Archivo local (no recuperado de la blockchain)',
        bytecodePresent:true,bytecodeMatches:typeof deployment.deployedBytecode==='string'?code.toLowerCase()===deployment.deployedBytecode.toLowerCase():null,
        compilerVersion:deployment.compilerVersion||null,eventsFromBlock:start,
        abiSource:'deployment.json local',
      });
    }catch(error){return json(res,502,{error:'No se pudo consultar el contrato',details:error.message});}
  }
  // API de aprendizaje para cuentas desbloqueadas, accesible solo en loopback.
  if(url.pathname==='/api/wallet' || url.pathname==='/api/wallet/update') {
    const isWrite=url.pathname.endsWith('/update');
    if(req.method!==(isWrite?'POST':'GET'))return json(res,405,{error:'Método no permitido'});
    const denied=checkLocal(req,isWrite);
    if(denied)return json(res,403,{error:denied});
    if(isWrite && req.headers['content-type']?.split(';')[0]?.trim()!=='application/json')return json(res,415,{error:'Se requiere application/json'});
    try {
      const target=selectedContract(url);
      const provider=new ethers.JsonRpcProvider(rpcUrl);
      if((await provider.getNetwork()).chainId!==31337n)throw Error('Solo Hardhat local 31337');
      const deployment=JSON.parse(await readFile(target.deploymentPath,'utf8'));
      if(!ethers.isAddress(deployment.address)||!Array.isArray(deployment.abi))throw Error('Despliegue inválido');
      if(deployment.chainId!=null&&Number(deployment.chainId)!==31337)throw Error('Red del despliegue incorrecta');
      const receipt=deployment.txHash?await provider.getTransactionReceipt(deployment.txHash):null;
      if(!receipt||receipt.contractAddress?.toLowerCase()!==deployment.address.toLowerCase())return json(res,409,{error:'Despliegue ausente de la cadena activa'});
      if(await provider.getCode(deployment.address)==='0x')return json(res,409,{error:'Contrato sin bytecode'});
      const contract=new ethers.Contract(deployment.address,deployment.abi,provider);
      const owner=await contract.propietario();
      const accounts=await provider.send('eth_accounts',[]);
      if(!Array.isArray(accounts))throw Error('Cuentas Hardhat no disponibles');
      const isOwner=a=>a.toLowerCase()===owner.toLowerCase();
      if(!isWrite){
        const view=await Promise.all(accounts.map(async address=>({address,balanceEth:ethers.formatEther(await provider.getBalance(address)),isOwner:isOwner(address)})));
        return json(res,200,{network:31337,contractId:target.id,contract:deployment.address,owner,restricted:target.id==='seguro',accounts:view,notice:'SOLO LABORATORIO LOCAL. La selección de cuenta no autentica al usuario.'});
      }
      let body='';
      for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>4096)return json(res,413,{error:'Solicitud demasiado grande'});}
      let payload;try{payload=JSON.parse(body);}catch{return json(res,400,{error:'JSON inválido'});}
      const message=payload?.mensaje,sender=payload?.cuenta;
      if(typeof message!=='string'||!message.trim()||Buffer.byteLength(message,'utf8')>256)return json(res,400,{error:'Mensaje obligatorio de hasta 256 bytes UTF-8'});
      if(typeof sender!=='string'||!ethers.isAddress(sender)||!accounts.some(a=>a.toLowerCase()===sender.toLowerCase()))return json(res,400,{error:'Selecciona una cuenta desbloqueada de Hardhat'});
      const from=ethers.getAddress(sender);
      const iface=new ethers.Interface(deployment.abi);
      if(!iface.hasFunction('actualizarMensaje'))throw Error('El contrato no tiene actualizarMensaje');
      const data=iface.encodeFunctionData('actualizarMensaje',[message]);
      // Importante: el contrato seguro debe poder demostrar el REVERT de una cuenta no propietaria.
      // Se envía únicamente esta función predefinida y nunca datos EVM arbitrarios del cliente.
      const txHash=await provider.send('eth_sendTransaction',[{from,to:deployment.address,data,gas:'0x493e0'}]);
      const txReceipt=await provider.waitForTransaction(txHash,1,30000);
      if(!txReceipt)return json(res,504,{error:'Transacción enviada pero aún sin recibo',txHash});
      const events=[];
      if(txReceipt.status===1){for(const log of txReceipt.logs){try{const ev=iface.parseLog(log);if(ev?.name==='MensajeActualizado')events.push({usuario:String(ev.args[0]),nuevoMensaje:String(ev.args[1]),contador:String(ev.args[2])});}catch{}}}
      return json(res,200,{contractId:target.id,txHash,blockNumber:txReceipt.blockNumber,status:txReceipt.status,authorized:isOwner(from),mensaje:await contract.mensaje(),contador:String(await contract.contador()),events,explanation:txReceipt.status===0?'Transacción revertida por la EVM; el estado no cambió.':isOwner(from)?'Actualización por propietario.':'Una cuenta no propietaria actualizó el contrato: ausencia de control de acceso.'});
    }catch(error){return json(res,502,{error:'Error en la wallet local',details:error.message});}
  }
  if(url.pathname==='/api/merkle') {
    if(req.method!=='GET') return json(res,405,{error:'Solo GET'});
    const number=url.searchParams.get('block') ?? 'latest';
    if(!(number==='latest'||/^(0|[1-9][0-9]{0,11})$/.test(number)))return json(res,400,{error:'Número de bloque inválido'});
    try {
      const query=async(method,params=[])=>{
        const r=await fetch(rpcUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params}),signal:AbortSignal.timeout(12000)});
        if(!r.ok)throw Error('Error HTTP del nodo');
        const data=await r.json();if(data.error)throw Error(data.error.message);return data.result;
      };
      const id=number==='latest'?'latest':'0x'+BigInt(number).toString(16);
      const block=await query('eth_getBlockByNumber',[id,true]);
      if(!block)return json(res,404,{error:'Bloque no encontrado'});
      const result=await inspectTransactions(block,hash=>query('eth_getRawTransactionByHash',[hash]));
      return json(res,200,result);
    } catch(error){return json(res,422,{error:error.message});}
  }
  if(url.pathname==='/api/rpc'){
    if(req.method!=='POST') return json(res,405,{error:'Solo POST'});
    let body='';
    try {
      for await(const part of req){body+=part;if(body.length>10000)throw new Error('Solicitud demasiado grande');}
      const {method,params=[]}=JSON.parse(body);
      if(!allowed.has(method) || !Array.isArray(params)) return json(res,400,{error:'Método no permitido o parámetros inválidos'});
      const upstream=await fetch(rpcUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params}),signal:AbortSignal.timeout(7000)});
      const output=await upstream.json();
      if(!upstream.ok) return json(res,502,{error:'Error del nodo',details:output.error?.message});
      return json(res,200,output);
    } catch(error) {return json(res,502,{error:'No se pudo consultar Hardhat',details:error.message});}
  }
  if(req.method!=='GET') return json(res,405,{error:'Método no permitido'});
  const name=url.pathname==='/'?'index.html':url.pathname.slice(1);
  if(!['index.html','app.js','style.css','glossary.js','contract.js','wallet.js'].includes(name))return json(res,404,{error:'No encontrado'});
  try{const file=await readFile(path.join(root,name));res.writeHead(200,{'Content-Type':mime[path.extname(name)],'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(file);}catch{json(res,404,{error:'Archivo no encontrado'});}
});
server.listen(port,'0.0.0.0',()=>console.log(`Explorer en puerto ${port}; RPC: ${rpcUrl}`));
