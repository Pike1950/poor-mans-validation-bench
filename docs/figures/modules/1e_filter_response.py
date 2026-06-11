"""
1e_filter_response.py - Figure 1E-6: reconstruction filter, singly- vs doubly-terminated

Shows why the Module 1E reconstruction filter is synthesized as a singly-terminated
5th-order Butterworth. All three curves are the SAME physical circuit (25 ohm DAC
termination as the per-leg source, ~1 kohm op-amp input resistor as the load); only
the L/C values differ, i.e. which termination model they were designed for. The
doubly-terminated designs ripple 6-11 dB in-band because the real 40:1 source/load
ratio is not the matched condition they assume; the singly-terminated design (the one
the board uses) stays smooth, leaving only a ~1.5 dB droop that the section 9.4
calibration removes.

Outputs:
  1e_filter_response.svg + .png

Run:  python3 1e_filter_response.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# PMVB dark-theme palette (matches pmvb-figures.sty)
PMVB_BG="#1a1a2e"; PMVB_PANEL="#16213e"; PMVB_FG="#f0f0f0"; PMVB_MUTED="#888"
PMVB_GRID="#2d3a55"; PMVB_BLUE="#60a5fa"; PMVB_AMBER="#fbbf24"; PMVB_RED="#f87171"; PMVB_GREEN="#4ade80"

FC=12e6; WC=2*np.pi*FC; RS=25.0; RL=1000.0          # real per-leg terminations
f=np.logspace(5,7.95,4000); w=2*np.pi*f

def resp_db(elem):
    """Normalized (to DC) magnitude in dB of the L-C-L-C-L ladder in the real Rs/RL circuit."""
    L1,C2,L3,C4,L5=elem; jw=1j*w
    one=np.ones_like(jw); zero=np.zeros_like(jw)
    def mul(m1,m2):
        A1,B1,C1,D1=m1; A2,B2,C2_,D2=m2
        return (A1*A2+B1*C2_, A1*B2+B1*D2, C1*A2+D1*C2_, C1*B2+D1*D2)
    T=(one,zero,zero,one)
    for m in [(one,jw*L1,zero,one),(one,zero,jw*C2,one),(one,jw*L3,zero,one),(one,zero,jw*C4,one),(one,jw*L5,zero,one)]:
        T=mul(T,m)
    A,B,C,D=T
    H=RL/(A*RL+B+RS*(C*RL+D))
    return 20*np.log10(np.abs(H)/np.abs(RL/(RS+RL)))

g=[0.6180,1.6180,2.0000,1.6180,0.6180]              # 5th-order Butterworth prototype
doubly=lambda R:[g[0]*R/WC,g[1]/(R*WC),g[2]*R/WC,g[3]/(R*WC),g[4]*R/WC]
singly=[0.22e-6,820e-12,0.68e-6,820e-12,0.22e-6]    # chosen, from the D2 synthesis

curves=[
 ("Singly-terminated (board): 0.22 / 0.68 / 0.22 uH, 820 pF", singly, PMVB_GREEN,2.8,"-"),
 ("Doubly-terminated, designed for 50 ohm (old assumption)", doubly(50), PMVB_AMBER,1.9,"--"),
 ("Doubly-terminated, designed for 158 ohm (geo-mean)", doubly(np.sqrt(25*1000)), PMVB_RED,1.7,":"),
]

fig,(ax1,ax2)=plt.subplots(2,1,figsize=(12.5,8.6),facecolor=PMVB_BG)
for label,elem,col,lw,ls in curves:
    H=resp_db(elem)
    ax1.semilogx(f/1e6,H,color=col,lw=lw,ls=ls,label=label)
    ax2.semilogx(f/1e6,H,color=col,lw=lw,ls=ls)

def style(ax):
    ax.set_facecolor(PMVB_PANEL); ax.grid(True,which="both",alpha=0.35,color=PMVB_GRID,lw=0.5)
    ax.tick_params(colors=PMVB_FG)
    for s in ax.spines.values(): s.set_color(PMVB_GRID)

# top: full response
style(ax1)
ax1.axhline(-3,color=PMVB_MUTED,lw=0.8,ls=(0,(4,4))); ax1.text(0.34,-1.4,"-3 dB",color=PMVB_MUTED,fontsize=8)
for fr,txt in [(10,"10 MHz\nband edge"),(20,"20 MHz\nimage @30 MSPS"),(40,"40 MHz\nimage @50 MSPS")]:
    ax1.axvline(fr,color=PMVB_MUTED,lw=0.7,ls=":",alpha=0.7)
    ax1.text(fr,10.5,txt,fontsize=7.5,ha="center",va="top",color=PMVB_MUTED)
ax1.set_ylim(-70,14); ax1.set_xlim(0.3,80)
ax1.set_ylabel("Magnitude (dB, norm. to DC)",color=PMVB_FG,fontsize=11)
ax1.set_title("Module 1E reconstruction filter: same real circuit (25 $\\Omega$ source, 1 k$\\Omega$ op-amp load), "
              "three design models",color=PMVB_FG,fontsize=12)
leg=ax1.legend(loc="lower left",facecolor=PMVB_PANEL,edgecolor=PMVB_GRID,labelcolor=PMVB_FG,framealpha=0.95,fontsize=9.5)

# bottom: passband zoom
style(ax2)
ax2.axhline(-3,color=PMVB_MUTED,lw=0.8,ls=(0,(4,4))); ax2.text(0.34,-2.6,"-3 dB",color=PMVB_MUTED,fontsize=8)
ax2.axvline(10,color=PMVB_MUTED,lw=0.7,ls=":",alpha=0.7); ax2.text(10.4,2.4,"10 MHz",fontsize=8,color=PMVB_MUTED)
ax2.set_ylim(-14,5); ax2.set_xlim(0.3,20)
ax2.set_xlabel("Frequency (MHz)",color=PMVB_FG,fontsize=11); ax2.set_ylabel("Magnitude (dB)",color=PMVB_FG,fontsize=11)
ax2.set_title("Passband detail: the doubly-terminated models ripple in-band; the singly-terminated model stays smooth",
              color=PMVB_FG,fontsize=10.5)
ax2.annotate("6-11 dB in-band ripple\n(wrong termination model)",xy=(2.3,-7.5),fontsize=9,color=PMVB_AMBER,ha="center")
ax2.annotate("~1.5 dB smooth droop\n(flattened by section 9.4 cal)",xy=(1.1,1.4),fontsize=9,color=PMVB_GREEN,ha="center")

fig.tight_layout()
here=os.path.dirname(os.path.abspath(__file__))
fig.savefig(os.path.join(here,"1e_filter_response.svg"),facecolor=PMVB_BG,edgecolor="none")
fig.savefig(os.path.join(here,"1e_filter_response.png"),facecolor=PMVB_BG,edgecolor="none",dpi=150)
plt.close(fig)
for label,elem,_,_,_ in curves:
    H=resp_db(elem); pb=H[f<=10e6]
    print(f"  {label[:46]:46s} ripple 0-10MHz = {pb.max()-pb.min():5.2f} dB")
print("Wrote 1e_filter_response.svg + .png")
