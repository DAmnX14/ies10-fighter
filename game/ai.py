"""Inteligencia artificial del rival (CPU) con 4 niveles de dificultad.

La IA genera las mismas entradas que un jugador humano (teclas virtuales),
así que usa exactamente el mismo sistema de combate.
"""
import random
import config as C
from game.characters_data import ULTIMATE_COST

LEVELS = [
    # reacción (ticks), prob. bloquear, agresividad, prob. especial, prob. anti-aéreo, errores
    dict(react=26, block=0.15, aggro=0.35, special=0.08, anti=0.05, combo=0.1, ult=0.3),
    dict(react=16, block=0.40, aggro=0.55, special=0.18, anti=0.25, combo=0.35, ult=0.6),
    dict(react=9, block=0.65, aggro=0.70, special=0.25, anti=0.55, combo=0.6, ult=0.85),
    dict(react=4, block=0.85, aggro=0.80, special=0.30, anti=0.80, combo=0.85, ult=1.0),
]

ANTI_AIR = {'nico': 'especial_2', 'parada': 'especial_2', 'nehuen': 'especial_2', 'luciano': 'especial_2', 'pantoja': None,
            'angel': 'especial_2', 'emi': 'especial_2', 'facu': None, 'pedro': 'especial_2', 'denis': None}
ZONER = {'nico': 'especial_1', 'pantoja': 'especial_2', 'nehuen': 'especial_1', 'luciano': 'especial_1', 'parada': None,
         'angel': 'especial_1', 'facu': 'especial_1', 'pedro': 'especial_1', 'emi': 'especial_1', 'denis': 'especial_1'}


