"""
Datos de los luchadores: estadísticas, colores, frases y TODOS los movimientos.

Formato de un golpe (hit):
  f=(ini, fin)  cuadros activos de la animación       j  articulación que golpea
  r  radio (px nativos)  off  desplazamiento (nativo)  dmg  daño base
  stun / bstun  ticks de aturdimiento al golpear / bloquear   kb  empuje
  kd  derriba   launch  impulso vertical   h  'high' | 'mid' | 'low'
  sfx / fx   sonido y chispa     stop  hitstop     id  identificador (multi-golpe)
Eventos por cuadro: ('vx', v) ('vy', v) ('proj', tipo) ('sfx', n) ('voice', k)
  ('shake', amp, ticks) ('flash', color, ticks) ('fx', efecto, articulación)
  ('aura', bool) ('quake', daño, alcance) ('blast', daño, radio) ('dust',)
"""

GUARD = dict(h='mid')


def H(f, j, dmg, r=14, off=(0, 0), stun=16, bstun=10, kb=6.0, kd=False, launch=0, h='mid',
      sfx='golpe_debil', fx='chispa_golpe', stop=6, id=None, chip=0.0):
    return dict(f=f, j=j, r=r, off=off, dmg=dmg, stun=stun, bstun=bstun, kb=kb, kd=kd,
                launch=launch, h=h, sfx=sfx, fx=fx, stop=stop, id=id or f'{j}{f}', chip=chip)


def normals():
    return {
        'golpe': dict(anim='golpe', name='Jab', hits=[H((1, 2), 'f_ha', 40, r=13, stun=14, bstun=9, kb=5)],
                      events={0: [('sfx', 'aire_debil')]}),
        'patada': dict(anim='patada', name='Patada', hits=[H((2, 3), 'f_an', 50, r=15, off=(4, 0), stun=16, kb=6,
                                                             sfx='patada_debil')],
                       events={1: [('sfx', 'aire_debil')]}),
        'golpe_fuerte': dict(anim='golpe_fuerte', name='Golpe fuerte',
                             hits=[H((3, 4), 'b_ha', 90, r=16, stun=22, bstun=14, kb=10, sfx='golpe_fuerte',
                                     fx='chispa_fuerte', stop=10)],
                             events={2: [('sfx', 'aire_fuerte'), ('voice', 'grito_1')]}),
        'patada_fuerte': dict(anim='patada_fuerte', name='Patada alta',
                              hits=[H((2, 4), 'f_an', 100, r=18, off=(6, -2), stun=24, bstun=14, kb=11,
                                      sfx='patada_fuerte', fx='chispa_fuerte', stop=10)],
                              events={1: [('sfx', 'aire_fuerte'), ('voice', 'grito_2')]}),
        'golpe_agachado': dict(anim='golpe_agachado', name='Jab bajo', crouch=True,
                               hits=[H((1, 2), 'f_ha', 35, r=13, stun=13, bstun=8, kb=5)],
                               events={0: [('sfx', 'aire_debil')]}),
        'patada_agachado': dict(anim='patada_agachado', name='Barrida', crouch=True,
                                hits=[H((2, 3), 'f_an', 75, r=16, off=(4, 2), stun=20, bstun=12, kb=4, kd=True,
                                        h='low', sfx='patada_fuerte', fx='chispa_fuerte', stop=8)],
                                events={1: [('sfx', 'aire_fuerte'), ('dust',)]}),
        'patada_aerea': dict(anim='patada_aerea', name='Patada aérea', air=True,
                             hits=[H((1, 3), 'f_an', 70, r=17, off=(4, 2), stun=18, bstun=12, kb=6, h='high',
                                     sfx='patada_debil')],
                             events={0: [('sfx', 'aire_debil')]}),
    }


