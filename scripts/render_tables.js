const fs=require('fs');const d=require('docx');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,BorderStyle,AlignmentType,PageOrientation,PageBreak,HeadingLevel,VerticalAlign}=d;
const T=JSON.parse(fs.readFileSync('results/tables.json','utf8'));
const FONT='Times New Roman', SZ=19; // 9.5pt
const AVAIL=16838-2*1080;
const none={style:BorderStyle.NONE,size:0,color:'FFFFFF'}, rule={style:BorderStyle.SINGLE,size:6,color:'000000'};
function cell(text,w,{bold=false,italic=false,top=false,bottom=false,span=1,align=AlignmentType.LEFT}={}){
  return new TableCell({width:{size:w,type:WidthType.DXA},columnSpan:span,verticalAlign:VerticalAlign.CENTER,
    borders:{top:top?rule:none,bottom:bottom?rule:none,left:none,right:none},margins:{top:40,bottom:40,left:70,right:70},
    children:[new Paragraph({alignment:align,spacing:{line:240},children:[new TextRun({text:String(text),font:FONT,size:SZ,bold,italics:italic})]})]});
}
function table(t){
  const tot=t.widths.reduce((a,b)=>a+b,0); const W=t.widths.map(x=>Math.floor(x/tot*AVAIL)); W[W.length-1]+=AVAIL-W.reduce((a,b)=>a+b,0);
  const rows=[new TableRow({tableHeader:true,children:t.cols.map((c,i)=>cell(c,W[i],{top:true,bottom:true,italic:['p','n','b','SE','z','R²'].includes(c),align:i?AlignmentType.CENTER:AlignmentType.LEFT}))})];
  t.rows.forEach((r,k)=>{const last=k===t.rows.length-1;
    if(!Array.isArray(r)) rows.push(new TableRow({children:[cell(r.group,AVAIL,{italic:true,span:t.cols.length,bottom:last})]}));
    else rows.push(new TableRow({children:r.map((v,i)=>cell(v,W[i],{bottom:last,bold:String(r[0]).includes('(preferred)')||r[0]==='Global',align:i?AlignmentType.CENTER:AlignmentType.LEFT}))}));});
  return [new Paragraph({spacing:{before:0,after:60},children:[new TextRun({text:t.id,font:FONT,size:24,bold:true})]}),
          new Paragraph({spacing:{after:160},children:[new TextRun({text:t.title,font:FONT,size:24,italics:true})]}),
          new Table({width:{size:AVAIL,type:WidthType.DXA},columnWidths:W,rows}),
          new Paragraph({spacing:{before:120,after:0,line:240},children:[new TextRun({text:'Note. ',font:FONT,size:SZ,italics:true}),new TextRun({text:t.note,font:FONT,size:SZ})]})];
}
function doc(list,heading){const ch=[new Paragraph({heading:HeadingLevel.HEADING_1,spacing:{after:240},children:[new TextRun({text:heading,font:FONT,size:28,bold:true,color:'000000'})]})];
  list.forEach((t,i)=>{ if(i>0) ch.push(new Paragraph({children:[new PageBreak()]})); ch.push(...table(t));});
  return new Document({styles:{default:{document:{run:{font:FONT,size:22}}}},sections:[{properties:{page:{size:{width:11906,height:16838,orientation:PageOrientation.LANDSCAPE},margin:{top:1080,bottom:1080,left:1080,right:1080}}},children:ch}]});}
(async()=>{
 fs.writeFileSync('manuscript/Tables_Main_APA.docx',await Packer.toBuffer(doc(T.filter(t=>t.main),'Main Text Tables')));
 fs.writeFileSync('manuscript/Tables_Supplementary_APA.docx',await Packer.toBuffer(doc(T.filter(t=>!t.main),'Supplementary Tables S1–S22')));
 console.log('ok');})();