class AIController:
    def __init__(self, level=1):
        self.level = max(0, min(3, level))
        self.p = LEVELS[self.level]
        self.plan = []          # lista de (acciones mantenidas, ticks)
        self.cool = 0
        self.mode = None        # para entrenamiento

    def think(self, me, opp, match):
        p = self.p
        dist = abs(opp.x - me.x)
        fwd = 'derecha' if me.facing > 0 else 'izquierda'
        back = 'izquierda' if me.facing > 0 else 'derecha'
        # defensa: el rival ataca cerca
        threat = (opp.state == 'attack' and dist < 330) or \
                 any(pr.owner is opp and abs(pr.x - me.x) < 260 for pr in match.projectiles)
        if threat and random.random() < p['block']:
            low = opp.move is not None and any(h.get('h') == 'low' for h in opp.move.get('hits', []))
            self.plan = [({'bloquear': True, 'abajo': low}, random.randint(14, 26))]
            return
        # anti-aéreo
        if opp.state == 'air' and dist < 320 and random.random() < p['anti']:
            aa = ANTI_AIR.get(me.name)
            if aa:
                self.plan = [({'abajo': True}, 1), ({'abajo': True, 'especial': True}, 2)]
            else:
                self.plan = [({fwd: True, 'golpe': True}, 2)]
            return
        # ultimate
        if me.meter >= ULTIMATE_COST and random.random() < p['ult'] * 0.5:
            if dist < 330 or me.name in ('nehuen', 'nico', 'luciano', 'angel', 'facu', 'pedro', 'emi', 'denis') or (me.name == 'pantoja' and opp.on_ground):
                mod = random.choice([{}, {'abajo': True}, {fwd: True}])
                self.plan = [(dict(mod), 1), (dict(mod, ultimate=True), 2)]
                return
        # castigo: rival cayendo / recuperándose
        if opp.state in ('lying', 'getup') and dist > 160:
            self.plan = [({fwd: True}, random.randint(10, 20))]
            return
        if dist > 420:
            z = ZONER.get(me.name)
            if z and random.random() < p['special'] * 1.5 and me.projectile is None:
                down = z == 'especial_2'
                self.plan = [({'abajo': down}, 1), ({'abajo': down, 'especial': True}, 2), ({}, 12)]
            elif random.random() < 0.15:
                self.plan = [({'arriba': True, fwd: True}, 3), ({}, 20), ({'patada': True}, 2)]
            else:
                self.plan = [({fwd: True}, random.randint(12, 30))]
            return
        if dist > 230:
            r = random.random()
            if r < p['aggro'] * 0.55:
                self.plan = [({fwd: True}, random.randint(8, 18))]
            elif r < p['aggro'] * 0.55 + p['special']:
                if me.name == 'parada':
                    self.plan = [({'especial': True}, 2)]
                elif me.name == 'pantoja' and dist < 380:
                    self.plan = [({'especial': True}, 2)]
                else:
                    z = ZONER.get(me.name)
                    if z and me.projectile is None:
                        down = z == 'especial_2'
                        self.plan = [({'abajo': down}, 1), ({'abajo': down, 'especial': True}, 2)]
                    else:
                        self.plan = [({fwd: True}, 10)]
            elif r < 0.85:
                self.plan = [({'arriba': True, fwd: True}, 3), ({}, 16), ({'patada': True}, 2), ({}, 10)]
            else:
                self.plan = [({back: True}, random.randint(8, 16))]
            return
        # cuerpo a cuerpo
        r = random.random()
        if r < p['aggro']:
            opts = [
                [({'golpe': True}, 2)],
                [({'patada': True}, 2)],
                [({fwd: True, 'golpe': True}, 2)],
                [({fwd: True, 'patada': True}, 2)],
                [({'abajo': True}, 2), ({'abajo': True, 'patada': True}, 2)],
                [({'abajo': True}, 2), ({'abajo': True, 'golpe': True}, 2)],
            ]
            plan = random.choice(opts)
            if random.random() < p['combo']:
                plan = [({'golpe': True}, 2), ({}, 8), ({'golpe': True}, 2), ({}, 8),
                        ({fwd: True, 'patada': True}, 2)]
                if random.random() < p['combo'] * 0.6:
                    down = random.random() < 0.5
                    plan += [({}, 6), ({'abajo': down, 'especial': True}, 2)]
            self.plan = plan + [({}, random.randint(4, 10))]
        elif r < p['aggro'] + 0.15:
            self.plan = [({back: True}, random.randint(10, 18))]
        elif r < p['aggro'] + 0.25:
            self.plan = [({'bloquear': True}, random.randint(10, 20))]
        else:
            self.plan = [({}, random.randint(6, 14))]

    def read(self, me, opp, match):
        held = {a: False for a in C.ACTIONS}
        if self.mode is not None:            # modo entrenamiento
            return self.training(me, opp, match, held)
        if not match.controls_enabled:
            return held
        if me.state not in ('idle', 'walk', 'walkb', 'crouch', 'block', 'cblock', 'air', 'blockstun'):
            self.plan = []
            if me.state in ('hitstun', 'locked'):
                self.cool = self.p['react']
            return held
        if self.cool > 0:
            self.cool -= 1
            if self.plan:
                pass
            else:
                return held
        if not self.plan:
            self.think(me, opp, match)
            self.cool = random.randint(self.p['react'] // 2, self.p['react'])
        if self.plan:
            acts, n = self.plan[0]
            for k, v in acts.items():
                held[k] = v
            n -= 1
            if n <= 0:
                self.plan.pop(0)
            else:
                self.plan[0] = (acts, n)
        return held

    def training(self, me, opp, match, held):
        m = match.dummy_mode
        if m == 1:
            held['abajo'] = True
        elif m == 2:
            held['arriba'] = me.on_ground and random.random() < 0.05
        elif m == 3:
            dist = abs(opp.x - me.x)
            low = opp.move is not None and any(h.get('h') == 'low' for h in opp.move.get('hits', []))
            held['bloquear'] = True
            held['abajo'] = low
        elif m == 4:
            saved = self.mode
            self.mode = None
            out = self.read(me, opp, match)
            self.mode = saved
            return out
        return held
