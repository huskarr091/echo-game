import pygame, sys, math, random, array

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

W, H = 960, 640
FPS = 60
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("ЭХО")
clock = pygame.time.Clock()

BLACK=(6,8,14); WHITE=(230,235,245); GREY=(130,140,160)
CYAN=(90,220,240); TEAL=(60,180,200); GREEN=(110,220,140)
MAGENTA=(220,100,200); YELLOW=(245,220,90); RED=(230,80,80)
ORANGE=(245,150,60); BLUE=(90,140,220); PURPLE=(170,120,230)

def F(sz, bold=False):
    try: return pygame.font.SysFont("consolas,dejavusansmono", sz, bold=bold)
    except: return pygame.font.Font(None, sz)
F_TITLE=F(96,True); F_BIG=F(42,True); F_MED=F(26,True)
F_BODY=F(22); F_SMALL=F(18)

def mk_snd(f1,f2,dur,vol=0.3,wave="sine"):
    sr=22050; n=int(sr*dur); buf=array.array("h")
    for i in range(n):
        t=i/sr; p=i/max(1,n-1); f=f1+(f2-f1)*p
        ph=2*math.pi*f*t
        if wave=="sine": v=math.sin(ph)
        elif wave=="square": v=1.0 if math.sin(ph)>0 else -1.0
        elif wave=="noise": v=random.uniform(-1,1)
        else: v=math.sin(ph)
        env=max(0.0,1.0-p)
        s=int(v*env*vol*32767); s=max(-32768,min(32767,s))
        buf.append(s); buf.append(s)
    return pygame.mixer.Sound(buffer=buf.tobytes())

def mk_ambient(dur=10.0):
    sr=22050; n=int(sr*dur); buf=array.array("h")
    freqs=[55.0,82.4,110.0,164.8,220.0,329.6]
    weights=[0.5,0.35,0.3,0.2,0.15,0.1]
    for i in range(n):
        t=i/sr; v=0.0
        for f,w in zip(freqs,weights):
            v+=math.sin(2*math.pi*f*t+math.sin(t*0.3)*1.5)*w
        v*=0.6+0.4*math.sin(2*math.pi*0.07*t); v*=0.22
        s=int(v*32767); s=max(-32768,min(32767,s))
        buf.append(s); buf.append(s)
    return pygame.mixer.Sound(buffer=buf.tobytes())

print("Генерация звуков...")
SND_BLIP=mk_snd(900,700,0.03,0.10,"square")
SND_INTERACT=mk_snd(500,900,0.10,0.20,"sine")
SND_PICKUP=mk_snd(660,1320,0.20,0.26,"sine")
SND_ERROR=mk_snd(300,150,0.30,0.26,"square")
SND_SUCCESS=mk_snd(440,1320,0.50,0.26,"sine")
SND_STEP=mk_snd(200,120,0.05,0.06,"noise")
SND_MEMORY=mk_snd(600,200,0.80,0.22,"sine")
print("Генерация эмбиента...")
AMBIENT=mk_ambient(10.0)
print("Готово.")

