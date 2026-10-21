const fs=require('fs');const d=require('docx');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,BorderStyle,AlignmentType,PageOrientation,HeadingLevel,
  VerticalAlign,ImageRun,Footer,Header,PageNumber,PageBreak,TabStopType,TabStopPosition,LevelFormat}=d;
const A=JSON.parse(fs.readFileSync('results/appendix.json','utf8'));
const FONT='Times New Roman', SZ=19;
const minus=s=>String(s).replace(/(^|[\s\[(;,=])-(?=\d)/g,'$1−');
const P=(text,o={})=>new Paragraph({spacing:{after:o.after??140,line:o.line??300},alignment:o.align??AlignmentType.JUSTIFIED,keepNext:o.keepNext,
  children:(Array.isArray(text)?text:[[text,{}]]).map(([t,f])=>new TextRun({text:minus(t),font:FONT,size:o.size??22,bold:f.b,italics:f.i}))});
const H=(text,lvl)=>new Paragraph({heading:lvl,spacing:{before:lvl===HeadingLevel.HEADING_1?240:180,after:120},keepNext:true,
  children:[new TextRun({text,font:FONT,size:lvl===HeadingLevel.HEADING_1?28:24,bold:true,color:'000000'})]});
const none={style:BorderStyle.NONE,size:0,color:'FFFFFF'}, rule={style:BorderStyle.SINGLE,size:6,color:'000000'};
function cell(text,w,{bold=false,italic=false,top=false,bottom=false,span=1,align=AlignmentType.LEFT,size=SZ}={}){
  return new TableCell({width:{size:w,type:WidthType.DXA},columnSpan:span,verticalAlign:VerticalAlign.CENTER,
    borders:{top:top?rule:none,bottom:bottom?rule:none,left:none,right:none},margins:{top:30,bottom:30,left:60,right:60},
    children:[new Paragraph({alignment:align,spacing:{line:228},children:[new TextRun({text:minus(text),font:FONT,size,bold,italics:italic})]})]});}
function apaTable(t,AV,size=SZ){
  const tot=t.widths.reduce((a,b)=>a+b,0); const W=t.widths.map(x=>Math.floor(x/tot*AV)); W[W.length-1]+=AV-W.reduce((a,b)=>a+b,0);
  const rows=[new TableRow({tableHeader:true,children:t.cols.map((c,i)=>cell(c,W[i],{top:true,bottom:true,italic:['p','n','b','SE','z'].includes(c),align:i?AlignmentType.CENTER:AlignmentType.LEFT,size}))})];
  t.rows.forEach((r,k)=>{const last=k===t.rows.length-1;
    if(!Array.isArray(r)) rows.push(new TableRow({cantSplit:true,children:[cell(r.group,AV,{italic:true,span:t.cols.length,bottom:last,size})]}));
    else rows.push(new TableRow({cantSplit:true,children:r.map((v,i)=>cell(v,W[i],{bottom:last,align:i?AlignmentType.CENTER:AlignmentType.LEFT,size}))}));});
  const out=[new Paragraph({keepNext:true,spacing:{before:0,after:60},children:[new TextRun({text:t.id,font:FONT,size:24,bold:true})]}),
    new Paragraph({keepNext:true,spacing:{after:140},children:[new TextRun({text:t.title,font:FONT,size:24,italics:true})]}),
    new Table({width:{size:AV,type:WidthType.DXA},columnWidths:W,rows})];
  if(t.note) out.push(new Paragraph({spacing:{before:100,after:0,line:240},children:[new TextRun({text:'Note. ',font:FONT,size:SZ,italics:true}),new TextRun({text:minus(t.note),font:FONT,size:SZ})]}));
  return out;}
const footer=new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({font:FONT,size:18,children:['Page ',PageNumber.CURRENT]})]})]});
const header=new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,children:[new TextRun({text:'Supplementary appendix — NTD and malaria burden, inequality and external financing',font:FONT,size:16,color:'666666'})]})]});
const portrait={page:{size:{width:11906,height:16838},margin:{top:1200,bottom:1200,left:1200,right:1200}}};
const landscape={page:{size:{width:11906,height:16838,orientation:PageOrientation.LANDSCAPE},margin:{top:1000,bottom:1000,left:1000,right:1000}}};
const AVP=11906-2400, AVL=16838-2000;
// ---- front matter
const front=[
  P([['Supplementary appendix to: Gmayinaam VU, Nortey AN, Dzissem PE, Immurana M, Manyeh AK. Global, regional and national inequalities in neglected tropical disease and malaria burden and the consequences of development-assistance cuts: a spatial and panel analysis of GBD 2023.',{}]],{size:20}),
  H('Supplementary appendix',HeadingLevel.HEADING_1),
  H('Contents',HeadingLevel.HEADING_2)];
