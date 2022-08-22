import pyge
import pygame
import random
import math
import threading
import time

wsize = 200

class ba:
    def __init__(self, clr, name, cso, hd):
        self.clr = clr
        self.name = name
        self.can_step_on = cso
        self.hard = hd

class block:
    def __init__(self, tp):
        self.tp = tp
        self.kingdom = ""
        self.lst_upd_tick = 0
        self.border = False
        self.district_border = False
        self.army = 0
        self.district = ""

def army_size_to_str(amsz):
    if amsz < 1000:
        return str(amsz)
    else:
        return str(round(amsz/1000, 1))+"k"

class obj(pyge.Picture):
    def __init__(self, sf, x=-1, y=-1):
        super().__init__(pyge.rect(0, 0, (0, 0, 0)), 0, 0)
        self.x, self.y = x, y
        self.clr = sf

    def draw(self, gm: pyge.Game):
        self.pos_in_world()
        blksz = min(max(2, int(blksza)), 32)
        vx = int(x) - WINSZ[0] // blksz // 2
        vy = int(y) - WINSZ[1] // blksz // 2
        if 0 <= (self.x - vx) * blksz <= WINSZ[0] and 0 <= (self.y - vy) * blksz <= WINSZ[1]: # FIXME: Wrong coord
            gm.sc.blit(pyge.rect(blksz, blksz, self.clr), ((self.x - vx) * blksz, (self.y - vy) * blksz))

    def pos_in_world(self):
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x >= wsize:
            self.x = wsize-1
        if self.y >= wsize:
            self.y = wsize-1