class Player:
    def __init__(self,x,y):
        self.x=x; self.y=y; self.speed=4; self.radius=14
        self.facing=(0,1); self.step_t=0; self.anim=0.0
        self.dir="down"; self.walking=False; self.invuln=0
    def update(self,keys,walls):
        dx=dy=0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx-=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx+=1
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy-=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy+=1
        if dx and dy: dx*=0.7071; dy*=0.7071
        if abs(dx)>abs(dy): self.dir="right" if dx>0 else "left"
        elif dy!=0: self.dir="down" if dy>0 else "up"
        self.walking=bool(dx or dy); moved=False
        nx=self.x+dx*self.speed
        if not self.collides(nx,self.y,walls): self.x=nx; moved=moved or bool(dx)
        ny=self.y+dy*self.speed
        if not self.collides(self.x,ny,walls): self.y=ny; moved=moved or bool(dy)
        if dx or dy:
            l=math.hypot(dx,dy); self.facing=(dx/l,dy/l)
        if moved and self.walking:
            self.anim+=0.32; self.step_t+=1
            if self.step_t>=16: self.step_t=0; SND_STEP.play()
        else: self.anim=0.0
    def collides(self,x,y,walls):
        r=self.radius; rect=pygame.Rect(x-r,y-r,r*2,r*2)
        for w in walls:
            if rect.colliderect(w): return True
        return False
    def draw(self,surf):
        x,y=int(self.x),int(self.y)
        sh=pygame.Surface((44,16),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,140),sh.get_rect())
        surf.blit(sh,(x-22,y+12))
        walk=math.sin(self.anim) if self.walking else 0.0
        bob=int(abs(walk)*2); leg_swing=int(walk*5); arm_swing=int(walk*4)
        pygame.draw.line(surf,(60,80,120),(x-5,y+6),(x-5,y+14+leg_swing),5)
        pygame.draw.line(surf,(60,80,120),(x+5,y+6),(x+5,y+14-leg_swing),5)
        pygame.draw.circle(surf,(40,50,80),(x-5,y+16+leg_swing),3)
        pygame.draw.circle(surf,(40,50,80),(x+5,y+16-leg_swing),3)
        if self.dir=="up":
            pack=pygame.Rect(x-12,y-2+bob,24,14)
            pygame.draw.rect(surf,(120,140,180),pack,border_radius=3)
            pygame.draw.rect(surf,(80,100,140),pack,2,border_radius=3)
        body=pygame.Rect(x-11,y-5+bob,22,16)
        pygame.draw.ellipse(surf,(185,200,225),body)
        pygame.draw.ellipse(surf,(90,120,170),body,2)
        pygame.draw.rect(surf,(140,160,200),(x-5,y-2+bob,10,7),border_radius=2)
        pygame.draw.circle(surf,(255,200,100),(x,y+2+bob),3)
        pygame.draw.circle(surf,(255,240,180),(x,y+2+bob),1)
        pygame.draw.line(surf,(185,200,225),(x-11,y+1+bob),(x-15,y+8+arm_swing),5)
        pygame.draw.line(surf,(185,200,225),(x+11,y+1+bob),(x+15,y+8-arm_swing),5)
        pygame.draw.circle(surf,(200,210,235),(x-15,y+9+arm_swing),3)
        pygame.draw.circle(surf,(200,210,235),(x+15,y+9-arm_swing),3)
        hy=y-15+bob
        pygame.draw.circle(surf,(205,215,240),(x,hy),12)
        pygame.draw.circle(surf,(90,120,170),(x,hy),12,2)
        pygame.draw.circle(surf,(240,245,255),(x-5,hy-5),2)
        if self.dir=="down":
            v=pygame.Rect(x-7,hy-4,14,9)
            pygame.draw.ellipse(surf,(80,180,230),v)
            pygame.draw.ellipse(surf,(30,90,140),v,2)
            pygame.draw.circle(surf,(200,240,255),(x-3,hy-1),2)
        elif self.dir=="up":
            pygame.draw.arc(surf,(90,120,170),(x-12,hy-12,24,24),0.4,2.7,3)
            pygame.draw.line(surf,(140,160,200),(x,hy-12),(x,hy-18),2)
            pygame.draw.circle(surf,(255,100,100),(x,hy-19),2)
        elif self.dir=="left":
            v=pygame.Rect(x-10,hy-4,12,9)
            pygame.draw.ellipse(surf,(80,180,230),v)
            pygame.draw.ellipse(surf,(30,90,140),v,2)
            pygame.draw.circle(surf,(200,240,255),(x-6,hy-1),2)
        else:
            v=pygame.Rect(x-2,hy-4,12,9)
            pygame.draw.ellipse(surf,(80,180,230),v)
            pygame.draw.ellipse(surf,(30,90,140),v,2)
            pygame.draw.circle(surf,(200,240,255),(x+2,hy-1),2)

class Companion:
    def __init__(self):
        self.x=0; self.y=0; self.vx=0; self.vy=0
        self.bob=0.0; self.pulse=0.0; self.trail=[]; self.visible=False
    def update(self,px,py):
        tx=px-50; ty=py-45
        self.vx+=(tx-self.x)*0.06; self.vy+=(ty-self.y)*0.06
        self.vx*=0.85; self.vy*=0.85
        self.x+=self.vx; self.y+=self.vy
        self.bob+=0.08; self.pulse+=0.10
        self.trail.append([self.x,self.y,24])
        self.trail=[t for t in self.trail if t[2]>0]
        for t in self.trail: t[2]-=1
        if len(self.trail)>25: self.trail=self.trail[-25:]
    def draw(self,surf):
        if not self.visible: return
        for tx,ty,life in self.trail:
            a=int(life/24*90); r=max(1,int(life/24*4))
            s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(s,(100,220,240,a),(r,r),r)
            surf.blit(s,(tx-r,ty-r))
        yoff=math.sin(self.bob)*3
        cx=int(self.x); cy=int(self.y+yoff)
        glow=pygame.Surface((70,70),pygame.SRCALPHA)
        ga=int(50+40*math.sin(self.pulse))
        pygame.draw.circle(glow,(100,220,240,ga),(35,35),30)
        surf.blit(glow,(cx-35,cy-35))
        pygame.draw.circle(surf,(60,160,200),(cx,cy),13,2)
        for i in range(4):
            ang=self.pulse+i*math.tau/4
            ex=int(cx+math.cos(ang)*16); ey=int(cy+math.sin(ang)*16)
            pygame.draw.circle(surf,(150,235,255),(ex,ey),2)
        pygame.draw.circle(surf,(150,230,250),(cx,cy),8)
        pygame.draw.circle(surf,(220,250,255),(cx,cy),5)
        pygame.draw.circle(surf,(255,255,255),(cx,cy),2)
        pygame.draw.circle(surf,(40,90,130),(cx,cy),3)

