"""
Audio de la versión 1.3 (todo sintetizado y original):
  - golpes más contundentes estilo arcade de los 90 (reemplazan a los anteriores)
  - sonidos nuevos: maullido, aleteo, campana, tiza, hinchada, corazones, bronca, amistad
  - voces de los 5 personajes nuevos y frases de los encuentros antes de pelear
  - música nueva de pelea, una por escenario, y nuevos temas de menú y selección,
    con síntesis FM de 2 operadores (sonido tipo placa arcade de 16 bits).
Uso: python tools/build_audio_v2.py      (requiere numpy, scipy; espeakng-loader para voces)
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import build_audio as B
from build_audio import (SR, t_, expdec, noise, lowpass, highpass, sweep, norm, softclip, mix, at, reverb,
                         save, freq, parse, stereo, master, MUS)

rng = np.random.default_rng(77)


# ================================================================== efectos
def punch(f0, f1, dur, slap, thump, crunch):
    n = int(SR * dur)
    body = sweep(f0, f1, dur, 'sine', .45) * expdec(n, dur / 3) * thump
    sl = highpass(noise(n), 1800) * expdec(n, .012) * slap
    mid = lowpass(noise(n), 2600) * expdec(n, dur / 5) * .8
    grit = np.sign(body) * np.abs(body) ** .6 * crunch
    return norm(reverb(softclip(body + sl + mid + grit, 3.2), .12, .03), .97)


def sfx():
    S = {}
    S['golpe_debil'] = punch(380, 110, .14, 1.0, 1.0, .1)
    S['golpe_fuerte'] = punch(260, 50, .34, 1.2, 1.3, .5)
    S['patada_debil'] = punch(300, 90, .18, .8, 1.1, .2)
    S['patada_fuerte'] = punch(200, 40, .40, 1.3, 1.4, .7)
    # maullido: formante que sube y baja
    d = .55; n = int(SR * d); tt = t_(d)
    f = 520 + 380 * np.sin(np.pi * tt / d) ** 1.5
    ph = np.cumsum(f / SR)
    v = sum(np.sin(2 * np.pi * ph * k) / k for k in range(1, 6))
    S['maullido'] = norm(reverb(lowpass(v, 3000) * np.sin(np.pi * tt / d) ** .6, .2, .04), .8)
    # aleteo: ráfagas cortas de ruido
    out = np.zeros(int(SR * .5))
    for k in range(5):
        m = int(SR * .05)
        out[int(k * .09 * SR):int(k * .09 * SR) + m] += lowpass(noise(m), 1400) * np.hanning(m)
    S['aleteo'] = norm(out, .7)
    # campana zen
    d = 2.2; n = int(SR * d)
    bell = sum(np.sin(2 * np.pi * fr * t_(d)) * expdec(n, dd) * a for fr, dd, a in
               [(523, 1.4, 1), (1046, .9, .5), (1385, .7, .35), (1760, .5, .25), (2637, .3, .2)])
    S['campana'] = norm(reverb(bell, .35, .1), .85)
    # tiza en el pizarrón
    d = .45; n = int(SR * d)
    S['tiza'] = norm(highpass(noise(n), 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * t_(d))) * np.hanning(n), .6)
    # hinchada: multitud + bombo
    d = 2.6; n = int(SR * d)
    crowd = sum(lowpass(noise(n), 900 + 300 * k) * (0.6 + 0.4 * np.sin(2 * np.pi * (0.7 + .13 * k) * t_(d) + k))
                for k in range(4))
    bombo = np.zeros(n)
    for k in range(6):
        i0 = int(k * .42 * SR); m = int(SR * .3)
        bombo[i0:i0 + m] += sweep(110, 45, .3, 'sine', .5)[:len(bombo[i0:i0 + m])] * expdec(m, .08)[:len(bombo[i0:i0 + m])]
    S['hinchada'] = norm(reverb(crowd * .5 * np.minimum(1, t_(d) * 3) + bombo * 1.2, .3, .1), .9)
    # corazones / amistad / bronca
    S['corazones'] = norm(reverb(mix(*[at(sweep(fr, fr, .3, 'sine') * expdec(int(SR * .3), .12), i * .11)
                                       for i, fr in enumerate([784, 988, 1175, 1568])]), .3, .08), .6)
    S['amistad'] = norm(reverb(mix(*[at(sweep(fr, fr, .35, 'tri') * expdec(int(SR * .35), .14), i * .09)
                                     for i, fr in enumerate([523, 659, 784, 1046, 1318])]), .3, .08), .6)
    d = .6; n = int(SR * d)
    S['bronca'] = norm(softclip(sweep(160, 90, d, 'saw', .7) * expdec(n, .25) + lowpass(noise(n), 500) * expdec(n, .2), 3), .8)
    S['rival'] = norm(reverb(mix(sweep(110, 110, .8, 'saw') * expdec(int(SR * .8), .3),
                                 sweep(116, 116, .8, 'saw') * expdec(int(SR * .8), .3),
                                 at(sweep(220, 220, .6, 'square') * expdec(int(SR * .6), .2) * .5, .25)), .3, .1), .85)
    return S


# ================================================================== voces
NEW_VOICES = {
    'angel': ('es-419+m7', 34, 0.9),
    'facu': ('es-419+m3', 58, 1.04),
    'pedro': ('es-419+m1', 48, 0.97),
    'emi': ('es-419+m4', 60, 1.05),
    'denis': ('es-419+m2', 44, 0.98),
}
NEW_LINES = {
    'angel': {'especial_1': '¡Bug en producción!', 'especial_2': '¡Deploy!', 'ultimate_1': '¡Bucle infinito!',
              'ultimate_2': '¡Stack overflow!', 'nombre': 'Ángel'},
    'facu': {'especial_1': '¡Michi!', 'especial_2': '¡Zarpazo!', 'ultimate_1': '¡Prompt definitivo!',
             'ultimate_2': '¡Lluvia de michis!', 'nombre': 'Facu'},
    'pedro': {'especial_1': '¡Paloma de la paz!', 'especial_2': '¡Onda zen!', 'ultimate_1': '¡Paz interior!',
              'ultimate_2': '¡Bandera blanca!', 'nombre': 'Pedro'},
    'emi': {'especial_1': '¡Avión de papel!', 'especial_2': '¡Mochilazo!', 'ultimate_1': '¡Prueba sorpresa!',
            'ultimate_2': '¡Tabla del nueve!', 'nombre': 'Emi'},
    'denis': {'especial_1': '¡Pelotazo!', 'especial_2': '¡Banda roja!', 'ultimate_1': '¡El Monumental!',
              'ultimate_2': '¡Golazo!', 'nombre': 'Denis'},
}
# frases de los encuentros antes de pelear (personaje_voz_<clave>)
ENCOUNTER_LINES = {
    'denis': {'rival': '¡Bostero! Hoy te gano como en Madrid.', 'odio': 'Parada... a vos te tenía ganas.'},
    'nehuen': {'rival': '¡Gallina! Vení que te bailo.'},
    'pedro': {'saludo': '¡Hola amigo! ¿Todo bien?', 'odio': 'Hasta yo pierdo la paz con vos, Parada.'},
    'emi': {'saludo': '¡Pedro! ¡Qué bueno verte!', 'odio': 'Parada, esto es personal.'},
    'nico': {'saludo': '¡Pedrito! Un abrazo, hermano.', 'abrazo': '¡Ángel! Vení, dame un abrazo.'},
    'luciano': {'saludo': '¡Pedro! ¿Cómo andás, amigo?'},
    'angel': {'abrazo': '¡Nico, jefe! Un abrazo antes de cobrarte.', 'odio': 'Parada, te voy a borrar del sistema.'},
    'facu': {'odio': 'Le pregunté a la IA y me dijo: a Parada, sin piedad.'},
    'pantoja': {'amor': 'Mi amor... perdón, pero hoy te pego.'},
    'parada': {'amor': 'Gordo... después hablamos en casa.', 'odio': '¿Y ahora qué les hice?'},
}


def voices():
    try:
        v = B.Voice()
    except Exception as ex:  # pragma: no cover
        print('Sin espeak-ng: se omiten las voces (', ex, ')')
        return {}
    out = {}
    A = dict(voice='es-419+m3', pitch=28, rate=130, rng_=60)
    for c, lines in NEW_LINES.items():
        out[f'loc_{c}'] = B.announcer(v.say(lines['nombre'], **A))
        out[f'loc_{c}_gana'] = B.announcer(v.say(lines['nombre'] + ' gana', **A))
    for c, (vn, pitch, fac) in NEW_VOICES.items():
        for k, txt in NEW_LINES[c].items():
            if k != 'nombre':
                out[f'{c}_voz_{k}'] = B.shout(v.say(txt, voice=vn, pitch=pitch, rate=175, rng_=90), fac)
        for k, txt in B.GRUNTS.items():
            rate = 120 if k == 'ko' else 200
            out[f'{c}_voz_{k}'] = B.shout(v.say(txt, voice=vn, pitch=pitch + (25 if 'dolor' in k else 0),
                                                rate=rate, rng_=99), fac)
    allv = dict(B.VOICES, **NEW_VOICES)
    for c, lines in ENCOUNTER_LINES.items():
        vn, pitch, fac = allv[c]
        for k, txt in lines.items():
            out[f'{c}_voz_{k}'] = B.shout(v.say(txt, voice=vn, pitch=pitch, rate=160, rng_=70), fac)
    out['loc_nuevo_retador'] = B.announcer(v.say('¡Nuevo retador!', **A))
    return out


# ================================================================== síntesis FM (2 operadores)
def fm(f, n, ratio=1.0, index=2.0, idx_decay=0.15, fb=0.0):
    tt = np.arange(n) / SR
    I = index * (0.35 + 0.65 * np.exp(-tt / max(idx_decay, 1e-3)))
    mod = np.sin(2 * np.pi * f * ratio * tt)
    if fb:
        mod = np.sin(2 * np.pi * f * ratio * tt + fb * mod)
    return np.sin(2 * np.pi * f * tt + I * mod)


PATCH = {   # timbres
    'brass': dict(ratio=1.0, index=3.2, idx_decay=.18, a=.012, d=.15, s=.75, r=.06),
    'lead': dict(ratio=2.0, index=1.6, idx_decay=.4, a=.006, d=.1, s=.8, r=.05),
    'bass': dict(ratio=1.0, index=4.5, idx_decay=.05, a=.002, d=.1, s=.45, r=.03),
    'slap': dict(ratio=3.0, index=3.0, idx_decay=.03, a=.001, d=.08, s=.3, r=.02),
    'bell': dict(ratio=3.5, index=2.0, idx_decay=.3, a=.002, d=.4, s=.2, r=.2),
    'pad': dict(ratio=1.0, index=1.0, idx_decay=1.0, a=.08, d=.3, s=.9, r=.2),
    'orch': dict(ratio=1.0, index=5.0, idx_decay=.08, a=.004, d=.25, s=.25, r=.1),
}


def fm_line(notes, bpm, patch, vol, octave=0, vib=0.0, detune=0.0):
    P = PATCH[patch]
    step = 60 / bpm / 4
    total = sum(dd for _, dd in notes)
    out = np.zeros(int(total * step * SR) + SR)
    pos = 0.0
    for nt, dd in notes:
        if nt is not None:
            f = freq(nt) * 2 ** octave
            L = int(dd * step * SR)
            ff = f * (1 + vib * np.sin(2 * np.pi * 5.5 * np.arange(L) / SR) * np.clip(np.arange(L) / SR * 4 - .3, 0, 1))
            w = fm(ff, L, P['ratio'], P['index'], P['idx_decay'])
            if detune:
                w = .65 * w + .35 * fm(ff * (1 + detune), L, P['ratio'], P['index'], P['idx_decay'])
            e = B.env(L, P['a'], P['d'], P['s'], min(P['r'], dd * step * .5))
            i0 = int(pos * step * SR)
            out[i0:i0 + L] += w * e * vol
        pos += dd
    return out[:int(total * step * SR)]


def drums2(pattern, bpm, bars, vol=1.0):
    """Batería más pesada (bombo con click, redoblante con cuerpo, platillo)."""
    step = 60 / bpm / 4
    L = int(16 * step * SR)
    bar = np.zeros(L)
    n = int(SR * .3)
    kick = softclip(sweep(170, 42, .3, 'sine', .35) * expdec(n, .09) * 1.4 + noise(n) * expdec(n, .003) * .5, 2)
    snare = softclip((highpass(noise(n), 900) * .9 + sweep(260, 170, .3, 'tri') * .7) * expdec(n, .07), 1.8)
    hat = highpass(noise(int(SR * .05)), 7500) * expdec(int(SR * .05), .01)
    ohat = highpass(noise(int(SR * .25)), 6000) * expdec(int(SR * .25), .08)
    crash = highpass(noise(int(SR * 1.2)), 4000) * expdec(int(SR * 1.2), .35)
    tom = sweep(200, 80, .3, 'sine', .5) * expdec(n, .1)
    inst = {'k': (kick, 1.0), 's': (snare, .75), 'h': (hat, .25), 'o': (ohat, .25), 'c': (crash, .35), 't': (tom, .7)}
    for key, pat in pattern.items():
        smp, g = inst[key]
        for i, ch in enumerate(pat):
            if ch == 'x':
                i0 = int(i * step * SR)
                seg = smp[:L - i0]
                bar[i0:i0 + len(seg)] += seg * g
    return np.tile(bar, bars) * vol


def bass_line(roots, style='drive'):
    out = []
    for r in roots:
        oct_ = r[:-1] + str(int(r[-1]) + 1)
        if style == 'drive':
            out += [(r, 2), (r, 2), (oct_, 2), (r, 2), (r, 2), (oct_, 2), (r, 2), (oct_, 2)]
        else:   # funk
            out += [(r, 3), (None, 1), (oct_, 2), (r, 2), (None, 2), (r, 2), (oct_, 2), (r, 2)]
    return out


def stabs(chords, rhythm):
    """Acordes cortos de bronces/orquesta. rhythm: string de 16 pasos."""
    voices_ = [[], [], []]
    for ch in chords:
        ns = ch.split('-')
        i = 0
        while i < 16:
            if rhythm[i] == 'x':
                L = 1
                while i + L < 16 and rhythm[i + L] == '-':
                    L += 1
                for v in range(3):
                    voices_[v].append((ns[v], L))
                i += L
            else:
                for v in range(3):
                    voices_[v].append((None, 1))
                i += 1
    return voices_


# ================================================================== temas (composiciones originales)
def song_aula():
    """Pelea en el aula: rock arcade rápido en Mi menor."""
    bpm = 158
    A = parse('E5:2 G5:2 A5:3 B5:1 A5:2 G5:2 E5:4 D5:2 E5:2 G5:2 A5:2 B5:4 D6:2 B5:2 '
              'A5:2 G5:2 E5:3 D5:1 E5:2 G5:2 A5:4 B5:2 A5:2 G5:2 F#5:2 E5:8')
    Bm = parse('C6:4 B5:2 A5:2 B5:4 G5:4 A5:2 B5:2 C6:2 D6:2 E6:8 '
               'D6:4 C6:2 B5:2 C6:4 A5:4 B5:2 A5:2 G5:2 F#5:2 G5:4 B5:4')
    C = parse('E6:2 D6:2 B5:2 A5:2 G5:2 A5:2 B5:4 E6:2 D6:2 B5:2 D6:2 E6:8 '
              'G6:2 F#6:2 E6:2 D6:2 B5:2 D6:2 E6:4 F#6:4 D#6:4 E6:8')
    lead = A + A + Bm + C
    roots = ['E2', 'E2', 'C2', 'D2', 'E2', 'E2', 'C2', 'B1'] * 2 + ['A1', 'G1', 'C2', 'E2', 'A1', 'G1', 'C2', 'B1'] \
        + ['E2', 'D2', 'C2', 'D2', 'E2', 'D2', 'B1', 'E2']
    chords = ['E3-G3-B3', 'E3-G3-B3', 'C3-E3-G3', 'D3-F#3-A3', 'E3-G3-B3', 'E3-G3-B3', 'C3-E3-G3', 'B2-D#3-F#3'] * 2 \
        + ['A2-C3-E3', 'G2-B2-D3', 'C3-E3-G3', 'E3-G3-B3', 'A2-C3-E3', 'G2-B2-D3', 'C3-E3-G3', 'B2-D#3-F#3'] \
        + ['E3-G3-B3', 'D3-F#3-A3', 'C3-E3-G3', 'D3-F#3-A3', 'E3-G3-B3', 'D3-F#3-A3', 'B2-D#3-F#3', 'E3-G3-B3']
    # cada compás = 8 corcheas -> la melodía está escrita en semicorcheas (16 por compás de 4/4 a 2 compases)
    bars = len(roots)
    lead_s = fm_line(lead, bpm, 'lead', .30, vib=.006, detune=.004)
    lead_s = np.concatenate([lead_s, np.zeros(max(0, bars * int(16 * 60 / bpm / 4 * SR) - len(lead_s)))])
    harm = fm_line(lead, bpm, 'brass', .12, octave=-1)
    bass = fm_line(bass_line(roots), bpm, 'bass', .45)
    sv = stabs(chords, 'x-..x-..x.x...x.')
    st = sum(fm_line(v, bpm, 'orch', .10) for v in sv)
    dr = drums2({'k': 'x.....x.x.x.....', 's': '....x.......x...', 'h': 'x.x.x.x.x.x.x.x.',
                 'o': '..............x.'}, bpm, bars, .9)
    intro = drums2({'k': 'x...x...x...x...', 's': '..........x.xxxx', 'c': 'x...............',
                    'h': 'x.x.x.x.x.x.x.x.'}, bpm, 2, .9)
    intro_b = fm_line(bass_line(['E2', 'E2']), bpm, 'bass', .45)
    body = stereo((lead_s, -.15), (harm, .3), (bass, 0), (st, .25), (dr, 0))
    return master(np.concatenate([stereo((intro, 0), (intro_b, 0)), body]))


def song_plaza():
    """Pelea en la plaza: funk arcade al aire libre en La menor."""
    bpm = 148
    A = parse('A5:3 G5:1 A5:2 C6:2 D6:2 C6:2 A5:4 G5:2 A5:2 C6:2 E6:2 D6:4 C6:4 '
              'A5:3 G5:1 A5:2 C6:2 D6:2 E6:2 G6:4 E6:2 D6:2 C6:2 D6:2 A5:8')
    Bm = parse('F5:2 A5:2 C6:2 F6:4 E6:2 D6:2 C6:2 G5:2 B5:2 D6:2 G6:4 F6:2 E6:2 D6:2 '
               'E6:2 C6:2 A5:2 E6:2 D6:2 B5:2 G#5:2 B5:2 A5:16')
    lead = A + A + Bm
    roots = ['A1', 'A1', 'D2', 'E2', 'A1', 'C2', 'D2', 'E2'] * 2 + ['F1', 'F1', 'G1', 'G1', 'A1', 'E2', 'A1', 'A1']
    chords = ['A3-C4-E4', 'A3-C4-E4', 'D3-F3-A3', 'E3-G#3-B3', 'A3-C4-E4', 'C3-E3-G3', 'D3-F3-A3', 'E3-G#3-B3'] * 2 \
        + ['F3-A3-C4', 'F3-A3-C4', 'G3-B3-D4', 'G3-B3-D4', 'A3-C4-E4', 'E3-G#3-B3', 'A3-C4-E4', 'A3-C4-E4']
    bars = len(roots)
    lead_s = fm_line(lead, bpm, 'brass', .30, vib=.005, detune=.003)
    echo = at(lead_s * .3, 60 / bpm * .75)
    bass = fm_line(bass_line(roots, 'funk'), bpm, 'slap', .5)
    sv = stabs(chords, '..x-..x-..x-..x.')
    st = sum(fm_line(v, bpm, 'lead', .08) for v in sv)
    bells = fm_line(B.chords_to_arp(chords, 16, (0, 1, 2, 1), 2), bpm, 'bell', .06, octave=1)
    dr = drums2({'k': 'x..x..x...x..x..', 's': '....x.......x...', 'h': 'x.xxx.xxx.xxx.xx',
                 'o': '......x.......x.'}, bpm, bars, .85)
    intro = drums2({'k': 'x..x..x...x..x..', 's': '....x.......xxxx', 'c': 'x...............',
                    'h': 'x.xxx.xxx.xxx.xx'}, bpm, 2, .85)
    body = stereo((lead_s, -.1), (echo, .45), (bass, 0), (st, .3), (bells, -.35), (dr, 0))
    return master(np.concatenate([stereo((intro, 0)), body]))


def song_gloriosa():
    """La Gloriosa: cancha cerrada de noche. Rock de tribuna con bombo y palmas, en Sol mayor."""
    bpm = 152
    A = parse('G5:2 G5:2 B5:2 D6:2 B5:4 G5:2 A5:2 B5:2 A5:2 G5:2 E5:2 D5:8 '
              'E5:2 E5:2 G5:2 B5:2 A5:4 G5:2 F#5:2 G5:2 A5:2 B5:2 C6:2 D6:8')
    Bm = parse('E6:4 D6:2 B5:2 C6:4 A5:4 D6:4 B5:2 G5:2 A5:8 '
               'E6:4 D6:2 B5:2 C6:2 B5:2 A5:2 F#5:2 G5:4 B5:4 G5:8')
    lead = A + A + Bm
    roots = ['G1', 'G1', 'C2', 'D2', 'E2', 'C2', 'D2', 'D2'] * 2 + ['C2', 'G1', 'D2', 'E2', 'C2', 'D2', 'G1', 'G1']
    chords = ['G3-B3-D4', 'G3-B3-D4', 'C3-E3-G3', 'D3-F#3-A3', 'E3-G3-B3', 'C3-E3-G3', 'D3-F#3-A3', 'D3-F#3-A3'] * 2 \
        + ['C3-E3-G3', 'G3-B3-D4', 'D3-F#3-A3', 'E3-G3-B3', 'C3-E3-G3', 'D3-F#3-A3', 'G3-B3-D4', 'G3-B3-D4']
    bars = len(roots)
    lead_s = fm_line(lead, bpm, 'brass', .30, vib=.006, detune=.004)
    harm = fm_line(lead, bpm, 'lead', .10, octave=-1)
    bass = fm_line(bass_line(roots), bpm, 'bass', .45)
    sv = stabs(chords, 'x-x-..x-x-x-..x.')
    st = sum(fm_line(v, bpm, 'orch', .09) for v in sv)
    dr = drums2({'k': 'x...x...x...x...', 's': '....x.......x...', 't': 'x..x..x.x..x..x.',
                 'h': 'x.x.x.x.x.x.x.x.', 'c': 'x...............'}, bpm, bars, .9)
    claps = drums2({'s': '..x...x...x.x.x.'}, bpm, bars, .35)
    intro = drums2({'t': 'x..x..x.x..x..x.', 'k': 'x...x...x...x...', 'c': 'x...............'}, bpm, 2, .9)
    body = stereo((lead_s, -.12), (harm, .3), (bass, 0), (st, .25), (dr, 0), (claps, -.3))
    return master(np.concatenate([stereo((intro, 0)), body]))


def song_patio():
    """El Patio: recreo al atardecer. Funk arcade relajado con campanitas, en Fa mayor."""
    bpm = 136
    A = parse('F5:3 A5:1 C6:2 A5:2 Bb5:4 A5:2 G5:2 F5:2 G5:2 A5:2 C6:2 D6:8 '
              'C6:3 A5:1 F5:2 A5:2 G5:4 E5:2 C5:2 D5:2 E5:2 F5:2 G5:2 F5:8')
    Bm = parse('D6:2 C6:2 A5:2 F5:2 G5:4 Bb5:4 A5:2 G5:2 F5:2 E5:2 F5:8 '
               'D6:2 C6:2 Bb5:2 A5:2 G5:4 C6:4 A5:4 G5:2 E5:2 F5:8')
    lead = A + A + Bm
    roots = ['F1', 'F1', 'Bb1', 'C2', 'D2', 'Bb1', 'C2', 'F1'] * 2 + ['Bb1', 'C2', 'A1', 'D2', 'G1', 'C2', 'F1', 'F1']
    chords = ['F3-A3-C4', 'F3-A3-C4', 'Bb2-D3-F3', 'C3-E3-G3', 'D3-F3-A3', 'Bb2-D3-F3', 'C3-E3-G3', 'F3-A3-C4'] * 2 \
        + ['Bb2-D3-F3', 'C3-E3-G3', 'A2-C3-E3', 'D3-F3-A3', 'G2-Bb2-D3', 'C3-E3-G3', 'F3-A3-C4', 'F3-A3-C4']
    bars = len(roots)
    lead_s = fm_line(lead, bpm, 'lead', .28, vib=.005, detune=.003)
    echo = at(lead_s * .3, 60 / bpm * .75)
    bass = fm_line(bass_line(roots, 'funk'), bpm, 'slap', .48)
    bells = fm_line(B.chords_to_arp(chords, 16, (0, 1, 2, 1), 2), bpm, 'bell', .07, octave=1)
    pad = sum(fm_line([(c.split('-')[i], 16) for c in chords], bpm, 'pad', .05, octave=1) for i in range(3))
    dr = drums2({'k': 'x..x..x...x.....', 's': '....x.......x...', 'h': 'x.xxx.xxx.xxx.xx', 'o': '......x.......x.'},
                bpm, bars, .8)
    intro = drums2({'k': 'x..x..x...x.....', 's': '....x.......xxxx', 'h': 'x.xxx.xxx.xxx.xx'}, bpm, 2, .8)
    body = stereo((lead_s, -.1), (echo, .45), (bass, 0), (bells, -.35), (pad, .3), (dr, 0))
    return master(np.concatenate([stereo((intro, 0)), body]))


def song_menu():
    """Menú: tema heroico de torneo en Re menor."""
    bpm = 126
    lead = parse('D5:4 F5:2 A5:2 D6:6 C6:2 Bb5:4 A5:4 G5:2 A5:2 F5:4 D5:4 '
                 'E5:4 F5:2 G5:2 A5:6 Bb5:2 C6:4 A5:4 F5:2 E5:2 D5:8 '
                 'Bb5:4 A5:2 G5:2 A5:4 F5:4 G5:4 F5:2 E5:2 F5:4 D5:4 '
                 'E5:2 F5:2 G5:2 A5:2 Bb5:4 C#6:4 D6:16')
    roots = ['D2', 'Bb1', 'G1', 'A1', 'D2', 'C2', 'Bb1', 'A1']
    chords = ['D3-F3-A3', 'Bb2-D3-F3', 'G2-Bb2-D3', 'A2-C#3-E3', 'D3-F3-A3', 'C3-E3-G3', 'Bb2-D3-F3', 'A2-C#3-E3']
    lead_s = fm_line(lead, bpm, 'brass', .3, vib=.007, detune=.004)
    pad = sum(fm_line([(c.split('-')[i], 16) for c in chords], bpm, 'pad', .07, octave=1) for i in range(3))
    bass = fm_line(bass_line(roots), bpm, 'bass', .4)
    sv = stabs(chords, 'x-.....x-.x-....')
    st = sum(fm_line(v, bpm, 'orch', .09) for v in sv)
    dr = drums2({'k': 'x.......x.x.....', 's': '....x.......x...', 'h': 'x.x.x.x.x.x.x.x.', 'c': 'x...............'},
                bpm, 8, .8)
    return master(stereo((lead_s, -.1), (pad, .3), (bass, 0), (st, -.3), (dr, 0)))


def song_select():
    """Selección: tema tenso y rítmico en Sol menor, en bucle."""
    bpm = 138
    lead = parse('G5:2 -:2 G5:2 Bb5:2 D6:4 C6:2 Bb5:2 A5:2 -:2 A5:2 C6:2 F5:8 '
                 'G5:2 -:2 G5:2 Bb5:2 D6:4 F6:2 Eb6:2 D6:4 C6:4 D6:8 '
                 'Eb6:4 D6:2 C6:2 Bb5:4 A5:4 G5:2 A5:2 Bb5:2 C6:2 D6:8 '
                 'C6:2 Bb5:2 A5:2 G5:2 F#5:4 A5:4 G5:16')
    roots = ['G1', 'F1', 'G1', 'D2', 'Eb2', 'Bb1', 'D2', 'G1']
    chords = ['G2-Bb2-D3', 'F2-A2-C3', 'G2-Bb2-D3', 'D3-F#3-A3', 'Eb3-G3-Bb3', 'Bb2-D3-F3', 'D3-F#3-A3', 'G2-Bb2-D3']
    lead_s = fm_line(lead, bpm, 'lead', .28, vib=.005)
    bass = fm_line(bass_line(roots), bpm, 'bass', .42)
    arp = fm_line(B.chords_to_arp(chords, 16, (0, 1, 2, 1), 1), bpm, 'bell', .06, octave=2)
    dr = drums2({'k': 'x...x...x...x...', 's': '....x.......x..x', 'h': '..x...x...x...x.'}, bpm, 8, .75)
    return master(stereo((lead_s, -.2), (bass, 0), (arp, .35), (dr, 0)))


def main():
    os.makedirs(B.SND, exist_ok=True); os.makedirs(MUS, exist_ok=True)
    only = sys.argv[1:]
    if not only or 'sfx' in only:
        print('efectos...', flush=True)
        for k, x in sfx().items():
            save(k, x)
    if not only or 'voces' in only:
        print('voces...', flush=True)
        for k, x in voices().items():
            save(k, x)
    if not only or 'musica' in only or any(a.startswith('musica_') for a in only):
        print('música...', flush=True)
        songs = [('musica_menu', song_menu), ('musica_seleccion', song_select), ('musica_aula', song_aula),
                 ('musica_plaza', song_plaza), ('musica_gloriosa', song_gloriosa), ('musica_patio', song_patio)]
        pick = [a[len('musica_'):] for a in only if a.startswith('musica_')]
        for name, fn in songs:
            if pick and name not in ['musica_' + p for p in pick]:
                continue
            x = fn()
            save(name, x, MUS, stereo=True)
            print(' ', name, round(len(x) / SR, 1), 's', flush=True)


if __name__ == '__main__':
    main()
