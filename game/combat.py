"""Combate: rondas, temporizador, colisiones, daño, proyectiles, ultimates y HUD."""
import math
import random
import pygame
import config as C
from game import assets, ui
from game.collisions import circle_rect, hit_point
from game.camera import Camera
from game.stage import Stage
from game.particles import FXManager, SpriteFX, Ring, SpeedLines, FloatText
from game.player import Fighter, FREE
from game.characters_data import PROJECTILES, ULTIMATE_COST
from game import encounters


# ====================================================================== proyectiles
class Projectile:
    def __init__(self, match, owner, kind):
        self.m = match
        self.owner = owner
        self.kind = kind
        d = self.d = PROJECTILES[kind]
        jx, jy = owner.spr.joint(owner.anim, owner.frame, d['joint'])
        self.x, self.y = owner.world_point(jx + d['off'][0], jy + d['off'][1])
        self.facing = owner.facing
        self.vx = d['speed'] * owner.facing
        self.t = 0
        self.alive = True
        self.returning = False
        self.frames = assets.effects().frames[d['fx']]
        self.dur = assets.effects().meta[d['fx']]['dur']
        self.length = 0
        self.hit_tick = 0
        self.hits = 0

    def update(self):
        d = self.d
        self.t += 1
        if d.get('beam'):
            o = self.owner
            if o.move is None or o.state != 'attack':
                self.finish_beam(); return
            jx, jy = o.spr.joint(o.anim, o.frame, d['joint'])
            self.x, self.y = o.world_point(jx + d['off'][0], jy + d['off'][1])
            self.facing = o.facing
            self.length = min(1100, self.length + 90)
            if self.t >= d['life']:
                self.finish_beam()
            return
        if d.get('boomerang') and self.t > d['life'] // 2:
            self.returning = True
            dx = self.owner.x - self.x
            dy = (self.owner.y - 200) - self.y
            dist = math.hypot(dx, dy) + 1e-6
            self.vx += dx / dist * 1.4
            self.vx = max(-14, min(14, self.vx))
            self.y += dy / dist * 4
            if dist < 60:
                self.alive = False
        self.x += self.vx
        if self.t > d['life'] * (2 if d.get('boomerang') else 1) or not (-200 < self.x < self.m.stage.w + 200):
            self.alive = False

    def finish_beam(self):
        if not self.alive:
            return
        self.alive = False
        opp = self.owner.opponent()
        fin = self.d.get('final')
        if fin and opp.state == 'locked' and opp.locked_by is self.owner:
            hit = dict(dmg=fin['dmg'], stun=30, bstun=10, kb=fin['kb'], kd=True, launch=fin['launch'],
                       h='mid', sfx='explosion', fx='chispa_fuerte', stop=16, chip=0)
            opp.locked_by = None
            self.m.apply_hit(self.owner, opp, hit, opp.x, opp.y - 200, force=True)
            self.m.fx.add(SpriteFX('explosion', opp.x, opp.y - 200, scale=1.6))

    def hit_rect(self):
        """Caja de golpe del proyectil (para el modo debug)."""
        d = self.d
        if d.get('beam'):
            x0 = self.x if self.facing > 0 else self.x - self.length
            return pygame.Rect(x0, self.y - 70, self.length, 140)
        r = d['r']
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def rect_hit(self, opp):
        d = self.d
        hb = opp.hurtbox()
        if d.get('beam'):
            x0 = self.x if self.facing > 0 else self.x - self.length
            beam = pygame.Rect(x0, self.y - 70, self.length, 140)
            return beam.colliderect(hb)
        return circle_rect(self.x, self.y, d['r'], hb)

    def draw(self, surf, cam):
        d = self.d
        if d.get('beam'):
            fr = self.frames[(self.t // self.dur) % len(self.frames)]
            w = fr.get_width()
            n = int(self.length // w) + 1
            for i in range(n):
                img = fr if self.facing > 0 else pygame.transform.flip(fr, True, False)
                bx = self.x + i * w * self.facing - (0 if self.facing > 0 else w)
                sx, sy = cam.to_screen(bx, self.y - fr.get_height() / 2)
                surf.blit(img, (sx, sy))
            sx, sy = cam.to_screen(self.x, self.y)
            pygame.draw.circle(surf, (255, 255, 255), (int(sx), int(sy)), 30 + (self.t % 6) * 3)
            return
        fr = self.frames[(self.t // self.dur) % len(self.frames)]
        if self.facing < 0:
            fr = pygame.transform.flip(fr, True, False)
        sx, sy = cam.to_screen(self.x, self.y)
        surf.blit(fr, (sx - fr.get_width() // 2, sy - fr.get_height() // 2))


# ====================================================================== combate
class Match:
    def __init__(self, game, c1, c2, mode='versus', ai1=None, ai2=None, difficulty=1):
        self.game = game
        self.audio = game.audio
        self.settings = game.settings
        self.mode = mode
        self.training = mode == 'training'
        self.stage = Stage(getattr(game, 'stage_id', 'aula'))
        self.camera = Camera(self.stage.w, self.stage.h)
        self.fx = FXManager()
        self.p1 = Fighter(c1, 1, self)
        self.p2 = Fighter(c2, 2, self)
        self.p1.meter = self.p2.meter = 0
        self.ai = {1: ai1, 2: ai2}
        self.projectiles = []
        self.round = 1
        self.rounds_to_win = self.settings['rounds_to_win'] if not self.training else 99
        self.round_time = self.settings['round_time'] if not self.training else 0
        self.tick = 0
        self.state_t = 0
        self.state = 'intro'
        self.controls_enabled = False
        self.freeze = 0
        self.freeze_owner = None
        self.flash_color = None
        self.flash_t = 0
        self.banner = None
        self.cutin = None
        self.combo_show = {1: (0, 0, 0), 2: (0, 0, 0)}  # (hits, daño, ticks)
        self.result = None
        self.infinite_meter = self.training
        self.show_hitboxes = getattr(game, 'debug', False)     # modo debug (F9), se mantiene entre peleas
        self.slowmo = 0
        self.winner = None
        self.round_winner = None
        self.timer = self.round_time
        self.timer_ticks = 0
        self.perfect = False
        self.dummy_mode = 0
        self.last_combo_dmg = 0
        self.start_round()

    # ------------------------------------------------------------------ rondas
    def start_round(self):
        for f in (self.p1, self.p2):
            meter = f.meter
            f.reset_round()
            f.meter = meter
        self.projectiles = []
        self.timer = self.round_time
        self.timer_ticks = 0
        self.state = 'intro'
        self.state_t = 0
        self.controls_enabled = False
        self.round_winner = None
        self.encounter = None
        if self.round == 1 and not self.training:
            for f in (self.p1, self.p2):
                f.state = 'intro'
                f.set_anim('presentacion')
            ev = encounters.pick(self.p1.name, self.p2.name)
            if ev:
                # escena especial antes de pelear (pareja, amigos, rivales, bronca contra Parada)
                self.encounter = encounters.Encounter(self, *ev)
                self.state = 'encounter'
        self.camera.zoom_target = 1.0
        self.camera.focus = None

    def set_banner(self, txt, color=C.YELLOW, ticks=80, size=64, sub=None):
        self.banner = dict(txt=txt, color=color, t=0, ticks=ticks, size=size, sub=sub)

    def super_flash(self, f, name):
        self.freeze = 62
        self.freeze_owner = f
        self.cutin = dict(f=f, name=name, t=0)
        self.audio.play('ultimate_activar')
        self.camera.focus = f
        self.camera.zoom_target = 1.12
        self.fx.add(SpeedLines(f.x, f.y - 190, f.color, 50))
        self.fx.add(Ring(f.x, f.y - 190, f.color, 20, 420, 30, 12))
        self.fx.burst(f.x, f.y - 200, f.color, 40, 14, 8, 0.1)

    def screen_flash(self, color, ticks):
        self.flash_color = color
        self.flash_t = ticks
        self.flash_max = ticks

    # ------------------------------------------------------------------ eventos
    def spawn_projectile(self, owner, kind):
        p = Projectile(self, owner, kind)
        owner.projectile = p
        self.projectiles.append(p)
        self.fx.add(Ring(p.x, p.y, owner.color, 10, 80, 12, 6))

    def spawn_fx_at_joint(self, f, name, joint):
        jx, jy = f.spr.joint(f.anim, f.frame, joint)
        x, y = f.world_point(jx, jy)
        self.fx.add(SpriteFX(name, x, y, f.facing, follow=f, offset=((x - f.x) * f.facing, y - f.y),
                             loops=3, scale=1.3), front=True)

    def strike(self, att, fx, dmg, final):
        """Golpe a distancia sobre la posición del rival (rayo, pantallazo...)."""
        opp = att.opponent()
        if fx:
            self.fx.add(SpriteFX(fx, opp.x, self.stage.ground_y - 262, 1, loops=2))
            self.fx.add(Ring(opp.x, self.stage.ground_y - 20, att.color, 10, 220, 16, 8))
            self.fx.burst(opp.x, opp.y - 120, (255, 255, 200), 18, 12, 6, 0.3)
        if opp.invuln > 0 or opp.ko or opp.state in ('lying', 'getup'):
            return
        hit = dict(dmg=dmg, stun=34, bstun=16, kb=14 if final else 2, kd=final, launch=-16 if final else 0,
                   h='mid', sfx='golpe_fuerte', fx='chispa_fuerte', stop=14 if final else 6, chip=0.2)
        self.apply_hit(att, opp, hit, opp.x, opp.y - 180)

    def quake(self, att, dmg, rng, final=True):
        opp = att.opponent()
        for k, d in enumerate((120, 330, 540, 750)):
            for s in (-1, 1):
                self.fx.add(SpriteFX('onda_choque', att.x + s * d, self.stage.ground_y - 70, s, loops=1,
                                     scale=1.2), front=False)
        self.fx.add(Ring(att.x, self.stage.ground_y - 10, (255, 150, 200), 30, 700, 30, 14))
        self.fx.burst(att.x, self.stage.ground_y - 20, (150, 110, 80), 50, 18, 9, 0.7)
        if opp.on_ground and abs(opp.x - att.x) < rng and opp.invuln <= 0 and opp.state not in ('lying', 'getup'):
            hit = dict(dmg=dmg, stun=34, bstun=20, kb=12 if final else 0, kd=final, launch=-22 if final else 0,
                       h='mid', sfx='golpe_fuerte', fx='chispa_fuerte', stop=14 if final else 8, chip=0)
            self.apply_hit(att, opp, hit, opp.x, opp.y - 60, force=True)

    def blast(self, att, dmg, radius):
        opp = att.opponent()
        self.fx.add(SpriteFX('explosion', att.x + att.facing * 40, att.y - 80, scale=2.0))
        self.fx.add(Ring(att.x, att.y - 40, (255, 220, 120), 20, radius * 2.2, 22, 10))
        hb = opp.hurtbox()
        if circle_rect(att.x + att.facing * 40, att.y - 60, radius, hb) and opp.invuln <= 0 and \
                opp.state not in ('lying', 'getup'):
            hit = dict(dmg=dmg, stun=30, bstun=20, kb=14, kd=True, launch=-18, h='mid', sfx='golpe_fuerte',
                       fx='chispa_fuerte', stop=14, chip=0.15)
            self.apply_hit(att, opp, hit, hb.centerx, hb.centery)

    def release_lock(self, att):
        opp = att.opponent()
        if opp.state == 'locked' and opp.locked_by is att:
            opp.locked_by = None
            opp.knockdown(-opp.facing_to(att) * 8, -10)

    # ------------------------------------------------------------------ golpes
    def wants_block(self, f):
        inp = self.inputs.get(f.side)
        if f.state in ('block', 'cblock', 'blockstun'):
            return True
        if f.state in FREE and inp is not None and inp.held['bloquear']:
            return True
        return False

    def apply_hit(self, att, dfn, hit, px, py, force=False, proj=False):
        crouch_block = dfn.state == 'cblock' or (self.inputs.get(dfn.side) and
                                                  self.inputs[dfn.side].held['abajo'] and dfn.state in FREE)
        blocked = False
        if not force and dfn.state != 'locked' and self.wants_block(dfn) and dfn.on_ground:
            h = hit.get('h', 'mid')
            if h == 'low' and not crouch_block:
                blocked = False
            elif h == 'high' and crouch_block:
                blocked = False
            else:
                blocked = True
        lock = (att.move is not None and att.move.get('lock') and not blocked) or \
               (proj and PROJECTILES.get(getattr(proj, 'kind', ''), {}).get('lock') and not blocked)
        base = hit['dmg']
        dmg = base * att.dmg_mult * dfn.def_mult
        juggle = dfn.state in ('knock',)
        if dfn.state in ('hitstun', 'locked', 'knock'):
            dfn.combo += 1
        else:
            dfn.combo = 1
            dfn.combo_dmg = 0
        if dfn.combo > 3 and not lock:
            dmg *= max(0.45, 0.88 ** (dfn.combo - 3))
        if juggle:
            dmg *= 0.7
        dmg = int(dmg)
        if blocked:
            dfn.take_hit(hit, att, dmg, True)
            stop = max(3, hit.get('stop', 6) - 2)
            att.hitstop = dfn.hitstop = stop
            self.audio.play('bloqueo')
            self.fx.add(SpriteFX('chispa_bloqueo', px, py, att.facing))
            self.fx.sparks(px, py, att.facing, (150, 200, 255), 6)
            att.meter = min(ULTIMATE_COST, att.meter + 2)
            dfn.combo = 0
            # empuje al atacante si el defensor está contra la pared
            if dfn.x <= self.stage.left + 5 or dfn.x >= self.stage.right - 5:
                att.x -= att.facing * 18
            return
        dfn.combo_dmg += dmg
        dfn.take_hit(hit, att, dmg, False, locked=bool(lock))
        if att.move is not None and not att.move.get('ult') and not proj and att.on_ground:
            att.vx *= 0.25
        stop = hit.get('stop', 6)
        att.hitstop = dfn.hitstop = stop
        if att.move is None or not att.move.get('ult'):
            att.meter = min(ULTIMATE_COST, att.meter + 7)
        self.audio.play(hit.get('sfx', 'golpe_debil'))
        big = hit.get('fx') == 'chispa_fuerte'
        self.fx.add(SpriteFX(hit.get('fx', 'chispa_golpe'), px, py, att.facing, scale=1.3 if big else 1.0))
        self.fx.sparks(px, py, att.facing, att.color, 14 if big else 8)
        self.fx.burst(px, py, (255, 255, 255), 6 if big else 3, 7, 5, 0.3)
        if big:
            self.camera.shake(9, 12)
            self.fx.add(Ring(px, py, (255, 255, 255), 10, 120, 12, 6))
        else:
            self.camera.shake(3, 5)
        if dfn.combo >= 2:
            self.combo_show[att.side] = (dfn.combo, dfn.combo_dmg, 110)
            if dfn.combo in (3, 5, 8, 12):
                self.audio.play('combo')
        if self.training:
            self.last_combo_dmg = dfn.combo_dmg
        if dfn.ko:
            self.on_ko(att, dfn)

    def resolve_hits(self):
        for att, dfn in ((self.p1, self.p2), (self.p2, self.p1)):
            if att.hitstop > 0:
                continue
            hits = att.active_hits()
            if not hits:
                continue
            if dfn.invuln > 0 or dfn.state in ('lying', 'getup') or dfn.ko:
                continue
            hb = dfn.hurtbox()
            for h, x, y, r in hits:
                if circle_rect(x, y, r, hb):
                    att.hits_done.add(h['id'])
                    px, py = hit_point(x, y, hb)
                    self.apply_hit(att, dfn, h, px, py)
                    break
        # proyectiles
        for p in self.projectiles:
            if not p.alive:
                continue
            opp = p.owner.opponent()
            if p.d.get('beam'):
                p.hit_tick -= 1
                if p.hit_tick <= 0 and opp.invuln <= 0 and not opp.ko and opp.state not in ('lying', 'getup') \
                        and p.rect_hit(opp):
                    p.hit_tick = p.d['interval']
                    hit = dict(dmg=p.d['dmg'], stun=p.d['stun'], bstun=8, kb=p.d['kb'], h='mid',
                               sfx=p.d['sfx'], fx='chispa_golpe', stop=2, chip=p.d['chip'])
                    hb = opp.hurtbox()
                    self.apply_hit(p.owner, opp, hit, hb.centerx, p.y, proj=p)
                    if opp.state == 'locked':
                        opp.locked_by = p.owner
                continue
            if opp.invuln <= 0 and not opp.ko and opp.state not in ('lying', 'getup') and p.rect_hit(opp):
                p.alive = False
                hit = dict(dmg=p.d['dmg'], stun=p.d['stun'], bstun=14, kb=p.d['kb'], kd=p.d.get('kd', False),
                           h='mid', sfx=p.d['sfx'], fx='chispa_fuerte', stop=8, chip=p.d['chip'])
                self.apply_hit(p.owner, opp, hit, p.x, p.y, proj=p)
        # choque de proyectiles
        a = [p for p in self.projectiles if p.alive and not p.d.get('beam')]
        for i in range(len(a)):
            for j in range(i + 1, len(a)):
                if a[i].owner is not a[j].owner and abs(a[i].x - a[j].x) < 70 and abs(a[i].y - a[j].y) < 120:
                    a[i].alive = a[j].alive = False
                    mx, my = (a[i].x + a[j].x) / 2, (a[i].y + a[j].y) / 2
                    self.fx.add(SpriteFX('explosion', mx, my))
                    self.audio.play('explosion', 0.6)

    def on_ko(self, att, dfn):
        if self.state != 'fight':
            return
        self.state = 'ko'
        self.state_t = 0
        self.slowmo = 70
        self.controls_enabled = False
        self.round_winner = att
        self.audio.play('ko_impacto')
        self.audio.announce('loc_ko')
        self.screen_flash((255, 255, 255), 10)
        self.camera.shake(18, 30)
        self.set_banner('K.O.', C.RED, 140, 110)
        self.perfect = att.health >= att.max_health

    def push_apart(self):
        a, b = self.p1, self.p2
        if a.passthrough or b.passthrough:
            return
        if a.move and a.move.get('passthrough') and a.move['passthrough'][0] <= a.mframe <= a.move['passthrough'][1]:
            return
        if b.move and b.move.get('passthrough') and b.move['passthrough'][0] <= b.mframe <= b.move['passthrough'][1]:
            return
        if a.state == 'lying' or b.state == 'lying':
            return
        # durante un agarre de ultimate la posición la maneja el agarre
        if a.state == 'locked' or b.state == 'locked':
            return
        # si uno está muy por encima del otro (saltándolo), no se empujan
        if abs(a.y - b.y) > 260:
            return
        w = a.push_w + b.push_w
        dx = b.x - a.x
        if abs(dx) < w:
            if dx != 0:
                s = 1 if dx > 0 else -1
            else:
                s = a.facing
            st = self.stage
            # quien cae encima de un rival arrinconado se resbala hacia el lado libre
            if not a.on_ground and b.on_ground:
                s = -1 if b.x <= st.left + 5 else (1 if b.x >= st.right - 5 else s)
            elif not b.on_ground and a.on_ground:
                s = 1 if a.x <= st.left + 5 else (-1 if a.x >= st.right - 5 else s)
            push = (w - abs(dx)) / 2
            a.x -= s * push
            b.x += s * push
            for f, other in ((a, b), (b, a)):
                if f.x < st.left:
                    other.x += st.left - f.x
                    f.x = st.left
                elif f.x > st.right:
                    other.x -= f.x - st.right
                    f.x = st.right
        # distancia máxima en pantalla
        maxd = C.WIDTH - 320
        if abs(b.x - a.x) > maxd:
            mid = (a.x + b.x) / 2
            s = 1 if b.x > a.x else -1
            for f, sgn in ((a, -s), (b, s)):
                if (f.x - mid) * sgn > maxd / 2:
                    f.x = mid + sgn * maxd / 2

    # ------------------------------------------------------------------ actualización
    def update(self, inputs):
        """inputs: {1: InputState, 2: InputState}"""
        self.inputs = inputs
        self.tick += 1
        self.stage.update()
        if self.banner:
            self.banner['t'] += 1
            if self.banner['t'] > self.banner['ticks']:
                self.banner = None
        if self.flash_t > 0:
            self.flash_t -= 1
        for s in (1, 2):
            h, d, t = self.combo_show[s]
            if t > 0:
                self.combo_show[s] = (h, d, t - 1)
        # ---- congelamiento del super flash
        if self.freeze > 0:
            self.freeze -= 1
            self.cutin['t'] += 1
            self.stage.dim = min(1.0, self.stage.dim + 0.1)
            self.fx.update()
            self.camera.update(self.p1, self.p2)
            if self.freeze == 0:
                self.camera.zoom_target = 1.0
                self.camera.focus = None
                self.cutin = None
            return
        ult_active = any(f.move is not None and f.move.get('ult') for f in (self.p1, self.p2))
        target_dim = 0.55 if ult_active else 0.0
        self.stage.dim += (target_dim - self.stage.dim) * 0.1
        # ---- cámara lenta del KO
        if self.slowmo > 0:
            self.slowmo -= 1
            if self.slowmo % 3 != 0:
                self.fx.update()
                self.camera.update(self.p1, self.p2)
                return
        self.state_t += 1
        self.round_flow()
        if self.training:
            self.training_update()
        for f in (self.p1, self.p2):
            inp = inputs.get(f.side)
            f.update(inp)
        self.push_apart()
        for p in self.projectiles:
            if p.alive:
                p.update()
        self.projectiles = [p for p in self.projectiles if p.alive]
        for f in (self.p1, self.p2):
            if f.projectile is not None and not f.projectile.alive:
                f.projectile = None
        if self.state in ('fight', 'ko'):
            self.resolve_hits()
        for f in (self.p1, self.p2):
            f.shown_health += (f.health - f.shown_health) * 0.06 if f.state not in ('hitstun', 'locked') else 0
        self.fx.update()
        self.camera.update(self.p1, self.p2)

    def round_flow(self):
        t = self.state_t
        if self.state == 'encounter':
            if t == 1:
                self.audio.play('publico', 0.6)
            self.encounter.update()
            if self.encounter.done:
                self.state = 'intro'
                self.state_t = 55          # sigue directo con "RONDA 1"
                if self.encounter.skipped:
                    self.banner = None
            return
        if self.state == 'intro':
            if self.training:
                if t == 2:
                    self.set_banner('ENTRENAMIENTO', C.CYAN, 70, 44)
                if t == 40:
                    self.state = 'fight'; self.controls_enabled = True
                return
            if t == 1 and self.round == 1:
                self.audio.play('publico', 0.6)
            start = 70 if self.round == 1 else 10
            if t == start:
                last = self.p1.wins == self.rounds_to_win - 1 and self.p2.wins == self.rounds_to_win - 1
                label = 'RONDA FINAL' if last else f'RONDA {self.round}'
                self.set_banner(label, C.YELLOW, 70, 60)
                self.audio.play('gong')
                self.audio.announce('loc_ronda_final' if last else ('loc_ronda_1' if self.round == 1 else 'loc_ronda_2'))
            if t == start + 75:
                self.set_banner('¡PELEEN!', C.RED, 50, 84)
                self.audio.announce('loc_pelea')
                for f in (self.p1, self.p2):
                    if f.state == 'intro':
                        f.state = 'idle'; f.set_anim('idle')
            if t == start + 85:
                self.state = 'fight'
                self.controls_enabled = True
                self.state_t = 0
        elif self.state == 'fight':
            if self.round_time > 0:
                self.timer_ticks += 1
                if self.timer_ticks >= 60:
                    self.timer_ticks = 0
                    self.timer -= 1
                    if 0 < self.timer <= 10:
                        self.audio.play('tic', 0.6)
                    if self.timer <= 0:
                        self.time_over()
        elif self.state == 'ko':
            loser = self.p1 if self.round_winner is self.p2 else self.p2
            if t > 100 and loser.state == 'lying' and all(f.on_ground for f in (self.p1, self.p2)) \
                    and self.round_winner.state in FREE + ('land',):
                self.finish_round(self.round_winner)
        elif self.state == 'timeover':
            if t > 110:
                a, b = self.p1, self.p2
                ra, rb = a.health / a.max_health, b.health / b.max_health
                if abs(ra - rb) < 1e-3:
                    self.finish_round(None)
                else:
                    self.finish_round(a if ra > rb else b)
        elif self.state == 'round_end':
            if t == 40 and self.round_winner is not None:
                w = self.round_winner
                if self.perfect:
                    self.set_banner('¡PERFECTO!', C.CYAN, 100, 64)
                    self.audio.announce('loc_perfecto')
                else:
                    self.set_banner(f'{w.data["display"]} GANA', w.color, 100, 52)
                    self.audio.announce(f'loc_{w.name}_gana')
            if t == 40 and self.round_winner is None:
                self.set_banner('EMPATE', C.WHITE, 100, 60)
                self.audio.announce('loc_empate')
            if t > 190:
                if self.p1.wins >= self.rounds_to_win or self.p2.wins >= self.rounds_to_win:
                    self.winner = self.p1 if self.p1.wins > self.p2.wins else self.p2
                    self.state = 'match_over'
                    self.state_t = 0
                else:
                    self.round += 1
                    self.start_round()
        elif self.state == 'match_over':
            pass

    def time_over(self):
        self.state = 'timeover'
        self.state_t = 0
        self.controls_enabled = False
        self.set_banner('¡TIEMPO!', C.ORANGE, 100, 72)
        self.audio.announce('loc_tiempo')
        self.perfect = False

    def finish_round(self, winner):
        self.state = 'round_end'
        self.state_t = 0
        self.round_winner = winner
        if winner is not None:
            winner.wins += 1
            winner.state = 'victory'
            winner.set_anim('victoria')
            winner.vx = 0
            self.audio.voice(winner.name, 'victoria')
            loser = self.p2 if winner is self.p1 else self.p1
            if not loser.ko:
                loser.state = 'defeat'; loser.set_anim('derrota'); loser.vx = 0
        else:
            for f in (self.p1, self.p2):
                f.state = 'defeat'; f.set_anim('derrota')

    # ------------------------------------------------------------------ entrenamiento
    def training_update(self):
        for f in (self.p1, self.p2):
            if f.state in FREE and f.health < f.max_health and f.combo == 0:
                f.health = min(f.max_health, f.health + 12)
            f.meter = ULTIMATE_COST
            if f.health <= 0:
                f.health = 1
            f.ko = False

    # ------------------------------------------------------------------ dibujo
    def draw(self, surf):
        cam = self.camera
        z = cam.zoom
        world = self.game.world_surf if abs(z - 1.0) > 0.01 else surf
        self.stage.draw_back(world, cam)
        self.fx.draw_back(world, cam)
        for f in (self.p1, self.p2):
            self.stage.draw_shadow(world, cam, f.x, f.y, 1.2 if f.name == 'pantoja' else 1.0)
        order = [self.p1, self.p2]
        if self.p2.state == 'attack' and self.p1.state != 'attack':
            order = [self.p1, self.p2]
        elif self.p1.state == 'attack':
            order = [self.p2, self.p1]
        for f in order:
            f.draw(world, cam)
            if self.show_hitboxes:
                f.draw_debug(world, cam)
        for p in self.projectiles:
            p.draw(world, cam)
            if self.show_hitboxes:
                r = p.hit_rect() if hasattr(p, 'hit_rect') else None
                if r is not None:
                    x, y = cam.to_screen(r.x, r.y)
                    pygame.draw.rect(world, (255, 80, 0), (x, y, r.w, r.h), 2)
        self.fx.draw_front(world, cam)
        self.stage.draw_front(world, cam)
        if self.show_hitboxes:
            self.draw_debug_overlay(world, cam)
        if world is not surf:
            fx_ = cam.focus.x if cam.focus else (self.p1.x + self.p2.x) / 2
            sx, sy = cam.to_screen(fx_, self.stage.ground_y - 200)
            w, h = int(C.WIDTH / z), int(C.HEIGHT / z)
            x0 = max(0, min(C.WIDTH - w, int(sx - w / 2)))
            y0 = max(0, min(C.HEIGHT - h, int(sy - h / 2)))
            sub = world.subsurface((x0, y0, w, h))
            pygame.transform.scale(sub, (C.WIDTH, C.HEIGHT), surf)
        if self.flash_t > 0:
            s = pygame.Surface((C.WIDTH, C.HEIGHT))
            s.fill(self.flash_color)
            s.set_alpha(int(220 * self.flash_t / self.flash_max))
            surf.blit(s, (0, 0))
        self.draw_hud(surf)
        if self.cutin:
            self.draw_cutin(surf)
        if self.banner and not self.cutin:
            self.draw_banner(surf)

    def draw_debug_overlay(self, surf, cam):
        """Línea de suelo, límites del escenario y referencias del modo debug."""
        _, gy = cam.to_screen(0, self.stage.ground_y)
        pygame.draw.line(surf, (255, 0, 255), (0, gy), (C.WIDTH, gy), 1)
        for xw in (self.stage.left, self.stage.right):
            x, _ = cam.to_screen(xw, 0)
            pygame.draw.line(surf, (255, 120, 0), (x, 0), (x, C.HEIGHT), 1)
        leg = ui.text_outline('DEBUG (F9)  verde=hurtbox  rojo=hitbox  amarillo=empuje  azul=sprite  '
                              'magenta=suelo/pies  naranja=límites/proyectil', 9, (255, 255, 255))
        surf.blit(leg, (C.WIDTH // 2 - leg.get_width() // 2, 118))

    def draw_cutin(self, surf):
        c = self.cutin
        f = c['f']
        t = c['t']
        k = min(1.0, t / 10)
        out = max(0.0, (t - 50) / 12)
        y = 250
        h = 190
        band = pygame.Surface((C.WIDTH, h), pygame.SRCALPHA)
        band.fill((0, 0, 0, 200))
        for i in range(0, C.WIDTH, 40):
            xx = (i + t * 18) % (C.WIDTH + 80) - 40
            pygame.draw.line(band, f.color + (120,), (xx, 0), (xx - 60, h), 6)
        pygame.draw.rect(band, f.color, (0, 0, C.WIDTH, 6))
        pygame.draw.rect(band, f.color, (0, h - 6, C.WIDTH, 6))
        bw = int(C.WIDTH * k * (1 - out))
        if bw <= 0:
            return
        bx = 0 if f.side == 1 else C.WIDTH - bw
        surf.blit(band, (bx, y), (bx, 0, bw, h))
        por = f.spr.portrait_at(220)
        if f.side == 2:
            por = pygame.transform.flip(por, True, False)
        px = (-240 + 300 * k) if f.side == 1 else (C.WIDTH + 20 - 300 * k - 0)
        px -= out * 400 * (1 if f.side == 1 else -1)
        surf.blit(por, (px if f.side == 1 else px - 0, y - 20))
        name = ui.text_gradient(c['name'], 40, (255, 255, 255), f.color, extrude=4)
        tx = C.WIDTH / 2 + (1 - k) * 600 * (1 if f.side == 1 else -1)
        ui.blit_center(surf, name, tx + 80 * (1 if f.side == 1 else -1), y + h / 2 + 10)
        lab = ui.text_outline('ULTIMATE', 20, C.YELLOW)
        ui.blit_center(surf, lab, tx + 80 * (1 if f.side == 1 else -1), y + 40)

    def draw_banner(self, surf):
        b = self.banner
        t = b['t']
        k = min(1.0, t / 8)
        img = ui.text_gradient(b['txt'], b['size'], (255, 255, 255), b['color'], extrude=6)
        sc = 0.5 + 0.5 * k          # crece hasta su tamaño final: nunca invade el HUD ni a los luchadores
        w, h = int(img.get_width() * sc), int(img.get_height() * sc)
        im = pygame.transform.scale(img, (w, h))
        if t > b['ticks'] - 10:
            im.set_alpha(int(255 * (b['ticks'] - t) / 10))
        # los carteles van en la franja entre el HUD y las cabezas de los luchadores
        ui.blit_center(surf, im, C.WIDTH / 2, 122 + img.get_height() / 2)

    def draw_hud(self, surf):
        t = self.tick
        bw, bh, y = 460, 30, 34          # las barras terminan antes del reloj (no se tocan)
        for f in (self.p1, self.p2):
            left = f.side == 1
            x = 120 if left else C.WIDTH - 120 - bw
            # retrato
            por = f.spr.portrait_at(88)
            if not left:
                por = pygame.transform.flip(por, True, False)
            px = 18 if left else C.WIDTH - 106
            pygame.draw.rect(surf, (0, 0, 0), (px - 4, 14, 96, 96))
            pygame.draw.rect(surf, f.color, (px - 2, 16, 92, 92))
            pygame.draw.rect(surf, (20, 20, 40), (px, 18, 88, 88))
            surf.blit(por, (px, 18))
            # barra de vida
            pygame.draw.rect(surf, (0, 0, 0), (x - 4, y - 4, bw + 8, bh + 8))
            pygame.draw.rect(surf, (255, 255, 255), (x - 2, y - 2, bw + 4, bh + 4), 2)
            pygame.draw.rect(surf, (90, 0, 10), (x, y, bw, bh))
            ks = max(0.0, f.shown_health / f.max_health)
            kh = max(0.0, f.health / f.max_health)
            ws, wh = int(bw * ks), int(bw * kh)
            if left:
                pygame.draw.rect(surf, (255, 40, 40), (x + bw - ws, y, ws, bh))
                col = (255, 214, 10) if kh > 0.25 or (t // 6) % 2 else (255, 120, 0)
                pygame.draw.rect(surf, col, (x + bw - wh, y, wh, bh))
                pygame.draw.rect(surf, (255, 250, 180), (x + bw - wh, y + 3, wh, 5))
            else:
                pygame.draw.rect(surf, (255, 40, 40), (x, y, ws, bh))
                col = (255, 214, 10) if kh > 0.25 or (t // 6) % 2 else (255, 120, 0)
                pygame.draw.rect(surf, col, (x, y, wh, bh))
                pygame.draw.rect(surf, (255, 250, 180), (x, y + 3, wh, 5))
            # nombre
            nm = ui.text_outline(f.data['display'], 18, C.WHITE)
            surf.blit(nm, (x if left else x + bw - nm.get_width(), y + bh + 10))
            # rondas ganadas
            for i in range(self.rounds_to_win if not self.training else 0):
                cx = (x + bw - 20 - i * 34) if left else (x + 20 + i * 34)
                won = i < f.wins
                pygame.draw.circle(surf, (0, 0, 0), (cx, y + bh + 22), 14)
                pygame.draw.circle(surf, (255, 200, 0) if won else (60, 60, 80), (cx, y + bh + 22), 12)
                if won:
                    ui.blit_center(surf, ui.text('10', 8, (120, 40, 0)), cx + 1, y + bh + 23)
            # barra de ultimate
            mw, mh = 330, 20
            mx = 30 if left else C.WIDTH - 30 - mw
            my = C.HEIGHT - 52
            pygame.draw.rect(surf, (0, 0, 0), (mx - 3, my - 3, mw + 6, mh + 6))
            pygame.draw.rect(surf, (30, 30, 70), (mx, my, mw, mh))
            km = f.meter / ULTIMATE_COST
            full = km >= 1
            mc = f.color if not full else ((255, 255, 255) if (t // 4) % 2 else f.color)
            if left:
                pygame.draw.rect(surf, mc, (mx, my, int(mw * km), mh))
            else:
                pygame.draw.rect(surf, mc, (mx + mw - int(mw * km), my, int(mw * km), mh))
            for i in range(1, 4):
                pygame.draw.line(surf, (0, 0, 0), (mx + mw * i // 4, my), (mx + mw * i // 4, my + mh), 2)
            lab = ui.text_outline('¡ULTIMATE LISTA!' if full else 'ULTIMATE', 14,
                                  C.YELLOW if full else (200, 200, 220))
            surf.blit(lab, (mx if left else mx + mw - lab.get_width(), my - 24))
            # combo
            hits, dmg, ct = self.combo_show[f.side]
            if ct > 0 and hits >= 2:
                pop = max(0.0, (ct - 100) / 10)
                ctext = ui.text_gradient(f'{hits} GOLPES', 34, (255, 255, 255), f.color, extrude=3)
                if pop > 0:
                    sc = 1 + 0.35 * pop
                    ctext = pygame.transform.scale(ctext, (int(ctext.get_width() * sc), int(ctext.get_height() * sc)))
                if ct < 15:
                    ctext = ctext.copy(); ctext.set_alpha(int(255 * ct / 15))
                ctext2 = ui.text_outline(f'COMBO  {dmg} DAÑO', 14, C.WHITE)
                cx = 40 if left else C.WIDTH - 40 - ctext.get_width()
                surf.blit(ctext, (cx, 190))
                surf.blit(ctext2, (cx + 6, 190 + ctext.get_height() + 4))
        # temporizador
        pygame.draw.rect(surf, (0, 0, 0), (C.WIDTH / 2 - 52, 18, 104, 76))
        pygame.draw.rect(surf, C.YELLOW, (C.WIDTH / 2 - 50, 20, 100, 72), 3)
        tt = '∞' if self.round_time == 0 else f'{max(0, self.timer):02d}'
        if self.round_time == 0:
            img = ui.text_outline('--', 34, C.YELLOW)
        else:
            col = C.RED if self.timer <= 10 and (t // 15) % 2 else C.YELLOW
            img = ui.text_gradient(tt, 40, (255, 255, 220), col)
        ui.blit_center(surf, img, C.WIDTH / 2, 56)
        if self.training:
            self.draw_training_panel(surf)

    def draw_training_panel(self, surf):
        modes = ['QUIETO', 'AGACHADO', 'SALTA', 'BLOQUEA TODO', 'CPU']
        ui.panel(surf, (C.WIDTH / 2 - 250, 110, 500, 92), (0, 0, 0, 150), C.CYAN, 2)
        lines = [f'ÚLTIMO COMBO: {self.last_combo_dmg} DAÑO',
                 f'F1 RIVAL: {modes[self.dummy_mode]}   F2 HITBOX: {"SÍ" if self.show_hitboxes else "NO"}',
                 'F3 REINICIAR POSICIÓN   ESC PAUSA']
        for i, l in enumerate(lines):
            surf.blit(ui.text(l, 11, C.WHITE if i else C.YELLOW), (C.WIDTH / 2 - 236, 124 + i * 24))