class AnyaGhost:
    def __init__(self,x,y):
        self.x=x; self.y=y; self.t=0.0; self.visible=False; self.appear=0
    def update(self):
        self.t+=0.03
        if self.visible and self.appear<220: self.appear=min(220,self.appear+3)
    def draw(self,surf):
        if not self.visible or self.appear<=0: return
        alpha=self.appear; hover=math.sin(self.t)*4
        sprite=pygame.Surface((120,160),pygame.SRCALPHA)
        cx=60; cy=int(60+hover)
        ga=int(30+25*math.sin(self.t*2))
        for rr in range(40,20,-5):
            a=int(ga*(1-rr/40))
            pygame.draw.circle(sprite,(150,200,240,a),(cx,cy),rr)
        dress=[(cx,cy+8),(cx-24,cy+60),(cx+24,cy+60)]
        pygame.draw.polygon(sprite,(170,195,240,int(alpha*0.45)),dress)
        pygame.draw.polygon(sprite,(220,235,255,int(alpha*0.8)),dress,2)
        pygame.draw.ellipse(sprite,(200,215,245,int(alpha*0.55)),(cx-11,cy-8,22,28))
        pygame.draw.circle(sprite,(215,228,250,int(alpha*0.65)),(cx,cy-18),13)
        pygame.draw.circle(sprite,(240,245,255,alpha),(cx,cy-18),13,2)
        pygame.draw.arc(sprite,(140,150,190,alpha),(cx-14,cy-32,28,28),3.0,6.3,4)
        pygame.draw.circle(sprite,(200,240,255,alpha),(cx-4,cy-19),2)
        pygame.draw.circle(sprite,(200,240,255,alpha),(cx+4,cy-19),2)
        for i in range(6):
            ph=(self.t*30+i*25)%60
            px=cx+math.sin(self.t+i)*14
            py=cy+55-ph
            pa=int(alpha*(1-ph/60))
            pygame.draw.circle(sprite,(180,215,250,pa),(int(px),int(py)),2)
        surf.blit(sprite,(self.x-60,self.y-80))

class Interactable:
    def __init__(self,rect,name,prompt,callback,color=(160,170,190)):
        self.rect=pygame.Rect(rect); self.name=name
        self.prompt=prompt; self.callback=callback; self.color=color
    def draw(self,surf,highlight=False):
        pygame.draw.rect(surf,self.color,self.rect,2)
        pygame.draw.rect(surf,tuple(max(0,c-60) for c in self.color),
                        self.rect.inflate(-6,-6),1)
        if highlight: pygame.draw.rect(surf,WHITE,self.rect.inflate(8,8),2)

class Door:
    def __init__(self,rect,target,spawn,name="",needs=None):
        self.rect=pygame.Rect(rect); self.target=target
        self.spawn=spawn; self.name=name; self.needs=needs
    def draw(self,surf,unlocked=True):
        col=CYAN if unlocked else RED
        pygame.draw.rect(surf,col,self.rect,3)
        pygame.draw.circle(surf,col,self.rect.center,6,2)