CHARACTERS = {
    'pantoja': dict(
        display='PANTOJA', color=(255, 70, 160), color2=(255, 200, 60),
        title='EL MARIDO DE PARADA',
        quote='¡Te paso por arriba como un colectivo!',
        win_quotes=['¡Volvé cuando sepas pelear, pibe!', '¡Esa panza es de acero, papá!',
                    '¡Metal hasta la médula! \\m/'],
        lose_quote='Esto... esto no es ni un tercio de mi poder...',
        stats=dict(fuerza=9, velocidad=4, resistencia=9, alcance=5, ejecucion=5),
        health=1100,
        moves=dict(
            especial_1=dict(anim='especial_1', name='PANZAZO', input='R',
                            hits=[H((2, 5), 'pelvis', 110, r=26, off=(22, -28), stun=24, bstun=16, kb=13, kd=True,
                                    sfx='golpe_fuerte', fx='chispa_fuerte', stop=10, chip=0.1)],
                            events={0: [('voice', 'especial_1')], 2: [('vx', 10), ('sfx', 'dash'), ('dust',)],
                                    6: [('vx', 0)]}),
            especial_2=dict(anim='especial_2', name='GRITO METALERO', input='↓+R',
                            events={1: [('voice', 'especial_2')], 3: [('proj', 'onda_metal'), ('sfx', 'onda_metal'),
                                                                     ('shake', 3, 10)]}),
            ultimate_1=dict(anim='ultimate_1', name='TERREMOTO PANTOJA', input='T', ult=True,
                            air_hold=(4, 8, 9),
                            events={1: [('voice', 'ultimate_1'), ('aura', True)],
                                    3: [('vy', -27), ('sfx', 'salto'), ('dust',)],
                                    7: [('vy', 30)],
                                    9: [('quake', 300, 900), ('sfx', 'terremoto'), ('sfx', 'explosion'),
                                        ('shake', 22, 50), ('flash', (255, 120, 200), 10), ('dust',)],
                                    13: [('aura', False)]},
                            hold={1: 10, 9: 6, 11: 14}),
            ultimate_2=dict(anim='ultimate_2', name='LLUVIA DE CACHETADAS', input='↓+T', ult=True, lock=True,
                            lock_dist=95,
                            hits=[H((i, i), 'f_ha' if i % 2 == 0 else 'b_ha', 17, r=20, stun=30, bstun=10, kb=1,
                                    sfx='cachetada', stop=3, id=f's{i}', chip=0.05) for i in range(2, 12)]
                            + [H((13, 15), 'b_ha', 120, r=34, off=(4, 14), stun=40, kb=8, kd=True, launch=-18,
                                 sfx='golpe_fuerte', fx='chispa_fuerte', stop=18, id='fin')],
                            events={0: [('voice', 'ultimate_2'), ('aura', True)], 2: [('vx', 9)],
                                    12: [('vx', 0)], 14: [('shake', 14, 20), ('flash', (255, 255, 255), 6),
                                                          ('sfx', 'explosion')], 16: [('aura', False)]}),
        ),
    ),
    'parada': dict(
        display='PARADA', color=(40, 210, 110), color2=(190, 255, 120),
        title='EL BESA PERRO',
        quote='¿Me viste? No. Nadie me ve.',
        win_quotes=['Fuiste lento hasta para caerte.', 'La campera ni se despeinó.',
                    'Velocidad, precisión y estilo. Anotalo.'],
        lose_quote='Ugh... me desconcentré un segundo...',
        stats=dict(fuerza=6, velocidad=9, resistencia=5, alcance=6, ejecucion=9),
        health=950,
        moves=dict(
            especial_1=dict(anim='especial_1', name='RÁFAGA ESMERALDA', input='R',
                            hits=[H((2, 4), 'f_ha', 100, r=18, off=(12, 0), stun=22, bstun=14, kb=12, sfx='golpe_fuerte',
                                    fx='chispa_fuerte', stop=9, chip=0.1)],
                            events={0: [('voice', 'especial_1')], 2: [('vx', 15), ('sfx', 'dash'), ('dust',),
                                                                     ('afterimage', True)],
                                    5: [('vx', 0), ('afterimage', False)]}),
            especial_2=dict(anim='especial_2', name='PATADA HURACÁN', input='↓+R', air_hold=(7, 7, 8),
                            hits=[H((1, 3), 'f_an', 60, r=20, off=(4, -4), stun=20, kb=4, launch=-10, sfx='patada_fuerte',
                                    fx='chispa_fuerte', stop=6, id='k1', chip=0.1),
                                  H((4, 5), 'b_an', 70, r=20, off=(4, -4), stun=24, kb=9, kd=True, launch=-14,
                                    sfx='patada_fuerte', fx='chispa_fuerte', stop=9, id='k2', chip=0.1)],
                            events={0: [('voice', 'especial_2')], 1: [('vy', -16), ('vx', 4), ('sfx', 'aire_fuerte')]}),
            ultimate_1=dict(anim='ultimate_1', name='MIL PIÑAS', input='T', ult=True, lock=True, lock_dist=100,
                            hits=[H((i, i), 'f_ha' if i % 2 == 0 else 'b_ha', 17, r=22, stun=30, bstun=8, kb=1,
                                    sfx='golpe_debil', stop=2, id=f'p{i}', chip=0.05) for i in range(2, 16)]
                            + [H((17, 18), 'f_ha', 110, r=24, stun=40, kb=16, kd=True, launch=-12,
                                 sfx='golpe_fuerte', fx='chispa_fuerte', stop=18, id='fin')],
                            events={0: [('voice', 'ultimate_1'), ('aura', True)], 2: [('vx', 12), ('afterimage', True)],
                                    16: [('vx', 0)], 17: [('shake', 14, 18), ('flash', (150, 255, 170), 6),
                                                          ('sfx', 'explosion')],
                                    19: [('aura', False), ('afterimage', False)]},
                            trail=True),
            ultimate_2=dict(anim='ultimate_2', name='TORNADO VERDE', input='↓+T', ult=True, lock=True,
                            lock_dist=60, air_hold=(13, 13, 14), passthrough=(2, 8),
                            hits=[H((3, 3), 'f_ha', 60, r=40, stun=40, kb=0, sfx='golpe_fuerte', stop=5, id='a', chip=0.05),
                                  H((5, 5), 'b_ha', 60, r=40, stun=40, kb=0, sfx='golpe_fuerte', stop=5, id='b', chip=0.05),
                                  H((7, 7), 'f_ha', 60, r=40, stun=40, kb=0, sfx='golpe_fuerte', stop=5, id='c', chip=0.05),
                                  H((9, 11), 'f_an', 130, r=40, off=(0, 12), stun=40, kb=10, kd=True, launch=-20,
                                    sfx='patada_fuerte', fx='chispa_fuerte', stop=18, id='fin')],
                            events={0: [('voice', 'ultimate_2'), ('aura', True)],
                                    2: [('vx', 16), ('fx', 'tornado', 'pelvis'), ('afterimage', True)],
                                    4: [('vx', -16)], 6: [('vx', 16)], 8: [('vx', 0)],
                                    9: [('vy', -18), ('fx', 'tornado', 'pelvis'), ('sfx', 'dash')],
                                    10: [('shake', 16, 20), ('flash', (120, 255, 150), 6)],
                                    14: [('aura', False), ('afterimage', False)]}),
        ),
    ),
    'nehuen': dict(
        display='NEHUEN', color=(60, 140, 255), color2=(255, 205, 50),
        title='EL BOSTERO',
        quote='Este acorde te va a dejar sordo.',
        win_quotes=['Afinado y ganador. Como siempre.', 'Hasta mi piluso te ganaba.',
                    'Bis... ¡bis! ¿No? Bueno.'],
        lose_quote='Se me cortó una cuerda... eso fue todo.',
        stats=dict(fuerza=6, velocidad=6, resistencia=6, alcance=9, ejecucion=6),
        health=1000,
        moves=dict(
            especial_1=dict(anim='especial_1', name='ACORDE SÓNICO', input='R',
                            events={0: [('voice', 'especial_1')], 2: [('sfx', 'guitarra_acorde')],
                                    4: [('proj', 'notas'), ('shake', 2, 8)]}),
            especial_2=dict(anim='especial_2', name='PATADA DEL PILUSO', input='↓+R', air_hold=(6, 6, 7),
                            hits=[H((1, 4), 'f_an', 105, r=22, off=(2, -6), stun=26, bstun=14, kb=8, kd=True,
                                    launch=-16, sfx='patada_fuerte', fx='chispa_fuerte', stop=10, chip=0.1)],
                            events={0: [('voice', 'especial_2')], 1: [('vy', -19), ('vx', 3), ('sfx', 'aire_fuerte')]}),
            ultimate_1=dict(anim='ultimate_1', name='SOLO INFINITO', input='T', ult=True,
                            events={0: [('voice', 'ultimate_1'), ('aura', True)],
                                    4: [('proj', 'rayo_notas'), ('sfx', 'guitarra_solo'), ('shake', 6, 60)],
                                    8: [('sfx', 'guitarra_solo')],
                                    12: [('flash', (120, 200, 255), 8), ('sfx', 'explosion'), ('shake', 14, 16)],
                                    14: [('aura', False)]},
                            hold={12: 8}),
            ultimate_2=dict(anim='ultimate_2', name='METEORO PILUSO', input='↓+T', ult=True,
                            air_hold=(3, 10, 11),
                            hits=[H((7, 10), 'f_an', 110, r=34, off=(4, 2), stun=40, kb=6, kd=True,
                                    sfx='patada_fuerte', fx='chispa_fuerte', stop=12, id='dive', chip=0.1)],
                            events={0: [('voice', 'ultimate_2'), ('aura', True)],
                                    2: [('vy', -34), ('sfx', 'salto'), ('dust',)],
                                    7: [('vy', 24), ('vx', 13), ('sfx', 'aire_fuerte'), ('afterimage', True)],
                                    11: [('vx', 0), ('blast', 200, 210), ('sfx', 'explosion'), ('shake', 20, 30),
                                         ('flash', (255, 220, 120), 8), ('dust',), ('afterimage', False)],
                                    13: [('aura', False)]},
                            hold={11: 8}),
        ),
    ),
    'luciano': dict(
        display='LUCIANO', color=(255, 190, 30), color2=(170, 90, 255),
        title='VOLTIO',
        quote='Firmame acá. Es tu acta de derrota.',
        win_quotes=['Quedás amonestado. Y derrotado.', 'Pasá por preceptoría a retirar tu dignidad.',
                    'Disciplina, pibe. Disciplina.'],
        lose_quote='Esto... va a quedar asentado en el libro de actas.',
        stats=dict(fuerza=7, velocidad=7, resistencia=7, alcance=6, ejecucion=8),
        health=1000,
        moves=dict(
            especial_1=dict(anim='especial_1', name='CREDENCIAL VOLADORA', input='R',
                            events={0: [('voice', 'especial_1')], 4: [('proj', 'credencial'), ('sfx', 'credencial')]}),
            especial_2=dict(anim='especial_2', name='GANCHO PRECEPTOR', input='↓+R', air_hold=(6, 6, 7),
                            hits=[H((2, 4), 'b_ha', 115, r=20, stun=26, bstun=14, kb=6, kd=True, launch=-20,
                                    sfx='golpe_fuerte', fx='chispa_fuerte', stop=11, chip=0.1)],
                            events={0: [('voice', 'especial_2')], 2: [('vy', -15), ('vx', 3), ('sfx', 'aire_fuerte')]}),
            ultimate_1=dict(anim='ultimate_1', name='COMBO DISCIPLINARIO', input='T', ult=True, lock=True,
                            lock_dist=105, air_hold=(13, 15, 16),
                            hits=[H((2, 2), 'f_ha', 50, r=24, stun=40, kb=1, id='1', sfx='golpe_debil', stop=5, chip=.05),
                                  H((4, 4), 'b_ha', 55, r=24, stun=40, kb=1, id='2', sfx='golpe_fuerte', stop=6, chip=.05),
                                  H((6, 7), 'f_ha', 55, r=24, stun=40, kb=1, id='3', sfx='golpe_fuerte', stop=6, chip=.05),
                                  H((8, 8), 'f_an', 50, r=24, stun=40, kb=1, id='4', sfx='patada_debil', stop=5, chip=.05),
                                  H((10, 11), 'f_an', 65, r=26, stun=40, kb=1, id='5', sfx='patada_fuerte', stop=7, chip=.05),
                                  H((13, 14), 'b_ha', 120, r=26, stun=40, kb=8, kd=True, launch=-22, id='fin',
                                    sfx='golpe_fuerte', fx='chispa_fuerte', stop=18)],
                            events={0: [('voice', 'ultimate_1'), ('aura', True)], 2: [('vx', 8)], 3: [('vx', 0)],
                                    13: [('vy', -16), ('shake', 14, 18), ('flash', (255, 220, 100), 6),
                                         ('sfx', 'explosion')],
                                    16: [('aura', False)]}),
            ultimate_2=dict(anim='ultimate_2', name='AMONESTACIÓN FINAL', input='↓+T', ult=True,
                            hits=[H((8, 11), 'b_ha', 340, r=34, off=(8, 0), stun=50, kb=24, kd=True, launch=-14,
                                    sfx='ko_impacto', fx='chispa_fuerte', stop=26, id='fin', chip=0.15)],
                            events={0: [('voice', 'ultimate_2'), ('aura', True), ('sfx', 'carga')],
                                    3: [('sfx', 'energia'), ('shake', 4, 40)],
                                    8: [('vx', 18), ('fx', 'puno_energia', 'b_ha'), ('sfx', 'aire_fuerte'),
                                        ('afterimage', True)],
                                    10: [('vx', 0)],
                                    12: [('aura', False), ('afterimage', False)]},
                            hold={2: 12, 4: 12, 9: 4}),
        ),
    ),
}

