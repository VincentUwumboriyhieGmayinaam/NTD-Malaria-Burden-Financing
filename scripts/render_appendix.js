const fs=require('fs');const d=require('docx');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,BorderStyle,AlignmentType,PageOrientation,HeadingLevel,
  VerticalAlign,ImageRun,Footer,Header,PageNumber,PageBreak,TabStopType,TabStopPosition,LevelFormat}=d;
const A=JSON.parse(fs.readFileSync('results/appendix.json','utf8'));
const FONT='Times New Roman', SZ=16; // Lancet: tables 8 pt, text 10 pt, main heading 12 pt
const PG=fs.existsSync('results/appendix_toc_pages.json')?JSON.parse(fs.readFileSync('results/appendix_toc_pages.json','utf8')):{};
const minus=s=>String(s).replace(/(^|[\s\[(;,=])-(?=\d)/g,'$1−')
  .replace(/(^|[^\w\/.])(\d+)\.(\d+)(?![\w\/]*\.[a-z])(?![\/\d])/g,(m,a,b,c,off,str)=>/(appendix|Appendix|sections?|SDG|Goal) $/.test(str.slice(Math.max(0,off-12),off+a.length))||/https?:|doi/.test(str.slice(Math.max(0,off-80),off))?m:`${a}${b}·${c}`)
  .replace(/^—$/,'··');
// runs with superscript citation markers ^{1,2}
const RUNS=(t,o)=>{const out=[];String(t).split(/(\^\{[^}]*\})/).forEach(seg=>{if(!seg)return;const sup=seg.startsWith('^{');out.push(new TextRun({...o,text:sup?seg.slice(2,-1):(o.raw?seg:minus(seg)),superScript:sup}));});return out;};
const P=(text,o={})=>new Paragraph({spacing:{after:o.after??120,line:o.line??240},alignment:o.align??AlignmentType.JUSTIFIED,keepNext:o.keepNext,
  children:(Array.isArray(text)?text:[[text,{}]]).flatMap(([t,f])=>RUNS(t,{font:FONT,size:o.size??20,bold:f.b,italics:f.i,raw:o.raw}))});
const H=(text,lvl)=>new Paragraph({heading:lvl==='TITLE'?HeadingLevel.HEADING_1:lvl,spacing:{before:lvl===HeadingLevel.HEADING_1?240:180,after:120},keepNext:true,
  children:[new TextRun({text,font:FONT,size:lvl==='TITLE'?24:20,bold:true,color:'000000'})]});
const none={style:BorderStyle.NONE,size:0,color:'FFFFFF'}, rule={style:BorderStyle.SINGLE,size:6,color:'000000'};
function cell(text,w,{bold=false,italic=false,top=false,bottom=false,span=1,align=AlignmentType.LEFT,size=SZ,raw=false}={}){
  return new TableCell({width:{size:w,type:WidthType.DXA},columnSpan:span,verticalAlign:VerticalAlign.CENTER,
    borders:{top:top?rule:none,bottom:bottom?rule:none,left:none,right:none},margins:{top:30,bottom:30,left:60,right:60},
    children:[new Paragraph({alignment:align,spacing:{line:240},children:RUNS(text,{font:FONT,size,bold,italics:italic,raw:raw})})]});}
function apaTable(t,AV,size=SZ){
  const tot=t.widths.reduce((a,b)=>a+b,0); const W=t.widths.map(x=>Math.floor(x/tot*AV)); W[W.length-1]+=AV-W.reduce((a,b)=>a+b,0);
  const rows=[new TableRow({tableHeader:true,children:t.cols.map((c,i)=>cell(c,W[i],{top:true,bottom:true,bold:true,italic:['p','n','b','SE','z'].includes(c),align:(i&&!t.left)?AlignmentType.CENTER:AlignmentType.LEFT,size}))})];
  t.rows.forEach((r,k)=>{const last=k===t.rows.length-1;
    if(!Array.isArray(r)) rows.push(new TableRow({cantSplit:true,children:[cell(r.group,AV,{italic:true,span:t.cols.length,bottom:last,size})]}));
    else rows.push(new TableRow({cantSplit:true,children:r.map((v,i)=>cell(v,W[i],{bottom:last,align:(i&&!t.left)?AlignmentType.CENTER:AlignmentType.LEFT,size,raw:!!t.left}))}));});
  const out=[new Paragraph({keepNext:true,spacing:{before:0,after:40},children:[new TextRun({text:t.id,font:FONT,size:20,bold:true})]}),
    new Paragraph({keepNext:true,spacing:{after:100},children:[new TextRun({text:t.title,font:FONT,size:20,bold:true})]}),
    new Table({width:{size:AV,type:WidthType.DXA},columnWidths:W,rows})];
  if(t.note) out.push(new Paragraph({spacing:{before:80,after:0,line:240},children:[new TextRun({text:'Note. ',font:FONT,size:20,italics:true}),...RUNS(t.note,{font:FONT,size:20})]}));
  return out;}
const footer=new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({font:FONT,size:18,children:['Page ',PageNumber.CURRENT]})]})]});
const header=new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,children:[new TextRun({text:'Supplementary appendix — NTD and malaria burden, inequality and external financing',font:FONT,size:16,color:'666666'})]})]});
const portrait={page:{size:{width:11906,height:16838},margin:{top:1200,bottom:1200,left:1200,right:1200}}};
const landscape={page:{size:{width:11906,height:16838,orientation:PageOrientation.LANDSCAPE},margin:{top:1000,bottom:1000,left:1000,right:1000}}};
const AVP=11906-2400, AVL=16838-2000;
// ---- front matter
const front=[
  P([['Supplementary appendix to: Gmayinaam VU, Nortey AN, Dzissem PE, Immurana M, Manyeh AK. Global, regional and national inequalities in neglected tropical disease and malaria burden and the consequences of development-assistance cuts: a spatial and panel analysis of GBD 2023.',{}]],{size:20}),
  H('Supplementary appendix','TITLE'),
  H('Contents',HeadingLevel.HEADING_2)];
