const fs=require('fs');
const m=JSON.parse(fs.readFileSync('manifest.json','utf8')).filter(x=>!x.brandingFlag&&fs.existsSync(x.file));
const slim=m.map(x=>({s:x.slug,f:x.file,t:x.title,c:x.category,d:x.description,k:x.sizeKB,v:x.variantOf,e:!!x.hasEditor,p:!!x.hasPreview,h:!!x.hasChat,g:x.engine,l:x.loads,j:x.jsErrors,m:!!x.mobileOk,x:!!x.mobileScrollX,n:x.notes||'',bad:(x.endpoints||[]).filter(e=>!e.status||e.status>=400).map(e=>e.host)}));
fs.writeFileSync('index.html',fs.readFileSync('template.html','utf8').replace('/*DATA*/',()=>JSON.stringify(slim).replace(/<\//g,'<\/')));
console.log(slim.length,'Eintraege');