# ------------------------------------------------------------------ terceras ultimates
CHARACTERS['pantoja']['moves']['ultimate_3'] = dict(
    anim='ultimate_3', name='COLECTIVAZO', input='→+T', ult=True,
    hits=[H((i, i + 1), 'pelvis', 38, r=26, off=(22, -28), stun=30, bstun=10, kb=2, sfx='golpe_fuerte',
            stop=4, id=f'c{i}', chip=0.05) for i in (2, 4, 6, 8)]
    + [H((10, 11), 'pelvis', 150, r=30, off=(22, -28), stun=40, kb=18, kd=True, launch=-16, sfx='ko_impacto',
         fx='chispa_fuerte', stop=18, id='fin', chip=0.1)],
    events={0: [('voice', 'ultimate_3'), ('aura', True)],
            2: [('vx', 13), ('sfx', 'dash'), ('dust',), ('afterimage', True)], 6: [('dust',), ('sfx', 'dash')],
            10: [('vx', 3), ('shake', 18, 24), ('flash', (255, 120, 200), 8), ('sfx', 'explosion')],
            12: [('vx', 0), ('aura', False), ('afterimage', False)]})
CHARACTERS['parada']['moves']['ultimate_3'] = dict(
    anim='ultimate_3', name='CIEN PATADAS', input='→+T', ult=True, lock=True, lock_dist=120,
    hits=[H((i, i), 'f_an', 21, r=26, stun=30, bstun=8, kb=1, sfx='patada_debil', stop=2, id=f'k{i}', chip=0.05)
          for i in range(2, 14, 2)]
    + [H((14, 15), 'f_an', 150, r=28, stun=40, kb=15, kd=True, launch=-18, sfx='patada_fuerte',
         fx='chispa_fuerte', stop=18, id='fin')],
    events={0: [('voice', 'ultimate_3'), ('aura', True)], 1: [('vx', 12), ('afterimage', True), ('sfx', 'dash')],
            3: [('vx', 3)], 13: [('vx', 0)],
            14: [('shake', 16, 20), ('flash', (150, 255, 170), 6), ('sfx', 'explosion')],
            16: [('aura', False), ('afterimage', False)]})