const TL=(txt,key,o={})=>new Paragraph({tabStops:[{type:TabStopType.RIGHT,position:AVP-10,leader:'dot'}],spacing:{after:o.after??30,line:240},indent:{left:o.indent??0,hanging:o.hang??0},
  children:[new TextRun({text:txt,font:FONT,size:20,bold:o.b}),new TextRun({text:'\t'+(PG[key]??'00'),font:FONT,size:20,bold:o.b})]});
const TOC=[['1. Reporting checklists: GATHER and STROBE','1. Reporting checklists'],['2. Evidence before this study: search strategy and evidence map','2. Evidence before this study'],['3. Detailed statistical methods','3. Detailed statistical methods'],
  ['4. Supplementary tables','4. Supplementary tables'],['5. Supplementary figures','5. Supplementary figures'],['6. References','6. References']];
const tocKeys=[];
TOC.forEach(([t,k],i)=>{front.push(TL(t,k,{b:true,after:30})); tocKeys.push(k);
  if(i===2) A.methods.forEach(([h])=>{front.push(TL(h,h,{indent:360})); tocKeys.push(h);});
  if(i===3) A.tables.forEach(t=>{front.push(TL(`${t.id}. ${t.title}`,t.id,{indent:720,hang:360})); tocKeys.push(t.id);});
  if(i===4) A.figures.forEach(f=>{front.push(TL(`${f[0]}. ${f[2]}`,f[0],{indent:720,hang:360})); tocKeys.push(f[0]);});});