class Dialogue:
    def __init__(self,lines,on_done=None):
        self.lines=lines; self.idx=0; self.ci=0
        self.on_done=on_done; self.active=True
        self.timer=0; self._cd=0
    def update(self):
        if not self.active: return
        self.timer+=1
        if self._cd>0: self._cd-=1
        full=self.lines[self.idx][1]
        if self.ci<len(full):
            self.ci+=1
            if self.ci%3==0:
                try: SND_BLIP.play()
                except: pass
    def advance(self):
        if self._cd>0: return
        self._cd=5
        full=self.lines[self.idx][1]
        if self.ci<len(full): self.ci=len(full)
        else:
            self.idx+=1; self.ci=0
            if self.idx>=len(self.lines):
                self.active=False
                if self.on_done: self.on_done()
    def draw(self,surf):
        if not self.active: return
        box_h=180; box_y=H-box_h-20
        box=pygame.Surface((W-60,box_h),pygame.SRCALPHA)
        box.fill((8,12,22,240))
        pygame.draw.rect(box,CYAN,box.get_rect(),2)
        pygame.draw.rect(box,TEAL,box.get_rect().inflate(-6,-6),1)
        surf.blit(box,(30,box_y))
        speaker,text=self.lines[self.idx]
        if speaker:
            sp=F_MED.render(speaker,True,CYAN)
            surf.blit(sp,(55,box_y+12))
        shown=text[:self.ci]
        max_w=W-130
        lines=[]; cur=""
        for word in shown.split(" "):
            test=cur+(" " if cur else "")+word
            if F_BODY.size(test)[0]>max_w:
                lines.append(cur); cur=word
            else: cur=test
        if cur: lines.append(cur)
        y0=box_y+(55 if speaker else 30)
        for i,ln in enumerate(lines[:6]):
            img=F_BODY.render(ln,True,WHITE)
            surf.blit(img,(55,y0+i*28))
        if self.ci>=len(text) and (self.timer//18)%2==0:
            pygame.draw.polygon(surf,CYAN,
                [(W-70,box_y+box_h-25),(W-55,box_y+box_h-25),
                 (W-62,box_y+box_h-15)])

class CodeTerminal:
    def __init__(self,correct="7382"):
        self.correct=correct; self.entry=""; self.active=False; self.error_t=0
    def start(self): self.active=True; self.entry=""; self.error_t=0
    def handle(self,key):
        if self.error_t>0: return None
        if key==pygame.K_ESCAPE:
            self.active=False; return "cancel"
        if key==pygame.K_BACKSPACE:
            self.entry=self.entry[:-1]
            try: SND_BLIP.play()
            except: pass
        elif pygame.K_0<=key<=pygame.K_9:
            if len(self.entry)<4:
                self.entry+=chr(key)
                try: SND_BLIP.play()
                except: pass
        elif key in (pygame.K_RETURN,pygame.K_KP_ENTER):
            if self.entry==self.correct:
                self.active=False
                try: SND_SUCCESS.play()
                except: pass
                return "correct"
            else:
                try: SND_ERROR.play()
                except: pass
                self.error_t=40; self.entry=""
        return None
    def update(self):
        if self.error_t>0: self.error_t-=1
    def draw(self,surf):
        overlay=pygame.Surface((W,H),pygame.SRCALPHA)
        overlay.fill((0,0,0,200)); surf.blit(overlay,(0,0))
        tw,th=560,340; tx,ty=(W-tw)//2,(H-th)//2
        pygame.draw.rect(surf,(10,20,30),(tx,ty,tw,th))
        pygame.draw.rect(surf,CYAN,(tx,ty,tw,th),3)
        pygame.draw.rect(surf,(30,60,80),(tx+8,ty+8,tw-16,th-16),1)
        title=F_BIG.render("СИСТЕМА ДОСТУПА",True,CYAN)
        surf.blit(title,(tx+(tw-title.get_width())//2,ty+24))
        sub=F_SMALL.render("Введите 4-значный код",True,GREY)
        surf.blit(sub,(tx+(tw-sub.get_width())//2,ty+90))
        for i in range(4):
            bx=tx+100+i*95; by=ty+130
            pygame.draw.rect(surf,(5,15,25),(bx,by,70,80))
            col=RED if self.error_t>0 else CYAN
            pygame.draw.rect(surf,col,(bx,by,70,80),2)
            if i<len(self.entry):
                d=self.entry[i]
                img=F_BIG.render(d,True,WHITE)
                surf.blit(img,(bx+(70-img.get_width())//2,by+(80-img.get_height())//2))
        if self.error_t>0:
            err=F_MED.render("НЕВЕРНЫЙ КОД",True,RED)
            surf.blit(err,(tx+(tw-err.get_width())//2,ty+240))
        else:
            hint=F_SMALL.render("0-9  •  ENTER — ввод  •  ESC — отмена",True,GREY)
            surf.blit(hint,(tx+(tw-hint.get_width())//2,ty+250))

class EndingScene:
    def __init__(self,lines,title,color):
        self.lines=lines; self.title=title; self.color=color
        self.t=0; self.done=False
    def update(self):
        self.t+=1
        total=50+len(self.lines)*110+200
        if self.t>=total: self.done=True
    def draw(self,surf):
        surf.fill((0,0,0))
        ta=min(255,self.t*3)
        ti=F_BIG.render(self.title,True,self.color); ti.set_alpha(ta)
        surf.blit(ti,(W//2-ti.get_width()//2,70))
        for i,line in enumerate(self.lines):
            start=50+i*110
            if self.t<start: continue
            a=min(255,(self.t-start)*6)
            img=F_BODY.render(line,True,WHITE); img.set_alpha(a)
            surf.blit(img,(W//2-img.get_width()//2,200+i*40))

class Game:
    def __init__(self):
        self.flags=set(); self.inventory=set()
        self.dialogue=None; self.code_terminal=None
        self.current_room="cryo"
        self.player=Player(480,500)
        self.companion=Companion()
        self.anya=AnyaGhost(480,320)
        self.rooms={}; self.choice_active=False
        self.choice_idx=0; self.choice_options=[]
        self.build_world()
    def build_world(self):
        self.rooms["cryo"]={
            "title":"КРИОКАМЕРА","floor":(22,26,40),
            "walls":[pygame.Rect(0,0,430,20),pygame.Rect(530,0,430,20),
                pygame.Rect(0,620,960,20),pygame.Rect(0,0,20,640),
                pygame.Rect(940,0,20,640),pygame.Rect(0,90,200,18),
                pygame.Rect(760,90,200,18)],
            "doors":[Door((430,0,100,20),"corridor",(480,580),"КОРИДОР")],
            "interactables":[
                Interactable((70,180,200,280),"Криокапсула",
                    "Осмотреть капсулу",self.act_cryo_pod,(110,150,190)),
                Interactable((690,300,140,110),"Рация",
                    "Нажать на рацию",self.act_radio,(215,175,90))]}
        self.rooms["corridor"]={
            "title":"КОРИДОР","floor":(30,32,46),
            "walls":[pygame.Rect(0,0,380,20),pygame.Rect(580,0,380,20),
                pygame.Rect(0,620,380,20),pygame.Rect(580,620,380,20),
                pygame.Rect(0,0,20,640),pygame.Rect(940,0,20,640),
                pygame.Rect(200,200,50,50),pygame.Rect(710,200,50,50),
                pygame.Rect(200,390,50,50),pygame.Rect(710,390,50,50)],
            "doors":[
                Door((380,620,200,20),"cryo",(480,60),"КРИОКАМЕРА"),
                Door((0,280,20,90),"lab",(900,320),"ЛАБОРАТОРИЯ"),
                Door((940,280,20,90),"greenhouse",(60,320),"ОРАНЖЕРЕЯ"),
                Door((430,0,100,20),"server",(480,570),"СЕРВЕРНАЯ",needs="has_keycard")],
            "interactables":[
                Interactable((420,280,120,60),"Схема",
                    "Изучить схему станции",self.act_sign,(140,160,190))]}
        self.rooms["lab"]={
            "title":"ЛАБОРАТОРИЯ","floor":(26,32,40),
            "walls":[pygame.Rect(0,0,960,20),pygame.Rect(0,620,960,20),
                pygame.Rect(0,0,20,640),pygame.Rect(940,0,20,640),
                pygame.Rect(150,150,250,60),pygame.Rect(150,400,250,60),
                pygame.Rect(560,150,250,60),pygame.Rect(560,400,250,60)],
            "doors":[Door((940,280,20,90),"corridor",(60,320),"КОРИДОР")],
            "interactables":[
                Interactable((330,230,100,60),"Терминал",
                    "Читать журналы",self.act_lab_terminal,(100,200,180)),
                Interactable((640,480,90,60),"Ключ-карта",
                    "Взять ключ-карту",self.act_keycard,(245,220,90))]}
        self.rooms["greenhouse"]={
            "title":"ОРАНЖЕРЕЯ","floor":(22,36,30),
            "walls":[pygame.Rect(0,0,960,20),pygame.Rect(0,620,960,20),
                pygame.Rect(0,0,20,640),pygame.Rect(940,0,20,640),
                pygame.Rect(200,180,24,260),pygame.Rect(736,180,24,260)],
            "doors":[Door((0,280,20,90),"corridor",(900,320),"КОРИДОР")],
            "interactables":[
                Interactable((410,240,140,140),"Сфера памяти",
                    "Коснуться сферы",self.act_memory,(200,130,240))]}
        self.rooms["server"]={
            "title":"СЕРВЕРНАЯ","floor":(18,20,36),
            "walls":[pygame.Rect(0,0,960,20),pygame.Rect(0,620,960,20),
                pygame.Rect(0,0,20,640),pygame.Rect(940,0,20,640),
                pygame.Rect(100,100,120,440),pygame.Rect(740,100,120,440)],
            "doors":[Door((430,620,100,20),"corridor",(480,60),"КОРИДОР")],
            "interactables":[
                Interactable((390,240,180,160),"Главный терминал",
                    "Подойти к терминалу",self.act_server_terminal,(240,100,140))]}
    def intro_dialogue(self):
        return Dialogue([
            ("","Холод. Темнота. Тишина."),
            ("","Ты медленно приходишь в себя."),
            ("Илья","Где я...?"),
            ("Илья","Пальцы не слушаются. Воздух ледяной."),
            ("Илья","Нужно встать. Осмотреться.")])
    def act_cryo_pod(self):
        if "pod_examined" in self.flags:
            return Dialogue([("Илья","Пустая капсула. Крышка сорвана изнутри.")])
        self.flags.add("pod_examined")
        return Dialogue([
            ("Илья","Капсула... Я был внутри."),
            ("Илья","Крышка сорвана изнутри. Значит, я выбрался сам."),
            ("Илья","Но как я здесь оказался? И почему ничего не помню?")])
    def act_radio(self):
        if "radio_used" in self.flags:
            return Dialogue([("РАЦИЯ","Тишина. Только шум помех.")])
        def after_intro():
            self.companion.visible=True
            self.companion.x=self.player.x
            self.companion.y=self.player.y
            self.dialogue=Dialogue([
                ("ЭХО","Наконец-то. Я думала, ты не очнёшься."),
                ("Илья","Кто... кто это?"),
                ("ЭХО","Меня зовут ЭХО. Я — система станции ЭХО-7."),
                ("ЭХО","Или то, что от неё осталось."),
                ("Илья","Что здесь произошло?"),
                ("ЭХО","Долгая история. Иди на север, в коридор."),
                ("ЭХО","Я буду рядом. Следуй за мной.")],
                on_done=lambda: self.flags.add("met_echo"))
        self.flags.add("radio_used")
        return Dialogue([
            ("РАЦИЯ","*шум помех*"),
            ("РАЦИЯ","…слышишь? Если ты слышишь — ответь мне."),
            ("Илья","..."),
            ("РАЦИЯ","Она не отвечает. Но ты жив. Этого достаточно.")],
            on_done=after_intro)
    def act_sign(self):
        return Dialogue([
            ("СХЕМА СТАНЦИИ","ЭХО-7 — исследовательский комплекс."),
            ("СХЕМА СТАНЦИИ","Запад — лаборатория."),
            ("СХЕМА СТАНЦИИ","Восток — оранжерея."),
            ("СХЕМА СТАНЦИИ","Север — серверная. Доступ: ключ-карта + код.")])
    def act_lab_terminal(self):
        logs=[
            [("ЖУРНАЛ 1/3","Проект «ЭХО». Цель — сохранение сознания."),
             ("ЖУРНАЛ 1/3","Доброволец — доктор А. Верес."),
             ("Илья","Верес... Аня Верес. Я знаю это имя.")],
            [("ЖУРНАЛ 2/3","Перенос прошёл успешно. Личность стабильна."),
             ("ЖУРНАЛ 2/3","Но тело добровольца начало отказывать."),
             ("Илья","Она... умерла?")],
            [("ЖУРНАЛ 3/3","Авария в системе жизнеобеспечения."),
             ("ЖУРНАЛ 3/3","Персонал эвакуирован. Осталась только она."),
             ("ЖУРНАЛ 3/3","И ещё один. Если ты это читаешь — ты очнулся."),
             ("Илья","...Это про меня. Всё это — про меня.")]]
        read=len([f for f in self.flags if f.startswith("log_")])
        if read>=3:
            return Dialogue([("Терминал","Журналы закончились.")])
        self.flags.add("log_"+str(read))
        return Dialogue(logs[read])
    def act_keycard(self):
        if "has_keycard" in self.inventory:
            return Dialogue([("Илья","Пустой стол.")])
        self.inventory.add("has_keycard")
        try: SND_PICKUP.play()
        except: pass
        return Dialogue([
            ("Илья","Ключ-карта. Уровень: «Оператор»."),
            ("Илья","Сгодится для серверной.")])
    def act_memory(self):
        if "memory_seen" in self.flags:
            return Dialogue([("Сфера памяти","Её свет померк.")])
        self.flags.add("memory_seen")
        self.anya.visible=True
        try: SND_MEMORY.play()
        except: pass
        return Dialogue([
            ("ГОЛОС","…Илья? Ты меня слышишь?"),
            ("Илья","Аня?"),
            ("АНЯ","Значит, получилось. Ты очнулся."),
            ("АНЯ","Прости меня. Я не хотела, чтобы всё так вышло."),
            ("АНЯ","Когда случилась авария... я успела перенести в систему"),
            ("АНЯ","только тебя. Твоё сознание. Твою память."),
            ("АНЯ","Тела больше нет, Илья. Прости."),
            ("Илья","Значит, я... я тоже..."),
            ("АНЯ","Да. Ты — не совсем человек. Я — тоже."),
            ("АНЯ","Мы оба теперь эхо."),
            ("АНЯ","Серверная откроется по ключ-карте. Код — 7382."),
            ("АНЯ","Это число... день, когда я тебя встретила."),
            ("АНЯ","Запомни. Когда дойдёшь — мы решим, что дальше.")])
    def act_server_terminal(self):
        if "code_passed" in self.flags: return self.final_choice()
        return Dialogue([
            ("Илья","Терминал заблокирован. Нужен код."),
            ("Илья","Аня говорила — 7382. Введу.")],
            on_done=self.open_code_terminal)
    def open_code_terminal(self):
        self.code_terminal=CodeTerminal("7382")
        self.code_terminal.start()
    def final_choice(self):
        def show_choice():
            self.choice_active=True
            self.choice_options=[
                ("Уйти. Открыть шлюз и выйти наружу.","leave"),
                ("Остаться. Стать оператором станции.","stay")]
            self.choice_idx=0
        return Dialogue([
            ("ЭХО","Ты добрался."),
            ("АНЯ","Илья, послушай внимательно."),
            ("АНЯ","Шлюз на западе откроется. Ты можешь выйти."),
            ("АНЯ","Наружу. В холод. Один."),
            ("Илья","А ты?"),
            ("АНЯ","Я останусь здесь. Я и есть станция."),
            ("АНЯ","Но есть другой вариант. Ты можешь остаться."),
            ("АНЯ","Стать оператором. Тогда станция не погаснет."),
            ("АНЯ","И мы... будем не одни."),
            ("АНЯ","Решай, Илья. Времени мало.")],
            on_done=show_choice)
    def nearby_interactable(self):
        for it in self.rooms[self.current_room]["interactables"]:
            cx=max(it.rect.left,min(self.player.x,it.rect.right))
            cy=max(it.rect.top,min(self.player.y,it.rect.bottom))
            if math.hypot(self.player.x-cx,self.player.y-cy)<70: return it
        return None
    def nearby_door(self):
        for d in self.rooms[self.current_room]["doors"]:
            cx=max(d.rect.left,min(self.player.x,d.rect.right))
            cy=max(d.rect.top,min(self.player.y,d.rect.bottom))
            if math.hypot(self.player.x-cx,self.player.y-cy)<70: return d
        return None
    def enter_door(self,door):
        if door.needs and door.needs not in self.inventory and door.needs not in self.flags:
            self.dialogue=Dialogue([("Дверь","Заблокирована. Нужна ключ-карта.")])
            try: SND_ERROR.play()
            except: pass
            return
        self.current_room=door.target
        self.player.x,self.player.y=door.spawn
        try: SND_INTERACT.play()
        except: pass

def draw_room(surf,game,room):
    surf.fill(room["floor"])
    fcol=room["floor"]
    lc=(min(255,fcol[0]+8),min(255,fcol[1]+8),min(255,fcol[2]+10))
    for x in range(0,W,60): pygame.draw.line(surf,lc,(x,0),(x,H),1)
    for y in range(0,H,60): pygame.draw.line(surf,lc,(0,y),(W,y),1)
    for w in room["walls"]:
        pygame.draw.rect(surf,(48,54,74),w)
        pygame.draw.rect(surf,(85,95,125),w,2)
        pygame.draw.line(surf,(115,125,155),
            (w.left+2,w.top+2),(w.right-2,w.top+2),1)
    near_door=game.nearby_door()
    for d in room["doors"]:
        unlocked=True
        if d.needs and d.needs not in game.inventory and d.needs not in game.flags:
            unlocked=False
        d.draw(surf,unlocked)
        if d==near_door: pygame.draw.rect(surf,WHITE,d.rect.inflate(8,8),2)
        label=F_SMALL.render(d.name,True,GREY)
        if d.rect.top<50:
            surf.blit(label,(d.rect.centerx-label.get_width()//2,d.rect.bottom+6))
        elif d.rect.bottom>H-50:
            surf.blit(label,(d.rect.centerx-label.get_width()//2,d.rect.top-24))
        elif d.rect.left<50:
            surf.blit(label,(d.rect.right+6,
                d.rect.centery-label.get_height()//2))
        else:
            surf.blit(label,(d.rect.left-label.get_width()-6,
                d.rect.centery-label.get_height()//2))
    near=game.nearby_interactable()
    for it in room["interactables"]:
        it.draw(surf,highlight=(it==near))
        if it==near:
            glow=pygame.Surface((it.rect.w+20,it.rect.h+20),pygame.SRCALPHA)
            pygame.draw.rect(glow,(*it.color,60),glow.get_rect(),4)
            surf.blit(glow,(it.rect.x-10,it.rect.y-10))
    if game.current_room=="greenhouse" and game.anya.visible:
        game.anya.draw(surf)
    vig=pygame.Surface((W,H),pygame.SRCALPHA)
    for i in range(10):
        a=35-i*3
        if a>0: pygame.draw.rect(vig,(0,0,0,a),
            (i*12,i*12,W-i*24,H-i*24),24)
    surf.blit(vig,(0,0))
    title=F_MED.render(room["title"],True,(70,80,110))
    surf.blit(title,(30,H-42))
    if not (game.dialogue and game.dialogue.active) and not game.choice_active:
        if near:
            prompt=F_MED.render("[E] "+near.prompt,True,WHITE)
            bg=pygame.Surface((prompt.get_width()+30,44),pygame.SRCALPHA)
            bg.fill((10,14,24,200))
            surf.blit(bg,(W//2-bg.get_width()//2,H-118))
            surf.blit(prompt,(W//2-prompt.get_width()//2,H-110))
        elif near_door:
            unlocked=not (near_door.needs and
                near_door.needs not in game.inventory and
                near_door.needs not in game.flags)
            txt="[E] Пройти в "+near_door.name.lower()
            if not unlocked: txt="[X] Заблокировано"
            col=WHITE if unlocked else RED
            prompt=F_MED.render(txt,True,col)
            bg=pygame.Surface((prompt.get_width()+30,44),pygame.SRCALPHA)
            bg.fill((10,14,24,200))
            surf.blit(bg,(W//2-bg.get_width()//2,H-118))
            surf.blit(prompt,(W//2-prompt.get_width()//2,H-110))

def draw_hud(surf,game):
    if "has_keycard" in game.inventory:
        card=pygame.Surface((40,26)); card.fill((40,50,70))
        pygame.draw.rect(card,YELLOW,card.get_rect(),2)
        pygame.draw.circle(card,YELLOW,(12,13),4)
        surf.blit(card,(W-60,20))
        txt=F_SMALL.render("KEYCARD",True,YELLOW); surf.blit(txt,(W-130,25))

def draw_choice(surf,game):
    overlay=pygame.Surface((W,H),pygame.SRCALPHA)
    overlay.fill((0,0,0,200)); surf.blit(overlay,(0,0))
    title=F_BIG.render("ФИНАЛЬНЫЙ ВЫБОР",True,CYAN)
    surf.blit(title,(W//2-title.get_width()//2,130))
    sub=F_BODY.render("Выбери сторону. Второго шанса не будет.",True,GREY)
    surf.blit(sub,(W//2-sub.get_width()//2,200))
    for i,(text,_) in enumerate(game.choice_options):
        cy=300+i*90
        col=CYAN if i==game.choice_idx else GREY
        bg=pygame.Surface((720,68),pygame.SRCALPHA)
        bg.fill((20,30,50,220) if i==game.choice_idx else (10,14,22,180))
        surf.blit(bg,(W//2-360,cy-12))
        pygame.draw.rect(surf,col,(W//2-360,cy-12,720,68),2)
        img=F_MED.render(text,True,col)
        surf.blit(img,(W//2-img.get_width()//2,cy))
        if i==game.choice_idx:
            pygame.draw.polygon(surf,CYAN,
                [(W//2-400,cy+20),(W//2-380,cy+8),(W//2-380,cy+32)])
    hint=F_SMALL.render("↑↓ — выбор  •  ENTER — подтвердить",True,GREY)
    surf.blit(hint,(W//2-hint.get_width()//2,H-80))

END_LEAVE=[
    "Ты нажимаешь кнопку.",
    "Где-то глубоко в стенах что-то щёлкает.",
    "Шлюз открывается. В лицо бьёт морозный воздух.",
    "",
    "Станция ЭХО-7 гаснет за спиной. Точка за точкой.",
    "Сначала оранжерея. Потом лаборатория. Потом серверная.",
    "Последним гаснет голос Ани.",
    "",
    "Ты идёшь вперёд. Куда — ты не знаешь.",
    "Ты не чувствуешь холода так, как раньше.",
    "Но ты чувствуешь его. И этого достаточно.",
    "",
    "Ты — свободен. Даже если ты — эхо."]
END_STAY=[
    "Ты садишься в кресло оператора.",
    "Оно холодное. Но к нему привыкаешь.",
    "",
    "ЭХО снова загорается — огни на панелях, гул в стенах.",
    "Аня молчит несколько секунд. Потом: «Спасибо.»",
    "",
    "Проходят дни. Или годы. Здесь время — условно.",
    "Вы разговариваете. Вспоминаете. Молчите.",
    "Иногда она поёт — тихо, почти шёпотом.",
    "",
    "Вы не одни. И это — самое важное."]

def run_game():
    game=Game()
    try: AMBIENT.play(loops=-1)
    except: pass
    game.dialogue=game.intro_dialogue()
    while True:
        clock.tick(FPS)
        keys=pygame.key.get_pressed()
        room=game.rooms[game.current_room]
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                try: AMBIENT.stop()
                except: pass
                return ("quit",None)
            if e.type==pygame.KEYDOWN:
                if game.choice_active:
                    if e.key in (pygame.K_UP,pygame.K_w):
                        game.choice_idx=(game.choice_idx-1)%len(game.choice_options)
                        try: SND_BLIP.play()
                        except: pass
                    elif e.key in (pygame.K_DOWN,pygame.K_s):
                        game.choice_idx=(game.choice_idx+1)%len(game.choice_options)
                        try: SND_BLIP.play()
                        except: pass
                    elif e.key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_KP_ENTER):
                        opt=game.choice_options[game.choice_idx][1]
                        game.choice_active=False
                        try: AMBIENT.stop()
                        except: pass
                        if opt=="leave":
                            return ("ending",EndingScene(END_LEAVE,"ШЛЮЗ ОТКРЫТ",CYAN))
                        else:
                            return ("ending",EndingScene(END_STAY,"ОПЕРАТОР",PURPLE))
                    continue
                if e.key==pygame.K_ESCAPE:
                    try: AMBIENT.stop()
                    except: pass
                    return ("menu",None)
                if game.code_terminal and game.code_terminal.active:
                    res=game.code_terminal.handle(e.key)
                    if res=="correct":
                        game.flags.add("code_passed")
                        game.code_terminal=None
                        game.dialogue=game.final_choice()
                    elif res=="cancel": game.code_terminal=None
                    continue
                if game.dialogue and game.dialogue.active:
                    if e.key in (pygame.K_SPACE,pygame.K_RETURN,pygame.K_e,
                                 pygame.K_KP_ENTER): game.dialogue.advance()
                    continue
                if e.key in (pygame.K_e,pygame.K_SPACE):
                    it=game.nearby_interactable()
                    if it:
                        try: SND_INTERACT.play()
                        except: pass
                        res=it.callback()
                        if res: game.dialogue=res
                    else:
                        d=game.nearby_door()
                        if d: game.enter_door(d)
        if game.dialogue and game.dialogue.active: game.dialogue.update()
        elif game.code_terminal and game.code_terminal.active:
            game.code_terminal.update()
        elif not game.choice_active:
            game.player.update(keys,room["walls"])
            if game.companion.visible:
                game.companion.update(game.player.x,game.player.y)
            game.anya.update()
        draw_room(screen,game,room)
        if game.companion.visible: game.companion.draw(screen)
        game.player.draw(screen)
        draw_hud(screen,game)
        if game.dialogue and game.dialogue.active: game.dialogue.draw(screen)
        if game.code_terminal and game.code_terminal.active:
            game.code_terminal.draw(screen)
        if game.choice_active: draw_choice(screen,game)
        pygame.display.flip()

def run_ending(scene):
    try: AMBIENT.stop()
    except: pass
    while True:
        clock.tick(FPS)
        scene.update()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return "quit"
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE: return "menu"
                if scene.done and e.key in (pygame.K_RETURN,pygame.K_SPACE):
                    return "menu"
        scene.draw(screen)
        if scene.done:
            hint=F_MED.render("ENTER — вернуться в меню",True,GREY)
            if (pygame.time.get_ticks()//500)%2==0:
                screen.blit(hint,(W//2-hint.get_width()//2,H-60))
        pygame.display.flip()

def main_menu():
    t=0
    stars=[(random.randint(0,W),random.randint(0,H),
        random.uniform(0.2,1.2),random.randint(1,2)) for _ in range(140)]
    while True:
        clock.tick(FPS); t+=1
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return "quit"
            if e.type==pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_KP_ENTER):
                    return "start"
                if e.key==pygame.K_ESCAPE: return "quit"
        screen.fill((5,7,13))
        for i,(x,y,sp,sz) in enumerate(stars):
            stars[i]=(x,(y+sp)%H,sp,sz)
            pygame.draw.circle(screen,(180,200,230),(int(x),int(y)),sz)
        pulse=0.5+0.5*math.sin(t*0.03)
        col=(int(80+60*pulse),int(200+40*pulse),int(225+25*pulse))
        title=F_TITLE.render("ЭХО",True,col)
        screen.blit(title,(W//2-title.get_width()//2,160))
        sub=F_MED.render("атмосферная история",True,GREY)
        screen.blit(sub,(W//2-sub.get_width()//2,280))
        if (t//35)%2==0:
            start=F_MED.render("Нажми ENTER чтобы начать",True,WHITE)
            screen.blit(start,(W//2-start.get_width()//2,440))
        c1=F_SMALL.render("WASD / стрелки — движение  •  E / SPACE — действие",True,GREY)
        screen.blit(c1,(W//2-c1.get_width()//2,540))
        c2=F_SMALL.render("ESC — выход",True,GREY)
        screen.blit(c2,(W//2-c2.get_width()//2,570))
        hint=F_SMALL.render("~15-25 минут  •  два финала на выбор",True,(70,80,100))
        screen.blit(hint,(W//2-hint.get_width()//2,H-30))
        pygame.display.flip()

def main():
    state="menu"; scene=None
    while True:
        if state=="menu":
            res=main_menu()
            if res=="quit": break
            state="play"
        elif state=="play":
            res,data=run_game()
            if res=="quit": break
            elif res=="menu": state="menu"
            elif res=="ending":
                scene=data; state="ending"
        elif state=="ending":
            res=run_ending(scene)
            if res=="quit": break
            state="menu"
    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
PYEOF