CHARACTERS['nehuen']['moves']['ultimate_3'] = dict(
    anim='ultimate_3', name='LA BOMBONERA LATE', input='→+T', ult=True,
    events={0: [('voice', 'ultimate_3'), ('aura', True)],
            3: [('quake', 75, 700, False), ('sfx', 'terremoto'), ('shake', 14, 20), ('flash', (60, 120, 255), 5)],
            6: [('quake', 75, 700, False), ('sfx', 'caida_suelo'), ('shake', 16, 20), ('flash', (255, 210, 40), 5)],
            9: [('quake', 170, 850, True), ('sfx', 'explosion'), ('shake', 24, 40), ('flash', (60, 120, 255), 10)],
            11: [('aura', False)]},
    hold={3: 4, 6: 4, 9: 8})
CHARACTERS['luciano']['moves']['ultimate_3'] = dict(
    anim='ultimate_3', name='ALTO VOLTAJE', input='→+T', ult=True,
    events={0: [('voice', 'ultimate_3'), ('aura', True), ('sfx', 'carga')],
            2: [('strike', 'rayo', 80, False), ('sfx', 'rayo'), ('shake', 10, 12), ('flash', (255, 255, 200), 4)],
            5: [('strike', 'rayo', 80, False), ('sfx', 'rayo'), ('shake', 10, 12), ('flash', (255, 255, 200), 4)],
            8: [('strike', 'rayo', 170, True), ('sfx', 'rayo'), ('sfx', 'explosion'), ('shake', 22, 30),
                ('flash', (255, 255, 255), 10)],
            11: [('aura', False)]},
    hold={8: 8})