const toc=[['1','GATHER checklist'],['2','Evidence before this study: search strategy and evidence map (Table E1)'],['3','Detailed statistical methods (3.1–3.15)'],
  ['4','Supplementary tables S1–S24'],['5','Supplementary figures S1–S4'],['6','References']];
toc.forEach(([n,t])=>front.push(P([[`${n}   ${t}`,{}]],{align:AlignmentType.LEFT,after:60})));
front.push(P([['Supplementary tables',{b:true}]],{after:60,align:AlignmentType.LEFT}));
A.tables.forEach(t=>front.push(P([[`${t.id}. ${t.title}`,{}]],{size:19,after:20,line:240,align:AlignmentType.LEFT})));
front.push(P([['Supplementary figures',{b:true}]],{after:60,align:AlignmentType.LEFT}));
A.figures.forEach(f=>front.push(P([[`${f[0]}. ${f[2]}`,{}]],{size:19,after:20,line:240,align:AlignmentType.LEFT})));
// ---- 1 GATHER
const g=[H('1. GATHER checklist',HeadingLevel.HEADING_1),
  ...apaTable({id:'Checklist',title:'Guidelines for Accurate and Transparent Health Estimates Reporting (GATHER)',cols:['Item','Checklist item','Where reported'],
   rows:A.gather.map(r=>[r[0],r[1],r[2]]),widths:[0.6,5.4,3.0],note:'Stevens GA, et al. Guidelines for accurate and transparent health estimates reporting: the GATHER statement. Lancet 2016; 388: e19–23.'},AVP,18)];
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
  fg.push(new Paragraph({keepNext:true,spacing:{after:80},children:[new TextRun({text:id+': ',font:FONT,size:22,bold:true}),new TextRun({text:title,font:FONT,size:22,bold:true})]}));
  fg.push(new Paragraph({keepNext:true,alignment:AlignmentType.CENTER,children:[new ImageRun({type:'png',data:buf,transformation:{width:W,height:Hh},altText:{title:id,description:title,name:id}})]}));
  fg.push(P(legend,{size:20}));});
// ---- 6 references
const refs=[H('6. References',HeadingLevel.HEADING_1)];
JSON.parse(fs.readFileSync('results/appendix_refs.json','utf8')).forEach(r=>refs.push(new Paragraph({spacing:{after:80,line:260},indent:{left:720,hanging:720},children:[new TextRun({text:r,font:FONT,size:19})]})));
const sec=(props,children)=>({properties:props,headers:{default:header},footers:{default:footer},children});
const doc=new Document({styles:{default:{document:{run:{font:FONT,size:22}}}},sections:[
  sec(portrait,[...front,new Paragraph({children:[new PageBreak()]}),...g]), sec(landscape,ev), sec(portrait,meth), sec(landscape,tb), sec(portrait,[...fg,new Paragraph({children:[new PageBreak()]}),...refs])]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('manuscript/Supplementary_Appendix.docx',b);console.log('ok');});
