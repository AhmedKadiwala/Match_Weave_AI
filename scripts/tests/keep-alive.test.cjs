const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=readFileSync(path.join(__dirname,'../../GOOGLE_KEEP_ALIVE.gs'),'utf8');
function run(status,body,url='https://valid-api.onrender.com'){
 const calls=[];const context={UrlFetchApp:{fetch:(...args)=>{calls.push(args);return{getResponseCode:()=>status,getContentText:()=>body}}},console:{log:()=>{}},Date};
 vm.createContext(context);vm.runInContext(source.replace('https://YOUR-ACTUAL-BACKEND.onrender.com',url),context);
 return {calls,invoke:()=>vm.runInContext('pingBackend()',context)};
}
test('one health GET only, never inference; HTTP 200 JSON status checked',()=>{const r=run(200,'{"status":"ok","deployment":"render"}');assert.equal(r.invoke().status,200);assert.equal(r.calls.length,1);assert.equal(r.calls[0][0],'https://valid-api.onrender.com/api/health');assert.equal(r.calls[0][1].method,'get');});
test('non-200 health is a failed execution',()=>assert.throws(run(503,'waking').invoke,/HTTP 503/));
test('HTML cold-start screen is not counted as healthy',()=>assert.throws(run(200,'<html>starting</html>').invoke,/not JSON/));
test('unhealthy JSON is rejected',()=>assert.throws(run(200,'{"status":"error"}').invoke,/did not report/));
test('unconfigured URL sends no request',()=>{const r=run(200,'{}','https://YOUR-ACTUAL-BACKEND.onrender.com');assert.throws(r.invoke,/Replace/);assert.equal(r.calls.length,0);});