# ------------------------------------------------------------------ NICO (jefe final)
CHARACTERS['nico'] = dict(
    display='NICO', color=(160, 90, 255), color2=(60, 220, 120),
    title='EL JEFE DE ARCETECH',
    quote='Quedás despedido antes de empezar.',
    win_quotes=['Tu rendimiento no cumple los objetivos.', 'Reunión terminada. Podés retirarte.',
                'En ArceTech no se pierde. Se factura.'],
    lose_quote='Esto... lo vamos a hablar en la próxima reunión.',
    stats=dict(fuerza=8, velocidad=7, resistencia=8, alcance=7, ejecucion=8),
    health=1100,
    moves=dict(
        especial_1=dict(anim='especial_1', name='HOJA DE ARCE', input='R',
                        events={0: [('voice', 'especial_1')], 3: [('proj', 'hoja'), ('sfx', 'proyectil')]}),
        especial_2=dict(anim='especial_2', name='REINICIO FORZADO', input='↓+R', air_hold=(5, 5, 6),
                        hits=[H((1, 4), 'f_kn', 110, r=22, off=(4, 0), stun=26, bstun=14, kb=9, kd=True, launch=-15,
                                sfx='golpe_fuerte', fx='chispa_fuerte', stop=10, chip=0.1)],
                        events={0: [('voice', 'especial_2')], 1: [('vy', -15), ('vx', 9), ('sfx', 'aire_fuerte')]}),
        ultimate_1=dict(anim='ultimate_1', name='PANTALLAZO AZUL', input='T', ult=True,
                        events={0: [('voice', 'ultimate_1'), ('aura', True), ('sfx', 'carga')],
                                4: [('flash', (30, 90, 255), 40), ('strike', None, 300, True), ('sfx', 'explosion'),
                                    ('sfx', 'ko_impacto'), ('shake', 26, 40)],
                                8: [('aura', False)]},
                        hold={1: 6, 3: 6, 4: 16}),
        ultimate_2=dict(anim='ultimate_2', name='DESPIDO INMEDIATO', input='↓+T', ult=True, lock=True,
                        lock_dist=105,
                        hits=[H((2, 2), 'f_ha', 55, r=26, stun=40, kb=1, id='1', sfx='golpe_fuerte', stop=6, chip=.05),
                              H((4, 4), 'f_kn', 60, r=28, stun=40, kb=1, id='2', sfx='golpe_fuerte', stop=7, chip=.05),
                              H((6, 6), 'f_ha', 60, r=28, stun=40, kb=1, id='3', sfx='golpe_fuerte', stop=7, chip=.05),
                              H((9, 10), 'f_an', 170, r=30, stun=40, kb=26, kd=True, launch=-12, id='fin',
                                sfx='ko_impacto', fx='chispa_fuerte', stop=20)],
                        events={0: [('voice', 'ultimate_2'), ('aura', True)], 1: [('vx', 15), ('sfx', 'dash'),
                                                                                 ('afterimage', True)],
                                2: [('vx', 0)],
                                9: [('shake', 18, 24), ('flash', (200, 150, 255), 8), ('sfx', 'explosion')],
                                12: [('aura', False), ('afterimage', False)]}),
    ),
)

PROJECTILES = {
    # tipo: efecto, velocidad, daño, origen, radio (px pantalla), etc.
    'onda_metal': dict(fx='onda_metal', speed=9, dmg=90, joint='head', off=(18, 4), r=48, stun=22, kd=False,
                       kb=9, life=110, sfx='golpe_fuerte', chip=0.15),
    'notas': dict(fx='notas', speed=8, dmg=85, joint='f_ha', off=(10, 6), r=44, stun=20, kb=8, life=130,
                  sfx='golpe_fuerte', chip=0.15),
    'credencial': dict(fx='credencial', speed=11, dmg=70, joint='b_ha', off=(8, 0), r=34, stun=18, kb=6,
                       life=80, boomerang=True, sfx='golpe_debil', chip=0.1),
    'hoja': dict(fx='hoja', speed=12, dmg=85, joint='f_ha', off=(10, 0), r=38, stun=20, kb=8, life=110,
                 sfx='golpe_fuerte', chip=0.15),
    'rayo_notas': dict(fx='rayo_notas', speed=0, dmg=26, joint='f_ha', off=(4, 0), r=60, stun=40, kb=1,
                       life=64, beam=True, interval=6, lock=True, sfx='golpe_debil', chip=0.03,
                       final=dict(dmg=90, kd=True, kb=14, launch=-14)),
}

ULTIMATE_COST = 100


