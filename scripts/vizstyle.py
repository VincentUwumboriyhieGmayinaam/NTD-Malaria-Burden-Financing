"""Shared manuscript figure style (Lancet-ready): Arial-metric sans, 7 pt text, hairline recessive axes,
validated palette (dataviz reference instance), 180 mm double-column width."""
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm, LinearSegmentedColormap
MM=1/25.4; W2=180*MM; W1=88*MM
INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'; GRID='#e1e0d9'; AXIS='#c3c2b7'; NEUTRAL='#f0efec'; NODATA='#d9d8d3'
BLUE='#2a78d6'; ORANGE='#eb6834'; AQUA='#1baf7a'; DEEMPH='#c3c2b7'
BLUE_RAMP=['#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95','#0d366b']
ORANGE_RAMP=['#fde3d6','#f8bfa3','#f39a72','#eb6834','#c94f1f','#9c3a14','#6b260b']
RED='#e34948'; RED_LIGHT='#f4b4b3'; BLUE_LIGHT='#b7d3f6'
def setup():
    mpl.rcParams.update({'font.family':'Liberation Sans','font.size':7,'axes.titlesize':7.5,'axes.labelsize':7,'xtick.labelsize':6.5,'ytick.labelsize':6.5,
      'legend.fontsize':6.5,'axes.edgecolor':AXIS,'axes.linewidth':0.5,'xtick.color':INK2,'ytick.color':INK2,'axes.labelcolor':INK2,'text.color':INK,
      'xtick.major.width':0.5,'ytick.major.width':0.5,'xtick.major.size':2.5,'ytick.major.size':2.5,'axes.spines.top':False,'axes.spines.right':False,
      'axes.grid':False,'grid.color':GRID,'grid.linewidth':0.5,'grid.linestyle':'-','lines.linewidth':1.2,'lines.solid_capstyle':'round',
      'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':600,'figure.dpi':150,'axes.titleweight':'bold','axes.titlelocation':'left',
      'legend.frameon':False,'axes.facecolor':'white','figure.facecolor':'white'})
def panel(ax,letter,title,x=-0.0,y=1.02):
    if not hasattr(ax.figure,'_panels'): ax.figure._panels=[]
    ax.figure._panels.append((letter,ax))
    ax.text(x,y,letter+'.',transform=ax.transAxes,fontsize=9,fontweight='bold',va='bottom',ha='left',color=INK)
    import matplotlib.transforms as mt
    ax.text(x,y,title,transform=mt.offset_copy(ax.transAxes,fig=ax.figure,x=12.5,y=0,units='points'),fontsize=7.5,fontweight='bold',va='bottom',ha='left',color=INK)
class _MidDot(mpl.ticker.Formatter):
    """Lancet style: mid-line decimal point (23·4) in tick labels; delegates to the axis' own formatter."""
    def __init__(self,inner): self.inner=inner
    def set_axis(self,axis): self.inner.set_axis(axis); super().set_axis(axis)
    def set_locs(self,locs): self.inner.set_locs(locs)
    def __call__(self,x,pos=None):
        import re; return re.sub(r'(\d)\.(\d)',r'\1·\2',str(self.inner(x,pos)))
def lancet_decimals(fig):
    import re
    for ax in fig.axes:
        for axis in (ax.xaxis,ax.yaxis):
            f=axis.get_major_formatter()
            if not isinstance(f,_MidDot): axis.set_major_formatter(_MidDot(f))
    for t in fig.findobj(mpl.text.Text):
        s=t.get_text()
        if s and '$' not in s: t.set_text(re.sub(r'(?<![\w/])(\d+)\.(\d+)',r'\1·\2',s))
def save(fig,name):
    lancet_decimals(fig)
    import os; sub='supplementary' if name.startswith('FigureS') else 'main'; os.makedirs(f'figures/{sub}',exist_ok=True); name=f'{sub}/{name}'
    for ext in ['pdf','png','svg']: fig.savefig(f'figures/{name}.{ext}',bbox_inches='tight',pad_inches=0.04,dpi=600 if ext=='png' else None)
    fig.savefig(f'figures/{name}.tiff',bbox_inches='tight',pad_inches=0.04,dpi=600,pil_kwargs={'compression':'tiff_lzw'})
    _save_panels(fig,name)
    plt.close(fig)
def _save_panels(fig,name):
    """Lancet: supply individual parts of multi-part figures as editable vector files (text as text)."""
    import os
    from matplotlib.transforms import Bbox
    P=getattr(fig,'_panels',[])
    if len(P)<2: return
    os.makedirs('figures/panels',exist_ok=True)
    fig.canvas.draw(); r=fig.canvas.get_renderer(); pax=[a for _,a in P]
    for L,ax in P:
        bbs=[ax.get_tightbbox(r)]; core=ax.get_window_extent(r)
        for o in fig.axes:
            if o in pax or not o.get_visible(): continue
            e=o.get_window_extent(r)
            if e.overlaps(core) or (abs(e.x0-core.x0)<core.width*0.05 and e.y1<=core.y0 and core.y0-e.y1<core.height*0.35):
                bbs.append(o.get_tightbbox(r))
        bb=Bbox.union([b for b in bbs if b is not None]).transformed(fig.dpi_scale_trans.inverted()).padded(0.03)
        for ext in ('pdf','svg'): fig.savefig(f'figures/panels/{os.path.basename(name)}_panel{L}.{ext}',bbox_inches=bb)