class kingdom:
    def __init__(self, name):
        self.name = name
        self.capital = (random.randint(1, wsize-2), random.randint(1, wsize-2))
        cnt = 0
        while (world[self.capital[0]][self.capital[1]].tp in (2, 4) or world[self.capital[0]][self.capital[1]].kingdom != "") and cnt < 1000:
            self.capital = (random.randint(1, wsize - 2), random.randint(1, wsize - 2))
        if cnt >= 1000:
            return
        world[self.capital[0]][self.capital[1]].kingdom = self.name
        world[self.capital[0]][self.capital[1]].district = self.name
        kingdoms[name] = self
        self.display_clr = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

        self.adj_kingdoms = []
        self.enemy = []
        self.ally = []
        self.allyreq = []
        self.army = 10
        self.gold = 10
        self.area = 1
        self.border_length = 1
        self.lst_border_length = 1
        self.lst_self_area = 1
        self.basic_defence = 10
        self.army_in_cell = 0
        self.peaceful = random.randint(2, 5)

    def aiupdate(self):
        if self.area != 0:
            self.lst_self_area = self.area
        if self.border_length != 0:
            self.lst_border_length = self.border_length
        self.basic_defence = max(self.army // 2 // self.lst_border_length, 5)
        if gm.tick % 10 == 0:
            for i in self.enemy:
                if i in self.ally:
                    self.ally.remove(i)

        for i in self.allyreq:
            if i not in self.enemy and i not in self.ally:
                self.ally.append(i)
                self.allyreq.remove(i)

        mxpk, mnpk = "", ""
        for i in self.adj_kingdoms:
            if mxpk == "" or kingdoms[mxpk].calc_score() < kingdoms[i].calc_score():
                mxpk = i
            if mnpk == "" or kingdoms[mnpk].calc_score() > kingdoms[i].calc_score():
                mnpk = i
        if len(self.enemy) == 0:
            if mnpk != "" and kingdoms[mnpk].calc_score()*(1+self.peaceful/10) < self.calc_score():
                self.enemy.append(mnpk)
                kingdoms[mnpk].enemy.append(self.name)
            elif mxpk != "" and kingdoms[mxpk].calc_score() < self.calc_score()*1.5:
                self.enemy.append(mxpk)
                kingdoms[mxpk].enemy.append(self.name)
        if mnpk != "":
            for i in self.adj_kingdoms:
                if i != mxpk and kingdoms[mnpk].calc_score()*(1+self.peaceful/10) >= self.calc_score():
                    kingdoms[i].allyreq.append(self.name)

    def update(self):
        for i in self.enemy.copy():
            if kingdoms[i].area == 0:
                self.enemy.remove(i)
                kingdoms[i].enemy.remove(self.name)
        if self.name != "player":
            self.aiupdate()
        else:
            # gm.draw_text("Player", (self.capital[0] - vx) * blksz, (self.capital[1] - vy) * blksz, color=(0, 0, 0))
            pass
    def calc_score(self):
        return self.army + self.army_in_cell + self.gold + self.area*10

blkattrs = [ba((0, 0, 0), "Bedrock", False, 1000000), ba((0, 200, 0), "Grass", True, 10), ba((0, 60, 255), "Ocean", False, 1000000), ba((247, 238, 214), "Sand", True, 10), ba((100, 100, 100), "Mountain", True, 200), ba((255, 255, 255), "Snow", True, 10)]
world = [[block(0) for i in range(wsize)] for j in range(wsize)]

kingdoms = {}

blksz = 0
days = 0

x, y = wsize/2, wsize/2
blksza = 16
WINSZ = (800, 600)

biome = [[0]*wsize for i in range(wsize)]
mountbetween = []

vx = 0
vy = 0

# generate world:

namechoices = ["Mongolia", "North Korea", "South Korea", "Japan", "Philippines", "Vietnam", "Laos", "Cambodia", "Myanmar", "Thailand", "Malaysia", "Brunei", "Singapore", "Indonesia", "East Timor", "Nepal", "Bhutan", "Bangladesh", "India", "Pakistan", "Sri Lanka", "Maldives", "Kazakhstan", "Kyrgyzstan", "Tajikistan", "Uzbekistan", "Turkmenistan", "Afghanistan", "Iraq", "Iran", "Syria", "Jordan", "Lebanon", "Israel", "Palestine", "Saudi Arabia", "Bahrain", "Qatar", "Kuwait", "United Arab Emirates", "Oman", "Yemen", "Georgia", "Armenia", "Azerbaijan", "Turkey", "Cyprus", "43个国家", "Finland", "Sweden", "Norway", "Iceland", "Denmark", "Faroe Islands", "Estonia", "Latvia", "Lithuania", "Belorussia", "Russia", "Ukraine", "Moldova", "Poland", "Czecho", "slovakia", "Hungary", "German", "Austria", "Switzerland", "Liechtenstein", "United Kingdom", "Ireland", "Netherlands", "Belgium", "Luxembourg", "France", "Monaco", "Romania", "Bulgaria", "Serbia", "Macedonia", "Albania", "Greece", "Slovenia", "Croatia", "Bosnia-Herzegovina", "Italy", "Vatican", "San Marino", "Malta", "Spain", "Portugal", "Andorra", "United States of America", "Canada", "the United Mexican States", "Guatemala", "Belize", "Salvador", "Honduras", "Panama", "Bahamas", "Cuba", "Jamaica", "Haiti", "The Dominican Republic", "Costa Rica", "Saint Kitts and Nevis", "Antigua and Barbuda", "The Commonwealth of Dominica", "Saint Lucia", "Saint Vincent and the Grenadines", "Barbados", "Grenada", "Trinidad and Tobago", "Nicaragua"]

def getaname():
    if len(namechoices) <= 0 or random.randint(0, 2) == 0:
        s = ""
        av = ["a", "e", "i", "o", "u", "a", "e", "i", "o", "u", "ai", "ao", "ou"]
        tv = ["b", "p", "m", "f", "c", "d", "g", "h", "j", "k", "l", "n", "p", "qu", "r", "s", "t", "w", "ch"]
        for i in range(random.choice([2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4])):
            s += random.choice(tv)
            s += random.choice(av)
            if random.randint(0, 6) == 0:
                chk = random.choice(av)
                if chk[0] != s[-1] and chk[0] != s[-2] and (len(chk)==1 or (chk[1] != s[-1] and chk[1] != s[-2])):
                    s += chk
        if random.randint(0, 2) == 0:
            s += random.choice(["l", "b", "p", "m", "d", "g", "n", "s", "s"])
            if random.randint(0, 2) == 0:
                s += random.choice("ia")
        if random.randint(0, 3) == 0:
            s = random.choice(av) + s
        if random.randint(0, 4) == 0:
            if random.randint(0, 3) == 0:
                s = random.choice(["Empire of "]) + s
            else:
                s += random.choice([" Empire", " Union", " Kingdom", " Dynasty"])
        return s.capitalize()
    nc = random.choice(namechoices)
    namechoices.remove(nc)
    return nc

def generate_world(gm: pyge.Game):
    global x, y
    print(f"\rGenerating world: 0/100%", end="")
    build_biomes()
    build_world()
    kingdom("player")
    for i in range(random.randint(60, 100)):
        kingdom(getaname())
    x, y = kingdoms["player"].capital

def build_world():
    global world
    for i in range(random.choice([1, 1, 2, 2, 2, 2, 3, 1, 1, 1, 2, 2, 2, 2, 3, 4])):
        xx = (random.randint(1, 4), random.randint(1, 4))
        if random.randint(0, 2) == 0:
            xx = (xx[0], 2)
        if xx[0] == 1 and random.randint(0, 1) == 0:
            continue
        if xx[0] == xx[1]:
            continue
        mountbetween.append(xx)
    for i in range(wsize):
        for j in range(wsize):
            if biome[i][j] == 1:
                world[i][j] = block(1)
            elif biome[i][j] == 2:
                world[i][j] = block(2)
            elif biome[i][j] == 3:
                world[i][j] = block(3)
            elif biome[i][j] == 4:
                world[i][j] = block(5)
        print(f"\rBuilding biome: {int((i*wsize+j)/(wsize*wsize)*3)+90}/100%", end="")
    for i in range(wsize):
        for j in range(wsize):
            if world[i][j].tp == 1:
                if (i-1>=0 and world[i-1][j].tp == 2) or (i+1<wsize and world[i+1][j].tp == 2) or (j-1>=0 and world[i][j-1].tp == 2) or (j+1<wsize and world[i][j+1].tp == 2):
                    world[i][j] = block(3)
                    if i - 1 >= 0 and world[i - 1][j].tp == 1 and random.randint(0, 2) == 0:
                        world[i - 1][j] = block(3)
                    if i + 1 < wsize and world[i + 1][j].tp == 1 and random.randint(0, 2) == 0:
                        world[i + 1][j] = block(3)
                    if j-1 >= 0 and world[i][j-1].tp == 1 and random.randint(0, 2) == 0:
                        world[i][j-1] = block(3)
                    if j + 1 < wsize and world[i][j + 1].tp == 1 and random.randint(0, 2) == 0:
                        world[i][j + 1] = block(3)
            for k, l in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                if 0 <= i + k < wsize and 0 <= j + l < wsize:
                    if (biome[i + k][j + l], biome[i][j]) in mountbetween or (biome[i][j], biome[i + k][j + l]) in mountbetween:
                        if random.randint(0, 1) == 0:
                            break
                        for kx, lx in ((0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)):
                            if 0 <= i + kx < wsize and 0 <= j + lx < wsize:
                                if random.randint(0, 2) <= 1:
                                    world[i+kx][j+lx] = block(4)
                        break
            print(f"\rBuilding biome: {int((i*wsize+j)/(wsize*wsize)*7)+93}/100%", end="")
    print("\nDone generating world!")

def rect_with_alpha(w, h, color=(0, 0, 0), alp = 255):
    sf = pygame.Surface((w, h), pygame.SRCALPHA)
    sf.fill((color[0], color[1], color[2], alp))
    return sf

def build_biomes():
    global biome
    mpt = [1, 1, 2, 2, 3, 1, 1, 2, 2, 1, 1, 2, 2, 3, 1, 1, 2, 2, 3, 4]+[2]
    for i in range(wsize//8):
        biome[random.randint(1, wsize-2)][random.randint(1, wsize-2)] = random.choice(mpt)
    while True:
        bkup = [[biome[i][j] for j in range(wsize)] for i in range(wsize)]
        cnt = 0
        for i in range(wsize):
            for j in range(wsize):
                if biome[i][j] != 0:
                    cnt += 1
                if biome[i][j] != 0:
                    if i - 1 >= 0 and bkup[i - 1][j] == 0 and random.randint(0, 2) == 0:
                        bkup[i - 1][j] = biome[i][j]
                    if i + 1 < wsize and bkup[i + 1][j] == 0 and random.randint(0, 2) == 0:
                        bkup[i + 1][j] = biome[i][j]
                    if j-1 >= 0 and bkup[i][j-1] == 0 and random.randint(0, 2) == 0:
                        bkup[i][j-1] = biome[i][j]
                    if j + 1 < wsize and bkup[i][j + 1] == 0 and random.randint(0, 2) == 0:
                        bkup[i][j + 1] = biome[i][j]
        biome = [[bkup[i][j] for j in range(wsize)] for i in range(wsize)]
        print(f"\rBuilding biome: {int(cnt/(wsize*wsize)*90)}/100% ({cnt} blocks)", end="")
        if cnt == wsize*wsize:
            return


def dist(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

ticks_per_day = 20
map_mode = 0

def update_each_cell():
    global days
    adjs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    upd_tick = 0
    while gm.running:
        if upd_tick % ticks_per_day == 0:
            days += 1
        for i in kingdoms:
            kingdoms[i].area = 0
            kingdoms[i].border_length = 0
            kingdoms[i].army_in_cell = 0
            kingdoms[i].adj_kingdoms = []
        for i in range(wsize):
            for j in range(wsize):
                if world[i][j].kingdom != "":
                    kingdoms[world[i][j].kingdom].area += 1
                    kingdoms[world[i][j].kingdom].army_in_cell += world[i][j].army
                    if world[i][j].border:
                        kingdoms[world[i][j].kingdom].border_length += 1
                    for k, l in adjs:
                        if 0 <= i+k < wsize and 0 <= j+l < wsize:
                            if world[i + k][j + l].kingdom != world[i][j].kingdom and world[i + k][j + l].kingdom != "" and world[i + k][j + l].kingdom not in kingdoms[world[i][j].kingdom].adj_kingdoms:
                                kingdoms[world[i][j].kingdom].adj_kingdoms.append(world[i + k][j + l].kingdom)
        ntm = time.time()
        for i in range(wsize):
            for j in range(wsize):
                if world[i][j].kingdom != "" and upd_tick % ticks_per_day == 0:
                    if world[kingdoms[world[i][j].kingdom].capital[0]][kingdoms[world[i][j].kingdom].capital[1]].kingdom != world[i][j].kingdom:
                        world[i][j].kingdom = world[kingdoms[world[i][j].kingdom].capital[0]][kingdoms[world[i][j].kingdom].capital[1]].kingdom
                    for k, l in adjs:
                        if 0 <= i+k < wsize and 0 <= j+l < wsize:
                            if world[i+k][j+l].kingdom == "" and world[i+k][j+l].tp not in (2, 4) and world[i][j].lst_upd_tick != upd_tick:
                                world[i+k][j+l].kingdom = world[i][j].kingdom
                                world[i + k][j + l].lst_upd_tick = upd_tick
                                world[i+k][j+l].district = world[i][j].district
                            if world[i+k][j+l].kingdom != world[i][j].kingdom and world[i+k][j+l].kingdom in kingdoms[world[i][j].kingdom].enemy and world[i][j].lst_upd_tick != upd_tick and world[i+k][j+l].lst_upd_tick != upd_tick:
                                totala = 0
                                for kx, lx in adjs:
                                    if 0 <= i + k + kx < wsize and 0 <= j + l + lx < wsize and world[i + k + kx][j + l + lx].kingdom == world[i][j].kingdom:
                                        totala += world[i + k + kx][j + l + lx].army
                                if totala > world[i+k][j+l].army:
                                    world[i][j].army -= random.randint(0, 10)
                                    world[i+k][j+l].army -= random.randint(0, 10)
                                    if world[i+k][j+l].army <= 0:
                                        world[i+k][j+l].kingdom = world[i][j].kingdom
                                        world[i+k][j+l].army = 10
                                        world[i][j].army //= 2
                                        world[i+k][j+l].lst_upd_tick = upd_tick
                                    elif world[i][j].army <= 0:
                                        world[i][j].kingdom = world[i+k][j+l].kingdom
                                        world[i][j].army = 10
                                        world[i][j].lst_upd_tick = upd_tick
                                        world[i+k][j+l].army //= 2
                if world[i][j].kingdom != "":
                    world[i][j].border = False
                    world[i][j].district_border = False
                    for k, l in adjs:
                        if 0 <= i+k < wsize and 0 <= j+l < wsize:
                            if world[i+k][j+l].kingdom != world[i][j].kingdom:
                                world[i][j].border = True
                                break
                            elif world[i][j].district != world[i+k][j+l].district:
                                world[i][j].district_border = True
                    amp = 0
                    glp = 0
                    if world[i][j].tp == 1:
                        amp += 1
                        glp += 1
                    elif world[i][j].tp == 3:
                        glp += random.randint(1, 2)
                        amp += random.randint(0, 1)
                    elif world[i][j].tp == 5:
                        amp += 1
                        glp += random.randint(1, 2)
                    if upd_tick % ticks_per_day == 0:
                        if upd_tick % (ticks_per_day*10) == 0 and kingdoms[world[i][j].kingdom].gold>=10*amp: # will change to 3*amp after finish gold system
                            kingdoms[world[i][j].kingdom].army += amp
                            kingdoms[world[i][j].kingdom].gold -= 7*amp
                        if upd_tick % (ticks_per_day * 3) == 0:
                            kingdoms[world[i][j].kingdom].gold += glp
                        if kingdoms[world[i][j].kingdom].army >= 1 and world[i][j].army < kingdoms[world[i][j].kingdom].basic_defence and world[i][j].border:
                            kingdoms[world[i][j].kingdom].army -= 1
                            world[i][j].army += 1
                        elif not world[i][j].border and world[i][j].army >= kingdoms[world[i][j].kingdom].basic_defence//2:
                            kingdoms[world[i][j].kingdom].army += world[i][j].army - kingdoms[world[i][j].kingdom].basic_defence//2
                            world[i][j].army = kingdoms[world[i][j].kingdom].basic_defence//2
        while time.time()-ntm < 1/20:
            time.sleep(0.001)
        upd_tick += 1

viewing = (-1, -1)

class game(pyge.Game):
    def setup(self):
        self.tick_rate = 20
        generate_world(self)

    def draw_text(self, text, x, y, size = 24, font = "pingfang", ft=None, color = (255, 255, 255)):
        if ft is None:
            ft = pygame.font.SysFont(font, size)
        txt = ft.render(text, False, color)
        self.sc.blit(txt, (x, y))

    def update_back(self):
        global x, y, blksza, vx, vy, blksz, ticks_per_day, viewing
        if viewing == (-1, -1):
            spd = max(32/min(max(3, int(blksza)), 50), 1)
            if self.keys[pyge.constant.K_UP]:
                y -= spd
            if self.keys[pyge.constant.K_DOWN]:
                y += spd
            if self.keys[pyge.constant.K_LEFT]:
                x -= spd
            if self.keys[pyge.constant.K_RIGHT]:
                x += spd
            if self.keys[pyge.constant.K_q]:
                blksza *= 1.2
            if self.keys[pyge.constant.K_e]:
                blksza /= 1.2
            if self.keys[pyge.constant.K_a]:
                ticks_per_day -= 1
            if self.keys[pyge.constant.K_d]:
                ticks_per_day += 1
            if self.keys[pyge.constant.K_h]:
                x, y = kingdoms["player"].capital
            ticks_per_day = min(max(10, ticks_per_day), 100)

            blksz = min(max(3, int(blksza)), 50)

            x, y = max(min(int(x), wsize-1), 0), max(min(int(y), wsize-1), 0)

            vx = int(x) - WINSZ[0] // blksz // 2
            vy = int(y) - WINSZ[1] // blksz // 2
            if blksz >= 10:
                for i in range(max(vx, 0), min(vx + WINSZ[0] // blksz + 2, wsize)):
                    for j in range(max(vy, 0), min(vy + WINSZ[1] // blksz + 2, wsize)):
                        self.sc.blit(pyge.rect(blksz, blksz, blkattrs[world[i][j].tp].clr), ((i - vx) * blksz, (j - vy) * blksz))
                        if world[i][j].kingdom != "":
                            if map_mode == 0:
                                if kingdoms[world[i][j].kingdom].capital == (i, j):
                                    self.sc.blit(
                                        rect_with_alpha(blksz, blksz, (0, 0, 0), 255),
                                        ((i - vx) * blksz, (j - vy) * blksz))
                                elif world[i][j].border:
                                    self.sc.blit(
                                        rect_with_alpha(blksz, blksz, kingdoms[world[i][j].kingdom].display_clr, 255),
                                        ((i - vx) * blksz, (j - vy) * blksz))
                                elif world[i][j].district_border:
                                    self.sc.blit(
                                        rect_with_alpha(blksz, blksz, kingdoms[world[i][j].kingdom].display_clr, 230),
                                        ((i - vx) * blksz, (j - vy) * blksz))
                                else:
                                    self.sc.blit(
                                        rect_with_alpha(blksz, blksz, kingdoms[world[i][j].kingdom].display_clr, 200),
                                        ((i - vx) * blksz, (j - vy) * blksz))
                                if self.mouse_click[2] and self.mouse_pos[0] // blksz == i - vx and self.mouse_pos[1] // blksz == j - vy:
                                    viewing = (i, j)
                        elif map_mode == 1:
                            if world[i][j].kingdom == "player":
                                self.sc.blit(
                                    rect_with_alpha(blksz, blksz, (0, 0, 255), 200),
                                    ((i - vx) * blksz, (j - vy) * blksz))
                            elif world[i][j].kingdom in kingdoms["player"].ally:
                                self.sc.blit(
                                    rect_with_alpha(blksz, blksz, (0, 255, 0), 200),
                                    ((i - vx) * blksz, (j - vy) * blksz))
                            elif world[i][j].kingdom in kingdoms["player"].enemy:
                                self.sc.blit(
                                    rect_with_alpha(blksz, blksz, (255, 0, 0), 200),
                                    ((i - vx) * blksz, (j - vy) * blksz))
                            else:
                                self.sc.blit(
                                    rect_with_alpha(blksz, blksz, (255, 255, 255), 200),
                                    ((i - vx) * blksz, (j - vy) * blksz))
            else:
                for i in range(max(vx, 0), min(vx + WINSZ[0] // blksz + 2, wsize), 2):
                    for j in range(max(vy, 0), min(vy + WINSZ[1] // blksz + 2, wsize), 2):
                        self.sc.blit(pyge.rect(blksz*2, blksz*2, blkattrs[world[i][j].tp].clr), ((i - vx) * blksz, (j - vy) * blksz))
                        if world[i][j].kingdom != "":
                            if map_mode == 0:
                                self.sc.blit(
                                    rect_with_alpha(blksz * 2, blksz * 2, kingdoms[world[i][j].kingdom].display_clr, 200),
                                    ((i - vx) * blksz, (j - vy) * blksz))
                            elif map_mode == 1:
                                if world[i][j].kingdom == "player":
                                    self.sc.blit(
                                        rect_with_alpha(blksz*2, blksz*2, (0, 0, 255), 200),
                                        ((i - vx) * blksz, (j - vy) * blksz))
                                elif world[i][j].kingdom in kingdoms["player"].ally:
                                    self.sc.blit(
                                        rect_with_alpha(blksz*2, blksz*2, (0, 255, 0), 200),
                                        ((i - vx) * blksz, (j - vy) * blksz))
                                elif world[i][j].kingdom in kingdoms["player"].enemy:
                                    self.sc.blit(
                                        rect_with_alpha(blksz*2, blksz*2, (255, 0, 0), 200),
                                        ((i - vx) * blksz, (j - vy) * blksz))
                                else:
                                    self.sc.blit(
                                        rect_with_alpha(blksz*2, blksz*2, (255, 255, 255), 200),
                                        ((i - vx) * blksz, (j - vy) * blksz))
        elif viewing[0] != -1:
            if self.keys[pyge.constant.K_ESCAPE]:
                viewing = (-1, -1)
            else:
                self.sc.fill((200, 200, 200))
                self.draw_text(f"{viewing[0]} {viewing[1]}", wsize // 2, 10, size=30, color=(0, 0, 0))
                self.draw_text(f"type: {world[viewing[0]][viewing[1]].tp}", 100, 40, size=20, color=(0, 0, 0))
                self.draw_text(f"district: {world[viewing[0]][viewing[1]].district}, {world[viewing[0]][viewing[1]].kingdom}", 100, 60, size=20, color=(0, 0, 0))
                self.draw_text(f"army size: {world[viewing[0]][viewing[1]].army}", 100, 80, size=20, color=(0, 0, 0))
                if self.keys[pyge.constant.K_k]:
                    viewing = (-1, world[viewing[0]][viewing[1]].kingdom)
        else:
            if self.keys[pyge.constant.K_ESCAPE]:
                viewing = (-1, -1)
            else:
                self.sc.fill((200, 200, 200))
                self.draw_text(f"{viewing[1]}", wsize // 2, 10, size=30, color=(0, 0, 0))
                self.draw_text(f"army: {kingdoms[viewing[1]].army}", 100, 40, size=20, color=(0, 0, 0))
                self.draw_text(f"allies: {kingdoms[viewing[1]].ally}", 100, 60, size=20, color=(0, 0, 0))
                self.draw_text(f"enemies: {kingdoms[viewing[1]].enemy}", 100, 80, size=20, color=(0, 0, 0))
                self.draw_text(f"gold: {kingdoms[viewing[1]].gold}", 100, 100, size=20, color=(0, 0, 0))
                self.draw_text(f"size: {kingdoms[viewing[1]].area}", 100, 120, size=20, color=(0, 0, 0))


        for i in kingdoms.keys():
            kingdoms[i].update()

        self.draw_text("fps: "+str(int(self.fps)), 0, 0)
        self.draw_text("Day "+str(int(days)), 0, 30)
        self.draw_text("tpd: "+str(int(ticks_per_day)), 0, 60)


gm = game()
threading.Thread(target=update_each_cell).start()
gm.run()