def move_list(char):
    """Lista de movimientos para pausa/galería."""
    c = CHARACTERS[char]
    lst = [('Puñetazo', 'GOLPE'), ('Patada', 'PATADA'), ('Golpe fuerte', '→ + GOLPE'),
           ('Patada alta', '→ + PATADA'), ('Jab bajo', '↓ + GOLPE'), ('Barrida', '↓ + PATADA'),
           ('Patada aérea', 'en el aire GOLPE/PATADA'), ('Bloqueo', 'BLOQUEAR (↓ para bajo)')]
    for k in ('especial_1', 'especial_2', 'ultimate_1', 'ultimate_2', 'ultimate_3'):
        if k not in c['moves']:
            continue
        m = c['moves'][k]
        inp = m['input'].replace('R', 'ESPECIAL').replace('T', 'ULTIMATE')
        lst.append((m['name'], inp + (' (barra llena)' if m.get('ult') else '')))
    return lst


# ====================================================================== PERSONAJES NUEVOS
import copy as _copy


def _like(char, key, **over):
    """Copia un movimiento existente (misma animación base) y le cambia lo indicado."""
    m = _copy.deepcopy(CHARACTERS[char]['moves'][key])
    m.update(over)
    return m


def _swap_proj(m, new):
    for evs in m.get('events', {}).values():
        for i, e in enumerate(evs):
            if e[0] == 'proj':
                evs[i] = ('proj', new)
    return m


def _strikes(fx, sfx, color):
    return {0: [('voice', 'ultimate_2'), ('aura', True), ('sfx', 'carga')],
            2: [('strike', fx, 80, False), ('sfx', sfx), ('shake', 10, 12), ('flash', color, 4)],
            5: [('strike', fx, 80, False), ('sfx', sfx), ('shake', 10, 12), ('flash', color, 4)],
            8: [('strike', fx, 170, True), ('sfx', sfx), ('sfx', 'explosion'), ('shake', 22, 30),
                ('flash', (255, 255, 255), 10)],
            11: [('aura', False)]}


# ---------------------------------------------------------------- ANGEL
CHARACTERS['angel'] = dict(
    display='ANGEL', color=(255, 190, 40), color2=(80, 230, 120),
    title='EL COMPILADOR HUMANO',
    quote='Tu defensa tiene más bugs que mi primer código.',
    win_quotes=['Compiló a la primera. Vos no.', 'git commit -m "le gané"', 'Error 404: rival no encontrado.'],
    lose_quote='Funcionaba en mi máquina...',
    stats=dict(fuerza=8, velocidad=5, resistencia=8, alcance=6, ejecucion=7),
    health=1050,
    moves=dict(
        especial_1=_swap_proj(_like('nico', 'especial_1', name='BUG EN PRODUCCIÓN'), 'codigo'),
        especial_2=_like('luciano', 'especial_2', name='DEPLOY FORZADO'),
        ultimate_1=_like('luciano', 'ultimate_1', name='BUCLE INFINITO'),
        ultimate_2=_like('luciano', 'ultimate_3', name='STACK OVERFLOW', input='↓+T',
                         events=_strikes('lluvia_codigo', 'rayo', (80, 255, 120)), hold={8: 8}),
    ),
)
CHARACTERS['angel']['moves']['ultimate_1']['events'][0] = [('voice', 'ultimate_1'), ('aura', True)]

# ---------------------------------------------------------------- FACU
CHARACTERS['facu'] = dict(
    display='FACU', color=(255, 140, 30), color2=(60, 200, 255),
    title='EL DOMADOR DE LA IA',
    quote='Le pregunté a la IA cómo ganarte. Tardó 0,2 segundos.',
    win_quotes=['Mi gato peleaba mejor que vos.', 'Prompt: "dejalo en el piso". Listo.',
                'Hasta la IA me dijo que fue demasiado fácil.'],
    lose_quote='La IA alucinó... y mi gato se durmió.',
    stats=dict(fuerza=5, velocidad=8, resistencia=5, alcance=9, ejecucion=8),
    health=950,
    moves=dict(
        especial_1=_swap_proj(_like('nico', 'especial_1', name='MICHI NARANJA'), 'gato'),
        especial_2=_like('parada', 'especial_1', name='ZARPAZO GATUNO'),
        ultimate_1=dict(anim='ultimate_1', name='PROMPT DEFINITIVO', input='T', ult=True,
                        events={0: [('voice', 'ultimate_1'), ('aura', True), ('sfx', 'carga')],
                                4: [('proj', 'rayo_ia'), ('sfx', 'energia'), ('shake', 6, 50)],
                                8: [('sfx', 'energia')],
                                12: [('flash', (60, 200, 255), 8), ('sfx', 'explosion'), ('shake', 14, 16)],
                                14: [('aura', False)]},
                        hold={2: 6, 12: 6}),
        ultimate_2=_like('luciano', 'ultimate_3', name='LLUVIA DE MICHIS', input='↓+T',
                         events=_strikes('gatos', 'maullido', (255, 160, 40)), hold={8: 8}),
    ),
)

