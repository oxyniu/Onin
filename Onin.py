import pygame
import sys
import time
import mido
import random
from collections import deque

def envalue(t,d):
    global width,height,tps,fpos,score,combo,c_sec
    global c_full,c_btime,c_fbig,tmiss,s_ttf,c_title
    global scolor,fcolor,tcolor,nspeed,kch,s_note
    global s_music,s_icon,pts,timelist,chanlist
    #const settings:int
    width   = 960                     #window width
    height  = 640                     #window height
    tps     = 60                      #game tps(fps)
    fpos    = 560                     #judging line position
    score   = 0                       #beginning score
    combo   = 0                       #beginning combo
    c_sec   = 1000                    #convertion ms->s
    c_full  = 1000000                 #full score
    c_btime = 1000                    #reject_judging time
    c_fbig  = 24                      #text size
    tmiss   = 250                     #range of miss
    #const settings:string
    s_ttf   = "Consolas"              #font
    c_title = "Onin v1.6 by Oxniu"    #screen title
    #const settings:tuple
    scolor  = (0,0,0)                 #background color
    fcolor  = (255,255,255)           #judging line color
    tcolor  = (255,255,255)           #text color
    #const settings:list
    nspeed  = [0,3]                   #falling speed
    kch     = [pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_j]
                                      #keys in each channel
    timelist= t
    chanlist= d
    #const settings:files
    s_note  = "res/note.png"              #note photo
    s_music = "res/nocturne.ogg"          #music
    s_icon  = "res/icon.png"              #icon photo
    pts     = len(timelist)

class Note(object):
    def __init__(self,apt,chan,num):
        self.nid     = num
        self.nshape  = pygame.image.load(s_note)
        self.nstatus = True
        self.nin     = apt
        self.n       = chan
        self.nwidth  = 40
        self.nheight = 10
        self.nleft   = chan*self.nwidth
        self.ntop    = fpos-apt/c_sec*tps*nspeed[1]
    def update(self):
        if self.nstatus:
            ncurrent_time = pygame.time.get_ticks()-zerotime
            screen.blit(self.nshape,(self.nleft,self.ntop,self.nwidth,self.nheight))
            if ncurrent_time-self.nin>tmiss:
                global combo
                combo = 0
                self.nstatus = False
                notelist[self.n].popleft()
                return True
            self.ntop = fpos-(self.nin-ncurrent_time)/c_sec*tps*nspeed[1]
            return False
    def judge(self):
        if self.nstatus:
            global combo,score,notelist
            ncurrent_time = pygame.time.get_ticks()-zerotime
            if abs(ncurrent_time-self.nin)<c_btime:
                if abs(ncurrent_time-self.nin)>tmiss:
                    combo = 0
                    self.nstatus = False
                    notelist[self.n].popleft()
                else:
                    score += c_full/pts
                    combo += 1
                    self.nstatus = False
                    notelist[self.n].popleft()
class Keysdealing():
    def __init__(self):
        self.kdict = {}
        for i in range(len(kch)):
            self.kdict[(kch[i],i)] = False
    def update(self):
        keys = pygame.key.get_pressed()
        for ks in self.kdict.keys():
            if keys[ks[0]]:
                if not self.kdict[ks]:
                    if len(notelist[ks[1]]):
                        notelist[ks[1]][0].judge()
                    self.kdict[ks] = True
            else:
                self.kdict[ks] = False
def display_score():
    fsc = font.render(str(combo),1,tcolor)
    fsd = font.render(str(int(score)),1,tcolor)
    screen.blit(fsc,[screen.get_width()/2-fsc.get_width()/2,0])
    screen.blit(fsd,[screen.get_width()-fsd.get_width(),0])
def note_update():
    tmp=False
    for i in range(maxch+1):
        for j in range(len(notelist[i])):
            if notelist[i][j].update():
                tmp=True
                break
        if tmp:
            for j in range(len(notelist[i])):
                notelist[i][j].update()
def event_detect():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainquit()
            sys.exit()
def notelist_gen():
    global maxch
    maxch = 0
    for chn in chanlist:
        maxch= max(maxch,chn)
    global notelist
    notelist = [deque([]) for i in range(maxch+1)]
    for ti in range(pts):
        notelist[chanlist[ti]].append(Note(timelist[ti],chanlist[ti],ti))
def maininit(t,d):
    envalue(t,d)
    global screen,clock,font,keyd
    pygame.init()                                        #pygame init
    pygame.font.init()                                   #pygame.font init
    screen = pygame.display.set_mode([width,height])     #define screen
    clock  = pygame.time.Clock()                         #define clock
    pygame.mixer.music.load(s_music)                     #load music
    font   = pygame.font.SysFont(s_ttf,c_fbig)           #load font
    pygame.display.set_caption(c_title)                  #load title
    pygame.display.set_icon(pygame.image.load(s_icon))   #load icon
    keyd   = Keysdealing()                               #create instance
    notelist_gen()                                       #generate notelist
def mainloop():
    time.sleep(2)
    global zerotime
    zerotime = pygame.time.get_ticks()
    pygame.mixer.music.play()
    while True:
        clock.tick(tps)
        screen.fill(scolor)
        pygame.draw.line(screen,fcolor,(0,fpos),(width-1,fpos))
        display_score()
        note_update()
        event_detect()
        keyd.update()
        pygame.display.update()
def mainquit():
    pygame.mixer.music.stop()
    pygame.quit()
def main(t,d):
    maininit(t,d)
    mainloop()
    mainquit()

if __name__=="__main__":
    mid = mido.MidiFile("res/nocturne.mid")
    for msg in mid.tracks[0]:
        try:
            tempo = msg.tempo
        except:
            continue
    ad,do,dua,t = 0,60*1000/(mido.tempo2bpm(tempo)*mid.ticks_per_beat),0,set()
    for msg in mid.tracks[1]:
        ad += msg.time
        if ad%(mid.ticks_per_beat/32)==0:
            t.add(ad)
    t,d = list(sorted(t)),[]
    for i in range(len(t)):
        d.append(random.randint(0,3))
        t[i] *= do
    main(t,d)
