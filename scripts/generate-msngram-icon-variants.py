#!/usr/bin/env python3
"""Generate all 15 launcher variants from the approved folded M. Requires Pillow.
Run: env -u PYTHONPATH /usr/bin/python3 scripts/generate-msngram-icon-variants.py
No Android SDK, network, builds or publication required.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import colorsys, hashlib, json, math, re
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'TMessagesProj/src/main/res'
OUT = ROOT / 'docs/branding/icon-variants'
OUT.mkdir(parents=True, exist_ok=True)
S = 432
# Enum name, stable manifest resource, highlight hue, background, frame geometry.
VARIANTS = [
 ('DEFAULT','ic_launcher_msngram',.54,'#102d48','orbit'),
 ('GOOGLE','ic_launcher_msngram_google',.10,'#f4efe1','tiles'),
 ('COLORFUL','ic_launcher_msngram_colorful',.04,'#132b37','confetti'),
 ('DARKGREEN','ic_launcher_msngram_darkgreen',.40,'#092e27','hexagon'),
 ('NEON','ic_launcher_msngram_neon',.48,'#031e29','neon'),
 ('NIELLO','ic_launcher_msngram_round_niello',.10,'#20272b','coin'),
 ('BLUE','ic_launcher_msngram_blue',.56,'#06476b','plain'),
 ('DARKBLUE','ic_launcher_msngram_dark_blue',.59,'#071c38','diamond'),
 ('BLURBLUE','ic_launcher_msngram_blur_blue',.53,'#255b75','cloud'),
 ('TELEGRAM','ic_launcher_dr',.52,'#daf4fa','bubble'),
 ('VINTAGE','icon_6_launcher',.075,'#392919','stamp'),
 ('AQUA','icon_4_launcher',.45,'#063e45','waves'),
 ('PREMIUM','icon_3_launcher',.12,'#222820','shield'),
 ('TURBO','icon_5_launcher',.025,'#382419','speed'),
 ('NOX','icon_2_launcher',.54,'#101a23','eclipse'),
]
source = Image.open(RES/'drawable-xxxhdpi/msngram_icon_foreground.png').convert('RGBA')
# Preserve the complete approved silhouette, folds, orbit and sparkles.
source.save(OUT/'approved-m-source.png')
records=[]
generated=[]
def save(im,p):
 # LANCZOS can overshoot RGB channels on nearly transparent edge pixels.
 # Remove only disallowed edge hues after resampling, retaining value and alpha.
 clean=[]
 for r,g,b,a in im.convert('RGBA').getdata():
  h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
  if 250/360<=h<=315/360 and s>.20 and v>.08:
   r,g,b=(round(c*255) for c in colorsys.hsv_to_rgb(.60,s,v))
  clean.append((r,g,b,a))
 im=im.convert('RGBA'); im.putdata(clean)
 p.parent.mkdir(parents=True,exist_ok=True); im.save(p,optimize=True); generated.append(p)
def poly(d,n,r,fill,outline=None,width=3,rotation=-math.pi/2):
 pts=[(216+r*math.cos(rotation+i*2*math.pi/n),216+r*math.sin(rotation+i*2*math.pi/n)) for i in range(n)]
 d.polygon(pts,fill=fill); d.line(pts+[pts[0]],fill=outline or fill,width=width)
for idx,(name,resource,hue,bg,style) in enumerate(VARIANTS):
 rgb=tuple(bytes.fromhex(bg[1:])); accent=tuple(round(c*255) for c in colorsys.hsv_to_rgb(hue,.65,.95))
 # Radial lighting keeps backgrounds dimensional without introducing purple.
 background=Image.new('RGBA',(S,S)); pixels=[]
 for y in range(S):
  for x in range(S):
   light=max(0,1-math.hypot(x-160,y-130)/400)
   pixels.append(tuple(min(255,round(v+light*(255-v)*.09)) for v in rgb)+(255,))
 background.putdata(pixels)
 fg=Image.new('RGBA',(S,S)); d=ImageDraw.Draw(fg)
 # All geometry fits inside the central 72dp adaptive viewport (288px).
 a=accent+(180,); soft=accent+(65,); faint=accent+(32,)
 if style=='orbit':
  d.arc((87,87,345,345),15,160,fill=a,width=5); d.arc((98,98,334,334),193,335,fill=soft,width=11)
 elif style=='tiles':
  for box,c in [((100,100,212,212),(232,173,51,255)),((220,100,332,212),(55,152,191,255)),((100,220,212,332),(69,160,124,255)),((220,220,332,332),(225,112,59,255))]:
   d.rounded_rectangle(box,24,fill=c)
 elif style=='confetti':
  for i in range(12):
   t=i*math.tau/12; x=216+123*math.cos(t); y=216+123*math.sin(t)
   c=tuple(round(v*255) for v in colorsys.hsv_to_rgb([.04,.12,.43,.54][i%4],.8,.95))+(230,)
   d.polygon([(x,y-7),(x+7,y),(x,y+7),(x-7,y)],fill=c)
 elif style=='hexagon': poly(d,6,135,accent+(25,),a,5)
 elif style=='neon':
  d.rounded_rectangle((94,94,338,338),55,outline=accent+(100,),width=14)
  fg=fg.filter(ImageFilter.GaussianBlur(7)); d=ImageDraw.Draw(fg)
  d.rounded_rectangle((94,94,338,338),55,outline=accent+(255,),width=3)
 elif style=='coin':
  d.ellipse((84,84,348,348),fill=(70,66,46,180),outline=a,width=6)
  d.ellipse((96,96,336,336),outline=soft,width=3)
 elif style=='diamond': poly(d,4,137,faint,a,4)
 elif style=='cloud':
  for x,y,r in [(137,158,56),(277,154,48),(257,280,65),(153,272,52)]: d.ellipse((x-r,y-r,x+r,y+r),fill=accent+(65,))
  fg=fg.filter(ImageFilter.GaussianBlur(17))
 elif style=='bubble':
  d.rounded_rectangle((90,100,342,319),55,fill=(255,255,255,220),outline=accent+(120,),width=3)
  d.polygon([(140,302),(130,337),(185,314)],fill=(255,255,255,220))
 elif style=='stamp':
  d.rectangle((99,99,333,333),fill=(128,94,51,120),outline=a,width=4)
  for q in range(110,330,18):
   for x,y in [(q,99),(q,333),(99,q),(333,q)]: d.ellipse((x-4,y-4,x+4,y+4),fill=(57,41,25,255))
  d.rectangle((112,112,320,320),outline=soft,width=2)
 elif style=='waves':
  for off in [0,18,36]:
   points=[(x,287+off+8*math.sin(x/28)) for x in range(91,342)]
   d.line(points,fill=accent+(150-off*2,),width=4)
  d.arc((92,90,340,338),190,345,fill=soft,width=3)
 elif style=='shield':
  d.polygon([(216,83),(333,130),(322,250),(285,306),(216,346),(147,306),(110,250),(99,130)],fill=accent+(28,),outline=a,width=5)
 elif style=='speed':
  for y,x in [(135,107),(174,87),(264,90),(302,110)]: d.line((x,y,x+205,y-30),fill=accent+(160,),width=7)
 elif style=='eclipse':
  d.ellipse((87,87,345,345),fill=(100,155,178,160)); d.ellipse((102,78,345,330),fill=rgb+(255,))
  d.arc((87,87,345,345),50,250,fill=(209,232,240,220),width=3)
 mark=Image.new('RGBA',source.size); recolored=[]
 for r,g,b,alpha in source.getdata():
  oldh,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
  # Keep facet luminance and saturation; limit blue to <240 degrees.
  h=(hue+(oldh-.56)*.36)%1
  if .64 <= h <= .92: h=.60
  if name=='COLORFUL': h=[.035,.12,.43,.55][min(3,int(v*4))]
  if name in ('NIELLO','NOX'): s*=.23
  rr,gg,bb=colorsys.hsv_to_rgb(h,s,v)
  recolored.append((round(rr*255),round(gg*255),round(bb*255),alpha))
 mark.putdata(recolored)
 # Tiles and badges use a compact mark; open frames retain the original scale.
 size={'tiles':326,'coin':370,'stamp':340,'shield':350,'bubble':360,'diamond':350}.get(style,392)
 mark=mark.resize((size,size),Image.Resampling.LANCZOS)
 shadow=Image.new('RGBA',(S,S)); shadow.paste(mark,(int((S-size)/2),int((S-size)/2+5)))
 shadow.putalpha(shadow.getchannel('A').point(lambda v:round(v*.40)))
 # The shadow is neutral black, so it cannot add a disallowed hue.
 black=Image.new('RGBA',(S,S),(0,0,0,0)); black.putalpha(shadow.getchannel('A'))
 fg=Image.alpha_composite(fg,black.filter(ImageFilter.GaussianBlur(5)))
 fg.alpha_composite(mark,((S-size)//2,(S-size)//2))
 for density,scale in [('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3),('xxxhdpi',4)]:
  n=round(108*scale)
  save(background.resize((n,n),Image.Resampling.LANCZOS),RES/f'drawable-{density}/msngram_{name.lower()}_background.png')
  save(fg.resize((n,n),Image.Resampling.LANCZOS),RES/f'drawable-{density}/msngram_{name.lower()}_foreground.png')
 composed=Image.alpha_composite(background,fg).crop((72,72,360,360))
 for suffix in ['', '_round']:
  for density,scale in [('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3),('xxxhdpi',4)]:
   mask=Image.new('L',(288,288)); md=ImageDraw.Draw(mask)
   if suffix: md.ellipse((0,0,287,287),fill=255)
   else: md.rounded_rectangle((0,0,287,287),56,fill=255)
   im=composed.copy(); im.putalpha(mask)
   save(im.resize((round(48*scale),)*2,Image.Resampling.LANCZOS),RES/f'mipmap-{density}/{resource}{suffix}.png')
  xml=f'''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/msngram_{name.lower()}_background"/>
    <foreground android:drawable="@drawable/msngram_{name.lower()}_foreground"/>
    <monochrome android:drawable="@drawable/msngram_icon_monochrome"/>
</adaptive-icon>
'''
  path=RES/f'mipmap-anydpi-v26/{resource}{suffix}.xml'; path.write_text(xml); generated.append(path)
 save(composed,OUT/f'{name.lower()}.png')
 records.append(dict(enum=name,alias_resource=resource,style=style,background=f'msngram_{name.lower()}_background',foreground=f'msngram_{name.lower()}_foreground',sha256=hashlib.sha256(composed.tobytes()).hexdigest()))
# Enum edits only change the drawable arguments; all keys and title IDs stay stable.
java=ROOT/'TMessagesProj/src/main/java/org/telegram/ui/LauncherIconController.java'
text=java.read_text()
for r in records:
 text=re.sub(r'('+r['enum']+r'\("[^"]+", )R.drawable.\w+, R.drawable.\w+,',r'\g<1>R.drawable.'+r['background']+', R.drawable.'+r['foreground']+',',text)
java.write_text(text)
# Verify real manifest mappings, both adaptive layers, legacy coverage and hues.
android='{http://schemas.android.com/apk/res/android}'
manifest=ET.parse(ROOT/'TMessagesProj/src/main/AndroidManifest.xml')
controller=java.read_text()
for r in records:
 key=re.search(r'\b'+r['enum']+r'\("([^"]+)"',controller).group(1)
 alias=next(x for x in manifest.iter('activity-alias') if x.get(android+'name')=='org.telegram.messenger.'+key)
 assert alias.get(android+'icon')=='@mipmap/'+r['alias_resource']
 assert alias.get(android+'roundIcon')=='@mipmap/'+r['alias_resource']+'_round'
 for suf in ['', '_round']:
  root=ET.parse(RES/f'mipmap-anydpi-v26/{r["alias_resource"]}{suf}.xml').getroot()
  for tag in ['background','foreground']: assert root.find(tag).get(android+'drawable')=='@drawable/'+r[tag]
  for density in ['mdpi','hdpi','xhdpi','xxhdpi','xxxhdpi']: assert (RES/f'mipmap-{density}/{r["alias_resource"]}{suf}.png').exists()
 r['alias']=key
purple=0; checked=0
for p in generated:
 if p.suffix!='.png': continue
 im=Image.open(p).convert('RGBA')
 for red,green,blue,alpha in im.getdata():
  if alpha<24: continue
  h,s,v=colorsys.rgb_to_hsv(red/255,green/255,blue/255)
  if 250/360 <= h <= 315/360 and s>.20 and v>.08: purple+=1
 checked+=1
assert len(set(r['sha256'] for r in records))==15
assert purple==0, purple
font=ImageFont.load_default(); sheet=Image.new('RGB',(1100,3*265),(232,237,241)); draw=ImageDraw.Draw(sheet)
for i,r in enumerate(records):
 im=Image.open(OUT/f'{r["enum"].lower()}.png').resize((192,192),Image.Resampling.LANCZOS)
 mask=Image.new('L',(192,192)); ImageDraw.Draw(mask).ellipse((0,0,191,191),fill=255)
 x=(i%5)*220+14; y=(i//5)*265+10
 sheet.paste(im,(x,y),mask); draw.text((x,y+204),r['enum']+' / '+r['style'],fill=(20,36,48),font=font)
sheet.save(OUT/'contact-sheet.png')
report=dict(variants=records,unique_composites=15,purple_pixels=purple,purple_definition='hue 250..315 degrees, saturation > .20, value > .08, alpha >=24',pngs_checked=checked,generated_resource_files=sum(1 for p in generated if RES in p.parents),generated_paths=[str(p.relative_to(ROOT)) for p in generated],source=str((OUT/'approved-m-source.png').relative_to(ROOT)),contact_sheet=str((OUT/'contact-sheet.png').relative_to(ROOT)),validation='Source/resource validation only; no build or device test requested.')
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('variants','generated_paths')},indent=2))