# ---------------------------------------------------------------- PEDRO
CHARACTERS['pedro'] = dict(
    display='PEDRO', color=(120, 210, 255), color2=(255, 255, 255),
    title='EL HOMBRE DE LA PAZ',
    quote='No quiero pelear... pero si insistís, lo hacemos en paz.',
    win_quotes=['Que la paz te acompañe. En el piso, pero en paz.', 'Respirá hondo. Ya pasó.',
                'Perdón, ¿te dolió? Te invito un mate.'],
    lose_quote='Está bien... la paz también se aprende perdiendo.',
    stats=dict(fuerza=6, velocidad=6, resistencia=9, alcance=7, ejecucion=7),
    health=1100,
    moves=dict(
        especial_1=dict(anim='especial_1', name='PALOMA DE LA PAZ', input='R',
                        events={0: [('voice', 'especial_1')], 3: [('proj', 'paloma'), ('sfx', 'aleteo')]}),
        especial_2=dict(anim='especial_2', name='ONDA ZEN', input='↓+R',
                        events={0: [('voice', 'especial_2'), ('sfx', 'carga')],
                                4: [('blast', 95, 150), ('sfx', 'campana'), ('shake', 6, 10),
                                    ('flash', (200, 240, 255), 4)]},
                        hold={3: 4}),
        ultimate_1=dict(anim='ultimate_1', name='PAZ INTERIOR', input='T', ult=True,
                        events={0: [('voice', 'ultimate_1'), ('aura', True), ('sfx', 'carga')],
                                3: [('sfx', 'campana')],
                                8: [('strike', 'luz', 260, True), ('sfx', 'campana'), ('sfx', 'explosion'),
                                    ('shake', 20, 30), ('flash', (255, 255, 230), 14)],
                                10: [('aura', False)]},
                        hold={4: 8, 7: 6, 8: 8}),
        ultimate_2=_like('luciano', 'ultimate_2', name='BANDERA BLANCA',
                         hits=[H((8, 11), 'f_ha', 330, r=34, off=(8, 0), stun=50, kb=24, kd=True, launch=-14,
                                 sfx='ko_impacto', fx='chispa_fuerte', stop=26, id='fin', chip=0.15)]),
    ),
)
CHARACTERS['pedro']['moves']['ultimate_2']['events'][8] = [('vx', 18), ('fx', 'puno_energia', 'f_ha'),
                                                            ('sfx', 'aire_fuerte'), ('afterimage', True)]

# ---------------------------------------------------------------- EMI
CHARACTERS['emi'] = dict(
    display='EMI', color=(30, 200, 190), color2=(255, 230, 90),
    title='EL ALUMNO EJEMPLAR',
    quote='Estudié toda la noche... tus movimientos.',
    win_quotes=['Aprobado con diez. Vos, a marzo.', 'Esto entra en la prueba, anotalo.',
                'Ni copiándote me ganabas.'],
    lose_quote='Me tocó el tema que no estudié...',
    stats=dict(fuerza=6, velocidad=8, resistencia=6, alcance=7, ejecucion=8),
    health=980,
    moves=dict(
        especial_1=_swap_proj(_like('nico', 'especial_1', name='AVIÓN DE PAPEL'), 'avion'),
        especial_2=_like('luciano', 'especial_2', name='MOCHILAZO'),
        ultimate_1=_like('luciano', 'ultimate_1', name='PRUEBA SORPRESA'),
        ultimate_2=_like('luciano', 'ultimate_3', name='TABLA DEL NUEVE', input='↓+T',
                         events=_strikes('numeros', 'tiza', (255, 240, 120)), hold={8: 8}),
    ),
)

# ---------------------------------------------------------------- DENIS
CHARACTERS['denis'] = dict(
    display='DENIS', color=(230, 30, 50), color2=(255, 255, 255),
    title='EL MILLONARIO',
    quote='Vos alentás a cualquiera. Yo soy de River.',
    win_quotes=['¡Uno más para la vitrina!', 'Esto fue un baile, como en Madrid.',
                'La banda roja nunca se mancha.'],
    lose_quote='Fue offside... clarísimo que fue offside.',
    stats=dict(fuerza=8, velocidad=7, resistencia=6, alcance=8, ejecucion=6),
    health=1000,
    moves=dict(
        especial_1=dict(anim='especial_1', name='PELOTAZO', input='R',
                        events={0: [('voice', 'especial_1')], 1: [('sfx', 'aire_debil')],
                                3: [('proj', 'pelota'), ('sfx', 'patada_fuerte')]}),
        especial_2=_like('parada', 'especial_1', name='BANDA ROJA',
                         hits=[H((2, 4), 'f_ha', 125, r=20, stun=26, bstun=16, kb=14, kd=True, launch=-8,
                                 sfx='golpe_fuerte', fx='chispa_fuerte', stop=11, chip=0.12)]),
        ultimate_1=_like('nehuen', 'ultimate_3', name='EL MONUMENTAL RUGE', input='T',
                         events={0: [('voice', 'ultimate_1'), ('aura', True), ('sfx', 'hinchada')],
                                 3: [('quake', 75, 700, False), ('strike', 'papelitos', 0, False),
                                     ('sfx', 'terremoto'), ('shake', 14, 20), ('flash', (230, 30, 50), 5)],
                                 6: [('quake', 75, 700, False), ('sfx', 'caida_suelo'), ('shake', 16, 20),
                                     ('flash', (255, 255, 255), 5)],
                                 9: [('quake', 170, 850, True), ('strike', 'papelitos', 0, False),
                                     ('sfx', 'explosion'), ('shake', 24, 40), ('flash', (230, 30, 50), 10)],
                                 11: [('aura', False)]}),
        ultimate_2=dict(anim='ultimate_2', name='GOLAZO DE MEDIA CANCHA', input='↓+T', ult=True,
                        events={0: [('voice', 'ultimate_2'), ('aura', True), ('sfx', 'carga')],
                                3: [('vx', 8), ('sfx', 'dash'), ('dust',)], 5: [('vx', 0)],
                                7: [('proj', 'pelota_gigante'), ('sfx', 'patada_fuerte'), ('sfx', 'explosion'),
                                    ('shake', 12, 16), ('flash', (255, 255, 255), 6)],
                                10: [('sfx', 'hinchada')], 12: [('aura', False)]},
                        hold={2: 10, 7: 6}),
    ),
)
CHARACTERS['denis']['moves']['especial_2']['events'][2] = [('vx', 15), ('sfx', 'dash'), ('dust',),
                                                            ('afterimage', True)]

