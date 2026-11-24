"""Luchador: máquina de estados, física, ejecución de movimientos y dibujo."""
import random
import pygame
import config as C
from game import assets
from game.characters_data import CHARACTERS, normals, ULTIMATE_COST

GRAVITY = 1.25
JUMP_V = -24.5
FREE = ('idle', 'walk', 'walkb', 'crouch', 'block', 'cblock')


class Fighter:
    def __init__(self, name, side, match):
        self.name = name
        self.side = side
        self.match = match
        self.data = CHARACTERS[name]
        self.spr = assets.character(name)
        st = self.data['stats']
        self.stats = st
        self.max_health = self.data['health']
        self.walk_speed = 2.6 + 0.42 * st['velocidad']
        self.back_speed = self.walk_speed * 0.8
        self.atk_speed = 1.25 - 0.05 * st['ejecucion']          # multiplicador de duración
        self.dmg_mult = 0.78 + 0.045 * st['fuerza']
        self.def_mult = 1.15 - 0.03 * st['resistencia']
        self.reach = 0.85 + 0.035 * st['alcance']
        self.moves = normals()
        self.moves.update(self.data['moves'])
        self.color = self.data['color']
        self.push_w = {'pantoja': 78, 'parada': 64, 'nehuen': 62, 'luciano': 64, 'nico': 64, 'angel': 72, 'facu': 60,
                       'pedro': 66, 'emi': 64, 'denis': 64}.get(name, 64)
        self.reset_round()
        self.wins = 0

    # ------------------------------------------------------------------ estado
    def reset_round(self):
        st = self.match.stage
        mid = st.w / 2
        self.x = mid - 260 if self.side == 1 else mid + 260
        self.ground_y = st.ground_y
        self.y = self.ground_y
        self.vx = self.vy = 0.0
        self.facing = 1 if self.side == 1 else -1
        self.health = self.max_health
        self.shown_health = self.max_health
        self.meter = getattr(self, 'meter', 0)
        self.state = 'idle'
        self.anim = 'idle'
        self.frame = 0
        self.atick = 0
        self.move = None
        self.mframe = 0
        self.mtick = 0
        self.hits_done = set()
        self.stun = 0
        self.stun_total = 1
        self.hitstop = 0
        self.invuln = 0
        self.air_attack_used = False
        self.jump_dir = 0
        self.flash = 0
        self.block_flash = 0
        self.aura = False
        self.afterimage = False
        self.trail = []
        self.locked_by = None
        self.ko = False
        self.combo = 0            # golpes recibidos en el combo actual
        self.combo_dmg = 0
        self.lie = 0
        self.projectile = None
        self.passthrough = False
        self.juggle = False
        self.last_move_name = ''
        self.just_landed = False
        self._was_air = False

    @property
    def on_ground(self):
        return self.y >= self.ground_y - 0.5

    def set_anim(self, name, frame=0):
        if self.anim == name and frame == 0 and name in ('idle', 'caminar', 'caminar_atras'):
            return
        self.anim = name
        self.frame = frame
        self.atick = 0

    def anim_info(self):
        return self.spr.info(self.anim)

    def step_anim(self, loop=None, speed=1.0):
        info = self.anim_info()
        dur = max(1, int(round(info['dur'] * speed)))
        self.atick += 1
        if self.atick >= dur:
            self.atick = 0
            self.frame += 1
            if self.frame >= info['frames']:
                if loop if loop is not None else info['loop']:
                    self.frame = 0
                else:
                    self.frame = info['frames'] - 1
                    return True
        return False

    def can_act(self):
        return self.state in FREE

    def opponent(self):
        return self.match.p2 if self.side == 1 else self.match.p1

    def is_blocking(self, inp=None):
        return self.state in ('block', 'cblock', 'blockstun')

    def crouching(self):
        return self.state in ('crouch', 'cblock') or (self.state == 'blockstun' and self.anim == 'bloquear_agachado') \
            or (self.move is not None and self.move.get('crouch'))

    # ------------------------------------------------------------------ input
    def handle_input(self, inp):
        opp = self.opponent()
        if self.on_ground and self.state in FREE:
            self.facing = 1 if opp.x >= self.x else -1
        fwd = 'derecha' if self.facing > 0 else 'izquierda'
        back = 'izquierda' if self.facing > 0 else 'derecha'
        h = inp.held
        # --- ultimate
        if inp.take('ultimate'):
            if self.meter >= ULTIMATE_COST or self.match.infinite_meter:
                if h['abajo']:
                    key = 'ultimate_2'
                elif h[fwd] and 'ultimate_3' in self.moves:
                    key = 'ultimate_3'
                else:
                    key = 'ultimate_1'
                self.start_ultimate(key)
                return
            else:
                self.match.audio.play('menu_atras', 0.5)
        if inp.take('especial'):
            key = 'especial_2' if h['abajo'] else 'especial_1'
            m = self.moves[key]
            needs_proj = any(e[0] == 'proj' for evs in m.get('events', {}).values() for e in evs)
            if not (needs_proj and self.projectile is not None and self.projectile.alive):
                self.start_move(key)
                return
        if inp.take('golpe'):
            if h['abajo']:
                self.start_move('golpe_agachado')
            elif h[fwd]:
                self.start_move('golpe_fuerte')
            else:
                self.start_move('golpe')
            return
        if inp.take('patada'):
            if h['abajo']:
                self.start_move('patada_agachado')
            elif h[fwd]:
                self.start_move('patada_fuerte')
            else:
                self.start_move('patada')
            return
        if h['arriba']:
            self.jump_dir = (1 if h['derecha'] else -1 if h['izquierda'] else 0)
            self.state = 'jump_pre'
            self.set_anim('saltar_adelante' if self.jump_dir else 'saltar')
            self.stun = 3
            return
        if h['bloquear']:
            if h['abajo']:
                self.state = 'cblock'; self.set_anim('bloquear_agachado') if self.anim != 'bloquear_agachado' else None
            else:
                self.state = 'block'; self.set_anim('bloquear') if self.anim != 'bloquear' else None
            self.vx = 0
            return
        if h['abajo']:
            if self.state != 'crouch':
                self.state = 'crouch'
                self.set_anim('agacharse')
            self.vx = 0
            return
        if h[fwd]:
            self.state = 'walk'
            if self.anim != 'caminar':
                self.set_anim('caminar')
            self.vx = self.walk_speed * self.facing
        elif h[back]:
            self.state = 'walkb'
            if self.anim != 'caminar_atras':
                self.set_anim('caminar_atras')
            self.vx = -self.back_speed * self.facing
        else:
            self.state = 'idle'
            if self.anim != 'idle':
                self.set_anim('idle')
            self.vx = 0

    # ------------------------------------------------------------------ movimientos
    def start_move(self, key):
        m = self.moves[key]
        if m.get('air') and self.on_ground:
            return
        self.move = m
        self.move_key = key
        self.last_move_name = m.get('name', key)
        self.state = 'attack'
        self.set_anim(m['anim'])
        self.mframe = 0
        self.mtick = 0
        self.hits_done = set()
        if self.on_ground:
            self.vx = 0
        self.run_events(0)

    def start_ultimate(self, key):
        if not self.match.infinite_meter:
            self.meter = 0
        self.start_move(key)
        self.invuln = 40
        self.match.super_flash(self, self.moves[key]['name'])

    def frame_len(self):
        m = self.move
        base = self.spr.info(m['anim'])['dur']
        sp = self.atk_speed if not m.get('ult') else 1.0
        return max(1, int(round(base * sp))) + m.get('hold', {}).get(self.mframe, 0)

    def run_events(self, fr):
        evs = self.move.get('events', {}).get(fr, [])
        M = self.match
        for e in evs:
            k = e[0]
            if k == 'vx':
                self.vx = e[1] * self.facing
            elif k == 'vy':
                self.vy = e[1]
                if e[1] < 0:
                    self.y -= 1
            elif k == 'sfx':
                M.audio.play(e[1])
            elif k == 'voice':
                M.audio.voice(self.name, e[1])
            elif k == 'proj':
                M.spawn_projectile(self, e[1])
            elif k == 'shake':
                M.camera.shake(e[1], e[2])
            elif k == 'flash':
                M.screen_flash(e[1], e[2])
            elif k == 'aura':
                self.aura = e[1]
            elif k == 'afterimage':
                self.afterimage = e[1]
            elif k == 'dust':
                M.fx.dust(self.x, self.ground_y)
            elif k == 'fx':
                M.spawn_fx_at_joint(self, e[1], e[2])
            elif k == 'quake':
                M.quake(self, e[1], e[2], e[3] if len(e) > 3 else True)
            elif k == 'strike':
                M.strike(self, e[1], e[2], e[3])
            elif k == 'blast':
                M.blast(self, e[1], e[2])

    def update_move(self):
        m = self.move
        nfr = self.spr.info(m['anim'])['frames']
        ah = m.get('air_hold')
        # aterrizaje durante el movimiento
        if ah and self.on_ground and self.vy >= 0 and ah[0] <= self.mframe <= ah[1] and self._was_air:
            self.mframe = ah[2]
            self.mtick = 0
            self.frame = self.mframe
            self.vx = 0
            self.match.audio.play('aterrizaje')
            self.match.fx.dust(self.x, self.ground_y)
            self.run_events(self.mframe)
            return
        self.mtick += 1
        if self.mtick >= self.frame_len():
            self.mtick = 0
            nxt = self.mframe + 1
            if ah and not self.on_ground and nxt > ah[1] and self.mframe <= ah[1]:
                nxt = ah[1]            # mantener mientras está en el aire
                if nxt == self.mframe:
                    self.frame = self.mframe
                    return
            if m.get('air') and nxt >= nfr:
                self.mframe = nfr - 1  # patada aérea: se mantiene hasta aterrizar
                self.frame = self.mframe
                return
            self.mframe = nxt
            if self.mframe >= nfr:
                self.end_move()
                return
            self.frame = self.mframe
            self.run_events(self.mframe)

    def end_move(self):
        m = self.move
        self.move = None
        self.aura = False
        self.afterimage = False
        self.passthrough = False
        self.match.release_lock(self)
        if not self.on_ground:
            self.state = 'air'
            self.set_anim('saltar', 4)
        else:
            self.state = 'idle'
            self.set_anim('idle')
            self.vx = 0

    def active_hits(self):
        """Golpes activos en el cuadro actual: lista de (hit, x, y, radio)."""
        if self.move is None or 'hits' not in self.move:
            return []
        out = []
        for h in self.move['hits']:
            if h['f'][0] <= self.mframe <= h['f'][1] and h['id'] not in self.hits_done:
                jx, jy = self.spr.joint(self.anim, self.frame, h['j'])
                ox, oy = h['off']
                x, y = self.world_point(jx + ox, jy + oy)
                out.append((h, x, y, h['r'] * C.SCALE * self.reach))
        return out

    def world_point(self, jx, jy):
        ax, ay = self.spr.ax, self.spr.ay
        return self.x + (jx - ax) * C.SCALE * self.facing, self.y + (jy - ay) * C.SCALE

    def hurtbox(self):
        x0, y0, x1, y1 = self.spr.bbox(self.anim, self.frame)
        w = x1 - x0
        x0 += w * 0.14; x1 -= w * 0.14
        a = self.world_point(x0, y0 + 2)
        b = self.world_point(x1, y1)
        return pygame.Rect(min(a[0], b[0]), a[1], abs(b[0] - a[0]), b[1] - a[1])

    # ------------------------------------------------------------------ recibir
    def take_hit(self, hit, attacker, dmg, blocked, locked=False):
        M = self.match
        if blocked:
            chip = int(dmg * hit.get('chip', 0))
            self.health = max(1, self.health - chip) if self.health > 1 else self.health
            self.state = 'blockstun'
            self.stun = hit['bstun']
            self.vx = -self.facing_to(attacker) * hit['kb'] * 0.7
            self.block_flash = 6
            self.meter = min(ULTIMATE_COST, self.meter + 2)
            return
        self.health -= dmg
        self.flash = 3
        self.meter = min(ULTIMATE_COST, self.meter + 4)
        self.move = None
        self.aura = False
        self.afterimage = False
        if self.locked_by is not None and not locked:
            self.locked_by = None
        d = -self.facing_to(attacker)
        if self.health <= 0:
            self.health = 0
            self.ko = True
            self.knockdown(d * max(hit['kb'], 9), min(hit.get('launch', 0), -12) or -12)
            return
        if locked:
            self.state = 'locked'
            self.locked_by = attacker
            self.set_anim('recibir_golpe', 0)
            self.stun = hit['stun']
            self.stun_total = max(1, self.stun)
            if hit.get('kd'):
                self.locked_by = None
                self.knockdown(d * hit['kb'], hit.get('launch', 0) or -10)
            return
        if hit.get('kd') or hit.get('launch') or not self.on_ground or self.juggle:
            self.knockdown(d * hit['kb'], hit.get('launch', 0) or (-9 if not self.on_ground else -6))
            return
        self.state = 'hitstun'
        self.stun = hit['stun']
        self.stun_total = max(1, self.stun)
        self.vx = d * hit['kb']
        self.set_anim('recibir_golpe', 0)
        if random.random() < 0.35:
            M.audio.grunt(self.name, 'dolor')

    def hurt_frame(self):
        """Cuadro de la reacción al golpe según el avance del aturdimiento: el impacto
        se ve enseguida, la postura de dolor se mantiene y al final se recupera la guardia
        (antes la animación terminaba a los pocos ticks y el resto del aturdimiento el
        luchador quedaba quieto como si no lo hubieran golpeado)."""
        if self.anim != 'recibir_golpe':
            self.set_anim('recibir_golpe', 0)
        n = self.anim_info()['frames']
        k = 1.0 - max(0, self.stun) / max(1, self.stun_total)
        if k < 0.18:
            f = 0
        elif k < 0.62:
            f = 1
        elif k < 0.85:
            f = 2
        else:
            f = 3
        self.frame = min(n - 1, f)

    def lock_distance(self, victim):
        """Distancia a la que se sostiene al rival durante una ultimate con agarre.
        Se calcula con el alcance real de los golpes de la animación para que los dos
        sprites no se encimen y todos los golpes sigan conectando."""
        m = self.move
        base = m.get('lock_dist', 100)
        if m.get('passthrough') or not m.get('hits'):
            return base
        key = (self.move_key, victim.name)
        cache = self.__dict__.setdefault('_lock_cache', {})
        if key not in cache:
            nfr = self.spr.info(m['anim'])['frames']
            reach = None
            for h in m['hits']:
                best = None
                for fr in range(h['f'][0], min(h['f'][1], nfr - 1) + 1):
                    jx, _ = self.spr.joint(m['anim'], fr, h['j'])
                    r = (jx + h['off'][0] - self.spr.ax) * C.SCALE
                    best = r if best is None else max(best, r)
                if best is not None:
                    reach = best if reach is None else min(reach, best)
            vfront = None
            vi = victim.spr.info('recibir_golpe')
            for fr in range(vi['frames']):
                x0, _, x1, _ = victim.spr.bbox('recibir_golpe', fr)
                f = (x1 - (x1 - x0) * 0.14 - victim.spr.ax) * C.SCALE
                vfront = f if vfront is None else min(vfront, f)
            d = base if reach is None else reach + (vfront or 0) - 14
            cache[key] = max(base, min(d, base + 140))
        return cache[key]

    def facing_to(self, other):
        return 1 if other.x >= self.x else -1

    def knockdown(self, vx, vy):
        self.state = 'knock'
        self.juggle = True
        self.move = None
        self.vx = vx
        self.vy = vy
        self.y -= 2
        self.facing = 1 if self.opponent().x >= self.x else -1
        self.set_anim('caida', 0)
        if self.ko:
            self.match.audio.voice(self.name, 'ko')
        else:
            self.match.audio.grunt(self.name, 'dolor')

    # ------------------------------------------------------------------ actualización
    def update(self, inp):
        self.flash = max(0, self.flash - 1)
        self.block_flash = max(0, self.block_flash - 1)
        if self.hitstop > 0:
            self.hitstop -= 1
            return
        if self.invuln > 0:
            self.invuln -= 1
        self._was_air = self.just_landed
        self.just_landed = False
        st = self.state
        if st in FREE:
            if inp is not None and self.match.controls_enabled:
                self.handle_input(inp)
            elif st != 'idle':
                self.state = 'idle'; self.set_anim('idle'); self.vx = 0
            if self.state in ('crouch', 'block', 'cblock'):
                self.step_anim(loop=False)
            elif self.state in FREE:
                self.step_anim()
        elif st == 'jump_pre':
            self.stun -= 1
            self.frame = 0
            if self.stun <= 0:
                self.state = 'air'
                self.vy = JUMP_V
                self.vx = self.jump_dir * 5.8
                self.y -= 1
                self.air_attack_used = False
                self.match.audio.play('salto', 0.6)
        elif st == 'air':
            if inp is not None and self.match.controls_enabled and not self.air_attack_used:
                if inp.take('patada') or inp.take('golpe'):
                    self.air_attack_used = True
                    self.start_move('patada_aerea')
                    self._air_jump_anim = self.anim
            self._air_frame()
        elif st == 'land':
            self.stun -= 1
            if self.stun <= 0:
                self.state = 'idle'; self.set_anim('idle')
        elif st == 'attack':
            self.update_move()
        elif st == 'hitstun':
            self.stun -= 1
            self.hurt_frame()
            self.vx *= 0.85
            if self.stun <= 0:
                self.state = 'idle'; self.set_anim('idle'); self.combo_reset()
        elif st == 'blockstun':
            self.stun -= 1
            self.vx *= 0.8
            if self.stun <= 0:
                self.state = 'idle'; self.set_anim('idle')
        elif st == 'locked':
            att = self.locked_by
            self.stun -= 1
            self.hurt_frame()
            if att is not None and att.move is not None and att.move.get('lock'):
                tx = att.x + att.facing * att.lock_distance(self)
                self.x += (tx - self.x) * 0.35
                self.facing = -att.facing
                self.vx = 0
                if not self.on_ground:
                    self.vy = 0
            if att is None or att.move is None or self.stun <= 0:
                self.locked_by = None
                self.knockdown(-self.facing * 8, -10)
        elif st == 'knock':
            if self.on_ground and self.vy >= 0 and self._was_air:
                self.state = 'lying'
                self.lie = 50 if not self.ko else 9999
                self.vx *= 0.3
                self.set_anim('caida', 4)
                self.match.audio.play('caida_suelo')
                self.match.fx.dust(self.x - self.facing * 60, self.ground_y, 2)
                self.match.camera.shake(7, 10)
            else:
                f = 0 if self.vy < -6 else 1 if self.vy < 0 else 2 if self.vy < 8 else 3
                self.frame = f
        elif st == 'lying':
            self.vx *= 0.8
            self.step_anim(loop=False)
            self.lie -= 1
            if self.lie <= 0 and not self.ko:
                self.state = 'getup'
                self.set_anim('levantarse')
                self.invuln = 40
                self.combo_reset()
        elif st == 'getup':
            self.invuln = max(self.invuln, 5)
            if self.step_anim(loop=False):
                self.state = 'idle'; self.set_anim('idle'); self.invuln = 10; self.juggle = False
        elif st in ('victory', 'defeat', 'intro'):
            self.step_anim(loop=(st == 'victory' and self.frame >= 8) or False)
            if st == 'victory' and self.frame >= self.anim_info()['frames'] - 1:
                self.frame = 7
                self.atick = 0
        self.physics()
        # estela
        if self.afterimage:
            self.trail.append((self.anim, self.frame, self.x, self.y, self.facing))
            if len(self.trail) > 6:
                self.trail.pop(0)
        elif self.trail:
            self.trail.pop(0)

    def _air_frame(self):
        if self.anim == 'saltar':
            vy = self.vy
            self.frame = 1 if vy < -14 else 2 if vy < -4 else 3 if vy < 4 else 4 if vy < 14 else 5
        elif self.anim == 'saltar_adelante':
            k = max(0.0, min(1.0, (self.vy - JUMP_V) / (-2 * JUMP_V)))
            self.frame = 1 + min(5, int(k * 6))

    def combo_reset(self):
        self.combo = 0
        self.combo_dmg = 0

    def physics(self):
        M = self.match
        st = self.state
        locked = st == 'locked'
        was_air = not self.on_ground
        if not self.on_ground and not locked:
            self.vy += GRAVITY
        if not locked:
            self.x += self.vx
            self.y += self.vy
        if self.y >= self.ground_y:
            if self.vy > 0 and st == 'air':
                self.state = 'land'
                self.stun = 5
                self.set_anim('saltar' if self.anim == 'saltar' else self.anim, 6 if self.anim == 'saltar' else 7)
                self.vx = 0
                M.audio.play('aterrizaje', 0.5)
            elif self.vy > 0 and st == 'attack' and self.move and self.move.get('air'):
                self.end_move(); self.state = 'land'; self.stun = 6
                self.set_anim('saltar', 6); self.vx = 0
            if was_air:
                self.just_landed = True
            self.y = self.ground_y
            self.vy = 0
            if st in ('hitstun', 'blockstun', 'lying'):
                pass
            elif st == 'attack' and self.move and not self.move.get('air_hold') and self.vx and not \
                    any(e[0] == 'vx' for evs in self.move.get('events', {}).values() for e in evs):
                self.vx = 0
        self.x = max(M.stage.left, min(M.stage.right, self.x))

    # ------------------------------------------------------------------ dibujo
    def draw(self, surf, cam):
        M = self.match
        fx = assets.effects()
        # estela de imágenes residuales
        for i, (an, fr, x, y, fc) in enumerate(self.trail[:-1]):
            img, dx, dy = self.spr.frame_surface(an, fr, fc)
            ghost = img.copy()
            ghost.fill(self.color + (0,), special_flags=pygame.BLEND_RGB_MULT)
            ghost.set_alpha(40 + i * 25)
            sx, sy = cam.to_screen(x, y)
            surf.blit(ghost, (sx + dx, sy + dy))
        # aura
        if self.aura:
            frames = fx.tinted('aura', self.color)
            a = frames[(M.tick // 3) % len(frames)]
            sx, sy = cam.to_screen(self.x, self.y)
            big = pygame.transform.scale(a, (int(a.get_width() * 1.2), int(a.get_height() * 1.25)))
            big.set_alpha(230)
            surf.blit(big, (sx - big.get_width() // 2, sy - big.get_height() + 20))
        img, dx, dy = self.spr.frame_surface(self.anim, self.frame, self.facing)
        sx, sy = cam.to_screen(self.x, self.y)
        if self.flash > 0:
            img = img.copy()
            img.fill((120, 120, 120, 0), special_flags=pygame.BLEND_RGB_ADD)
        elif self.block_flash > 0:
            img = img.copy()
            img.fill((70, 90, 160, 0), special_flags=pygame.BLEND_RGB_ADD)
        elif self.invuln > 0 and self.state == 'getup' and (M.tick // 3) % 2:
            img = img.copy(); img.set_alpha(150)
        surf.blit(img, (sx + dx, sy + dy))
        if self.aura and (M.tick // 4) % 3 == 0:
            glow = img.copy()
            glow.fill(tuple(c // 8 for c in self.color) + (0,), special_flags=pygame.BLEND_RGB_ADD)
            surf.blit(glow, (sx + dx, sy + dy))

    def draw_debug(self, surf, cam):
        r = self.hurtbox()
        x, y = cam.to_screen(r.x, r.y)
        pygame.draw.rect(surf, (0, 255, 0), (x, y, r.w, r.h), 2)
        for h, hx, hy, rad in self.active_hits():
            sx, sy = cam.to_screen(hx, hy)
            pygame.draw.circle(surf, (255, 0, 0), (int(sx), int(sy)), int(rad), 2)
