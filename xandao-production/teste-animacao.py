#!/usr/bin/env python3
"""Prova de movimento real, gráficos e legendas temporizadas - Xandão Studio."""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SECONDS = 960, 540, 24, 12
OUT = Path("xandao-outputs")
OUT.mkdir(exist_ok=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SMALL="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
titlefont=ImageFont.truetype(FONT,43)
capfont=ImageFont.truetype(FONT,31)
smallfont=ImageFont.truetype(SMALL,19)
CYAN=(72,230,252); GOLD=(255,170,84)

def draw_mic(d,x,y,scale=1):
    a=int(27*scale); b=int(52*scale)
    d.rounded_rectangle((x-a,y-b,x+a,y+b//3),radius=a,fill=(126,220,237))
    d.arc((x-a-13,y-34*scale,x+a+13,y+68*scale),0,180,fill=(245,248,250),width=5)
    d.line((x,y+68*scale,x,y+105*scale),fill=(240,250,255),width=5)
    d.line((x-36*scale,y+105*scale,x+36*scale,y+105*scale),fill=(240,250,255),width=5)

def draw_speaker(d,x,y,scale=1):
    d.rounded_rectangle((x-73*scale,y-101*scale,x+73*scale,y+101*scale),radius=14,fill=(24,50,73),outline=CYAN,width=4)
    for rr,yy in [(49,34),(23,-57)]:
        d.ellipse((x-rr*scale,y+yy*scale-rr*scale,x+rr*scale,y+yy*scale+rr*scale),fill=(8,22,35),outline=(118,208,221),width=4)

def centered(d,text,font,y,fill):
    box=d.textbbox((0,0),text,font=font)
    d.text(((W-(box[2]-box[0]))/2,y),text,font=font,fill=fill)

def frame(n):
    t=n/FPS
    im=Image.new("RGB",(W,H))
    pix=im.load()
    for y in range(H):
        base=int(y/H*19)
        for x in range(W):
            pix[x,y]=(7+base//3,15+base,28+base)
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    for i in range(13):
        p=(i*83.7+t*(26+i*3))%W
        q=(i*53.4+t*(19+i))%H
        r=3+i%4
        gd.ellipse((p-r,q-r,p+r,q+r),fill=(70,206,255,125))
    glow=glow.filter(ImageFilter.GaussianBlur(12))
    im=Image.alpha_composite(im.convert("RGBA"),glow).convert("RGB")
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,6),fill=CYAN)
    d.text((50,30),"XANDÃO STUDIO  /  SISTEMA DE ÁUDIO",font=smallfont,fill=CYAN)
    d.line((48,67,912,67),fill=(35,78,99),width=2)
    centered(d,"O CICLO DA MICROFONIA",titlefont,87,(235,248,254))
    dx=8*math.sin(t*17) if 3<t<6 else 0
    mx=int(241+dx); sx=710
    draw_mic(d,mx,267)
    draw_speaker(d,sx,265)
    for j in range(3):
        shift=(t*0.28+j/3)%1
        x=330+int(270*shift)
        amp=(10+16*math.sin(math.pi*shift))
        d.arc((x-amp,232-amp,x+amp,232+amp),-72,72,fill=CYAN,width=4)
    if t>=3:
        for j in range(3):
            shift=(t*0.37+j/3)%1
            x=603-int(260*shift)
            y=327+42*math.sin(shift*math.pi)
            d.ellipse((x-6,y-6,x+6,y+6),fill=GOLD)
    if t>=6:
        for k in range(34):
            x=52+k*25
            val=25+80*abs(math.sin(0.27*k+3.8*t))*abs(math.sin(0.075*k+t))
            d.rounded_rectangle((x,431-val,x+11,431),radius=5,fill=GOLD if val>78 else CYAN)
    else:
        pts=[]
        for x in range(50,912,3):
            y=418+17*math.sin((x/28)-t*9)*math.sin((x/83)+t*1.7)
            pts.append((x,int(y)))
        d.line(pts,fill=CYAN,width=3)
    if t<3:
        caption="O SOM SAI DA CAIXA"
    elif t<6:
        caption="VOLTA PARA O MICROFONE"
    elif t<9:
        caption="O CICLO SE AMPLIFICA!"
    else:
        caption="POSICIONE E AJUSTE O GANHO"
    d.rounded_rectangle((140,460,820,517),radius=13,fill=(25,56,72))
    centered(d,caption,capfont,470,(245,251,254))
    return im

def main():
    dest=OUT/"Xandao-Demo-Animacao-Real.mp4"
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-f","rawvideo","-vcodec","rawvideo","-s",f"{W}x{H}",
         "-pix_fmt","rgb24","-r",str(FPS),"-i","-",
         "-f","lavfi","-i","sine=frequency=180:sample_rate=48000",
         "-t",str(SECONDS),"-c:v","libx264","-preset","veryfast",
         "-crf","23","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","96k","-af","volume=0.025",
         "-movflags","+faststart",str(dest)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for n in range(SECONDS*FPS):
            p.stdin.write(frame(n).tobytes())
        p.stdin.close()
        status=p.wait()
        if status: raise RuntimeError(f"ffmpeg terminou com erro {status}")
    finally:
        if p.poll() is None:
            p.kill()
    print(f"Demo animada pronta: {dest} ({dest.stat().st_size} bytes)")

if __name__=="__main__":
    main()