PROJECTILES.update({
    'codigo': dict(fx='codigo', speed=10, dmg=85, joint='f_ha', off=(10, 0), r=38, stun=20, kb=8, life=110,
                   sfx='golpe_fuerte', chip=0.15),
    'gato': dict(fx='gato', speed=9, dmg=80, joint='f_ha', off=(8, 6), r=40, stun=22, kb=8, life=120,
                 sfx='maullido', chip=0.15),
    'paloma': dict(fx='paloma', speed=8, dmg=75, joint='neck', off=(26, 10), r=40, stun=22, kb=7, life=130,
                   sfx='golpe_debil', chip=0.1),
    'avion': dict(fx='avion', speed=12, dmg=70, joint='f_ha', off=(10, 0), r=32, stun=18, kb=6, life=100,
                  sfx='golpe_debil', chip=0.1),
    'pelota': dict(fx='pelota', speed=13, dmg=85, joint='f_toe', off=(6, -4), r=34, stun=20, kb=9, life=100,
                   sfx='golpe_fuerte', chip=0.15),
    'pelota_gigante': dict(fx='pelota_gigante', speed=11, dmg=330, joint='f_toe', off=(14, -20), r=90, stun=40,
                           kb=22, kd=True, life=140, sfx='ko_impacto', chip=0.2),
    'rayo_ia': dict(fx='rayo_ia', speed=0, dmg=26, joint='f_ha', off=(4, 0), r=60, stun=40, kb=1,
                    life=64, beam=True, interval=6, lock=True, sfx='golpe_debil', chip=0.03,
                    final=dict(dmg=90, kd=True, kb=14, launch=-14)),
})

_INPUTS = {'especial_1': 'R', 'especial_2': '↓+R', 'ultimate_1': 'T', 'ultimate_2': '↓+T', 'ultimate_3': '→+T'}
for _c in ('angel', 'facu', 'pedro', 'emi', 'denis'):
    for _k, _m in CHARACTERS[_c]['moves'].items():
        _m['anim'] = _k
        _m['input'] = _INPUTS[_k]


# ====================================================================== NEHUEN BOSTERO (v1.6)
# Deja la guitarra: ahora es hincha fanático de Boca (azul y oro). Textos originales.
_n = CHARACTERS['nehuen']
_n.update(
    title='EL BOSTERO',
    quote='Acá se juega como en la Bombonera: con todo.',
    win_quotes=['¡Dale Bo! Uno más para la historia.', 'Azul y oro, como la copa que me llevo.',
                'Te ganó la mitad más uno, pibe.'],
    lose_quote='Fue penal... clarísimo que fue penal.',
)
_n['moves']['especial_1'] = dict(anim='especial_1', name='BUFANDAZO', input='R',
                                 events={0: [('voice', 'especial_1')], 2: [('sfx', 'aire_fuerte')],
                                         3: [('proj', 'bufanda'), ('sfx', 'proyectil')]})
_n['moves']['especial_2']['name'] = 'CHILENA XENEIZE'
_n['moves']['ultimate_1'] = dict(anim='ultimate_1', name='AZUL Y ORO', input='T', ult=True,
                                 events={0: [('voice', 'ultimate_1'), ('aura', True), ('sfx', 'hinchada')],
                                         4: [('proj', 'rayo_xeneize'), ('sfx', 'energia'), ('shake', 6, 50)],
                                         8: [('sfx', 'hinchada')],
                                         12: [('flash', (255, 210, 60), 8), ('sfx', 'explosion'), ('shake', 14, 16)],
                                         14: [('aura', False)]},
                                 hold={2: 6, 12: 6})
_u2 = _n['moves']['ultimate_2']
_u2['name'] = 'LA DOCE SALTA'
_u2['events'][0] = [('voice', 'ultimate_2'), ('aura', True), ('sfx', 'hinchada')]
_u2['events'][11] = _u2['events'][11] + [('strike', 'papelitos_boca', 0, False)]
_u3 = _n['moves']['ultimate_3']
_u3['events'][0] = [('voice', 'ultimate_3'), ('aura', True), ('sfx', 'hinchada')]
_u3['events'][3] = _u3['events'][3] + [('strike', 'papelitos_boca', 0, False)]
_u3['events'][9] = _u3['events'][9] + [('strike', 'papelitos_boca', 0, False)]
PROJECTILES['bufanda'] = dict(fx='bufanda', speed=10, dmg=85, joint='f_ha', off=(10, 0), r=42, stun=20, kb=8,
                              life=120, sfx='golpe_fuerte', chip=0.15)
PROJECTILES['rayo_xeneize'] = dict(PROJECTILES['rayo_notas'], fx='rayo_xeneize')