fs.writeFileSync('results/appendix_toc_keys.json',JSON.stringify(tocKeys));
// ---- 1 GATHER
const g=[H('1. Reporting checklists: GATHER and STROBE',HeadingLevel.HEADING_1),P('The study produces health estimates and projections (GATHER) from an ecological observational design (STROBE). Locations refer to the main text, appendix sections and supplementary tables; items that do not apply are justified.'),
  ...apaTable({id:'GATHER checklist',left:true,title:'Guidelines for Accurate and Transparent Health Estimates Reporting (GATHER)',cols:['Item','Checklist item','Where reported'],
   rows:A.gather.map(r=>[r[0],r[1],r[2]]),widths:[0.6,5.4,3.0],note:'Stevens GA, et al. Guidelines for accurate and transparent health estimates reporting: the GATHER statement. Lancet 2016; 388: e19–23.'},AVP,SZ),
  new Paragraph({children:[new PageBreak()]}),
  ...apaTable({id:'STROBE checklist',left:true,title:'STROBE Statement: Checklist of Items for Ecological and Cross-Sectional Observational Studies',cols:['Item','Section','Recommendation','Where reported or justification'],
   rows:A.strobe,widths:[0.5,1.5,3.6,3.4],note:'von Elm E, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. Lancet 2007; 370: 1453–57. The unit of analysis is the country or territory, so participant items refer to countries.'},AVP,SZ)];
// ---- 3 methods (portrait)
const meth=[H('3. Detailed statistical methods',HeadingLevel.HEADING_1),
  P('This section gives the full specification of every analysis summarised in the main text. Formulae are described in words.',{})];
A.methods.forEach(([h,ps])=>{meth.push(H(h,HeadingLevel.HEADING_2)); ps.forEach(p=>meth.push(P(p)));});
// ---- 2 evidence (landscape)
const ev=[H('2. Evidence before this study: search strategy and evidence map',HeadingLevel.HEADING_1),P(A.search),...apaTable(A.evidence,AVL,16)];
if(A.other){ev.push(H('Other eligible studies (not tabulated)',HeadingLevel.HEADING_2)); A.other.split('\n').forEach(l=>ev.push(P(l.replace(/\*\*/g,'').replace(/^- /,''),{size:18,after:60})));}
// ---- 4 tables (landscape)
const tb=[H('4. Supplementary tables',HeadingLevel.HEADING_1)];
A.tables.forEach((t,i)=>{ if(i>0) tb.push(new Paragraph({children:[new PageBreak()]})); tb.push(...apaTable(t,AVL,t.rows.length>40?16:SZ));});
// ---- 5 figures (portrait)
const fg=[H('5. Supplementary figures',HeadingLevel.HEADING_1)];
A.figures.forEach(([id,file,title,legend],i)=>{
  const buf=fs.readFileSync('figures/supplementary/'+file); const w=buf.readUInt32BE(16), h=buf.readUInt32BE(20);
  const W=620, Hh=Math.round(W*h/w);
  if(i>0) fg.push(new Paragraph({children:[new PageBreak()]}));
  fg.push(new Paragraph({keepNext:true,spacing:{after:80},children:[new TextRun({text:id+': ',font:FONT,size:20,bold:true}),new TextRun({text:title,font:FONT,size:20,bold:true})]}));
  fg.push(new Paragraph({keepNext:true,alignment:AlignmentType.CENTER,children:[new ImageRun({type:'png',data:buf,transformation:{width:W,height:Hh},altText:{title:id,description:title,name:id}})]}));
  fg.push(P(legend,{size:20}));});
// ---- 6 references
const refs=[H('6. References',HeadingLevel.HEADING_1)];
A.references.forEach((r,i)=>refs.push(new Paragraph({spacing:{after:60,line:240},tabStops:[{type:TabStopType.LEFT,position:500}],indent:{left:500,hanging:500},children:[new TextRun({text:`${i+1}\t${r}`,font:FONT,size:20})]})));
const sec=(props,children)=>({properties:props,headers:{default:header},footers:{default:footer},children});
const doc=new Document({styles:{default:{document:{run:{font:FONT,size:22}}}},sections:[
  sec(portrait,[...front,new Paragraph({children:[new PageBreak()]}),...g]), sec(landscape,ev), sec(portrait,meth), sec(landscape,tb), sec(portrait,[...fg,new Paragraph({children:[new PageBreak()]}),...refs])]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('manuscript/Supplementary_Appendix.docx',b);console.log('ok');});
