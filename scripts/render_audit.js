const fs=require('fs');const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,BorderStyle,AlignmentType,HeadingLevel,PageOrientation,LevelFormat}=require('docx');
const F='Times New Roman';const W=16838-2*1000;
const none={style:BorderStyle.NONE,size:0,color:'FFFFFF'},rule={style:BorderStyle.SINGLE,size:6,color:'000000'},hair={style:BorderStyle.SINGLE,size:2,color:'BFBFBF'};
const P=(t,o={})=>new Paragraph({spacing:{after:120,line:276},...o.p,children:(Array.isArray(t)?t:[t]).map(x=>typeof x==='string'?new TextRun({text:x,font:F,size:o.size||22}):new TextRun({font:F,size:o.size||22,...x}))});
const H=(t,l=1)=>new Paragraph({heading:l===1?HeadingLevel.HEADING_1:HeadingLevel.HEADING_2,spacing:{before:240,after:120},children:[new TextRun({text:t,font:F,bold:true,size:l===1?28:24,color:'000000'})]});
const B=(t)=>new Paragraph({numbering:{reference:'b',level:0},spacing:{after:80,line:264},children:(Array.isArray(t)?t:[t]).map(x=>typeof x==='string'?new TextRun({text:x,font:F,size:21}):new TextRun({font:F,size:21,...x}))});
function cell(t,w,{head=false,last=false}={}){return new TableCell({width:{size:w,type:WidthType.DXA},borders:{top:head?rule:none,bottom:head?rule:(last?rule:hair),left:none,right:none},margins:{top:50,bottom:50,left:70,right:70},
 children:[new Paragraph({spacing:{line:240},children:[new TextRun({text:t,font:F,size:18,bold:head})]})]});}
function tbl(cols,rows,wr){const tot=wr.reduce((a,b)=>a+b);const w=wr.map(x=>Math.floor(x/tot*W));w[w.length-1]+=W-w.reduce((a,b)=>a+b);
 return new Table({width:{size:W,type:WidthType.DXA},columnWidths:w,rows:[new TableRow({tableHeader:true,children:cols.map((c,i)=>cell(c,w[i],{head:true}))}),...rows.map((r,k)=>new TableRow({cantSplit:true,children:r.map((c,i)=>cell(c,w[i],{last:k===rows.length-1}))}))]});}
const A=JSON.parse(fs.readFileSync('results/audit.json','utf8'));
const ch=[];
ch.push(new Paragraph({spacing:{after:80},children:[new TextRun({text:'Methodological Audit, Statistical Methods and Reviewer-Response Dossier',font:F,size:32,bold:true})]}));
ch.push(P([{text:'Global NTD and malaria burden, spatial structure and the economics of development-assistance cuts. Prepared 7 October 2026.',italics:true}]));
ch.push(H('1. Bottom line'));
A.summary.forEach(s=>ch.push(B(s)));
ch.push(H('2. Issue-by-issue audit'));
ch.push(P('Each row is a criticism a statistical, econometric or spatial reviewer would plausibly raise, how it was tested in the data, what was found, and what was changed. Rows marked FIXED changed numbers in the manuscript.',{size:21}));
ch.push(tbl(['#','Potential flaw / reviewer comment','How it was tested','Finding','Action and status'],A.audit,[0.3,2.2,2.2,2.6,2.6]));
ch.push(H('3. Statistical analysis (manuscript-ready methods text)'));
A.methods.forEach(([h,t])=>{ch.push(H(h,2)); t.forEach(x=>ch.push(P(x,{size:21})));});
ch.push(H('4. Limitations that cannot be fixed with available data'));
A.limits.forEach(s=>ch.push(B(s)));
ch.push(H('5. Figure legends'));
A.legends.forEach(([h,t])=>ch.push(P([{text:h+' ',bold:true},t],{size:21})));
const doc=new Document({numbering:{config:[{reference:'b',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:360,hanging:260}}}}]}]},
 sections:[{properties:{page:{size:{width:11906,height:16838,orientation:PageOrientation.LANDSCAPE},margin:{top:1000,bottom:1000,left:1000,right:1000}}},children:ch}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('manuscript/Methods_Audit_and_Reviewer_Responses.docx',b);console.log('ok')});
