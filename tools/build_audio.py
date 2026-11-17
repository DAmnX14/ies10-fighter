"""
Genera TODO el audio del juego de forma procedural (síntesis original):
  - efectos de sonido (golpes, patadas, bloqueos, saltos, menú, especiales...)
  - voces del locutor y gritos de los personajes (síntesis de voz espeak-ng)
  - 5 temas musicales chiptune estilo arcade de los 90 (composiciones originales)

Uso: python tools/build_audio.py
Requiere: numpy; opcional espeakng-loader (voces) y ffmpeg (OGG). Sin ellos se
usa WAV y se omiten las voces.
"""
import os, sys, wave, math, shutil, subprocess, ctypes
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SND = os.path.join(ROOT, 'assets', 'sounds')
MUS = os.path.join(ROOT, 'assets', 'music')
SR = 44100
rng = np.random.default_rng(10)


# ------------------------------------------------------------------ utilidades
def t_(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.002, d=0.1, s=0.0, r=0.05, total=None):
    """ADSR simple sobre n muestras."""
    e = np.zeros(n)
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    A = max(A, 1)
    e[:A] = np.linspace(0, 1, A)
    e[A:A + D] = np.linspace(1, s, len(e[A:A + D]))
    e[A + D:] = s
    if R > 0 and s > 0:
        e[-R:] *= np.linspace(1, 0, R)
    return e


def expdec(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def noise(n):
    return rng.uniform(-1, 1, n)


def lowpass(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.zeros_like(x); acc = 0.0
    # filtro de un polo vectorizado por bloques
    from scipy.signal import lfilter  # noqa
    return lfilter([1 - a], [1, -a], x)


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def sweep(f0, f1, d, wave='sine', curve=2.0):
    n = int(SR * d)
    k = np.linspace(0, 1, n) ** curve
    f = f0 + (f1 - f0) * k
    ph = np.cumsum(2 * np.pi * f / SR)
    if wave == 'sine':
        return np.sin(ph)
    if wave == 'square':
        return np.sign(np.sin(ph))
    if wave == 'saw':
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if wave == 'tri':
        return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def softclip(x, drive=1.5):
    return np.tanh(x * drive) / np.tanh(drive)


def pad(x, d):
    return np.concatenate([x, np.zeros(int(SR * d))])


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def at(x, delay):
    return np.concatenate([np.zeros(int(SR * delay)), x])


def reverb(x, wet=0.25, room=0.08):
    out = x.copy()
    for i, (d, g) in enumerate([(room, .5), (room * 1.37, .4), (room * 1.83, .3), (room * 2.6, .2), (room * 3.4, .12)]):
        out = mix(out, at(x * g * wet * 2, d))
    return out


def write_wav(path, x, sr=SR, stereo=False):
    x = np.clip(x, -1, 1)
    if stereo and x.ndim == 1:
        x = np.stack([x, x], 1)
    data = (x * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2 if data.ndim == 2 else 1)
        w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(data.tobytes())


HAVE_FFMPEG = shutil.which('ffmpeg') is not None


def save(name, x, folder=SND, ogg=True, stereo=False):
    os.makedirs(folder, exist_ok=True)
    wav = os.path.join(folder, name + '.wav')
    write_wav(wav, x, stereo=stereo)
    if ogg and HAVE_FFMPEG:
        oggp = os.path.join(folder, name + '.ogg')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'libvorbis',
                        '-q:a', '5', oggp], check=True)
        os.remove(wav)


# ------------------------------------------------------------------ efectos
def sfx():
    S = {}
    # golpes: cuerpo grave + chasquido de ruido
    def hit(f0, f1, dur, nz, tone_amp=1.0, crunch=0.0):
        n = int(SR * dur)
        body = sweep(f0, f1, dur, 'sine', 0.5) * expdec(n, dur / 3.5) * tone_amp
        sn = lowpass(noise(n), 3500 + 2000 * crunch) * expdec(n, dur / 6) * nz
        click = noise(n) * expdec(n, 0.004) * 0.7
        return norm(softclip(body + sn + click, 2.5 + crunch * 2), 0.95)
    S['golpe_debil'] = hit(320, 90, 0.16, 0.8)
    S['golpe_fuerte'] = hit(220, 45, 0.32, 1.0, crunch=0.6)
    S['patada_debil'] = hit(260, 70, 0.2, 0.9, 0.9)
    S['patada_fuerte'] = hit(180, 38, 0.38, 1.1, 1.2, crunch=1.0)
    S['cachetada'] = norm(highpass(noise(int(SR * .12)), 1500) * expdec(int(SR * .12), .02)
                          + hit(500, 200, .12, .2) * .5)
    n = int(SR * .22)
    S['bloqueo'] = norm(mix(sweep(1400, 900, .22, 'square') * expdec(n, .03) * .5,
                            highpass(noise(n), 2500) * expdec(n, .02),
                            sweep(700, 650, .22, 'tri') * expdec(n, .06) * .6), .8)
    def whoosh(d, f0, f1, amp=1.0):
        n = int(SR * d)
        x = noise(n)
        e = np.sin(np.linspace(0, np.pi, n)) ** 1.5
        cut = np.linspace(f0, f1, n)
        y = np.zeros(n); a_prev = 0.0
        from scipy.signal import lfilter
        out = []
        for i in range(0, n, 512):
            a = math.exp(-2 * math.pi * cut[i] / SR)
            out.append(lfilter([1 - a], [1, -a], x[i:i + 512]))
        y = np.concatenate(out)
        return norm(y * e, 0.6 * amp)
    S['aire_debil'] = whoosh(.13, 1500, 4000)
    S['aire_fuerte'] = whoosh(.25, 800, 3500, 1.2)
    n = int(SR * .7)
    S['caida_suelo'] = norm(softclip(sweep(120, 35, .7, 'sine', .4) * expdec(n, .15) * 1.3
                                     + lowpass(noise(n), 600) * expdec(n, .12), 3), .95)
    S['salto'] = norm(sweep(180, 520, .16, 'square', .7) * expdec(int(SR * .16), .07) * .5
                      + whoosh(.16, 2000, 5000) * .6, .5)
    n = int(SR * .15)
    S['aterrizaje'] = norm(lowpass(noise(n), 400) * expdec(n, .03) + sweep(90, 50, .15) * expdec(n, .04), .6)
    S['menu_mover'] = norm(mix(sweep(880, 880, .05, 'square') * expdec(int(SR * .05), .02),
                               at(sweep(1320, 1320, .05, 'square') * expdec(int(SR * .05), .02), .04)), .35)
    S['menu_ok'] = norm(mix(*[at(sweep(f, f, .09, 'square') * expdec(int(SR * .09), .05), i * .06)
                              for i, f in enumerate([660, 880, 1320])]), .45)
    S['menu_atras'] = norm(mix(*[at(sweep(f, f, .09, 'square') * expdec(int(SR * .09), .05), i * .06)
                                 for i, f in enumerate([880, 590])]), .4)
    S['seleccion'] = norm(reverb(mix(*[at(sweep(f, f * 1.01, .25, 'saw') * expdec(int(SR * .25), .1), i * .05)
                                       for i, f in enumerate([523, 659, 784, 1046])]), .3), .6)
    S['moneda'] = norm(mix(sweep(988, 988, .08, 'square') * .6, at(sweep(1319, 1319, .35, 'square')
                           * expdec(int(SR * .35), .12), .08)), .4)
    n = int(SR * 1.6)
    gong = sum(np.sin(2 * np.pi * f * t_(1.6)) * expdec(n, d) * a for f, d, a in
               [(110, .9, 1), (221, .6, .6), (331, .4, .4), (447, .3, .3), (563, .25, .2)])
    S['gong'] = norm(reverb(gong + lowpass(noise(n), 900) * expdec(n, .05) * .5, .4, .11), .9)
    n = int(SR * 1.3)
    S['ko_impacto'] = norm(reverb(softclip(sweep(160, 25, 1.3, 'sine', .35) * expdec(n, .35) * 1.5
                                           + lowpass(noise(n), 1200) * expdec(n, .25), 3), .35, .12), .98)
    n = int(SR * .9)
    S['carga'] = norm(sweep(100, 900, .9, 'saw', 1.5) * np.linspace(.2, 1, n) * .5
                      + highpass(noise(n), 3000) * np.linspace(0, .4, n), .55)
    n = int(SR * .5)
    S['proyectil'] = norm(mix(sweep(900, 200, .5, 'square', .6) * expdec(n, .2) * .5,
                              whoosh(.5, 1000, 3000) * .8), .7)
    n = int(SR * 1.4)
    flash = mix(sweep(200, 2400, .35, 'saw', 2) * .5,
                at(np.sin(2 * np.pi * 1760 * t_(1.0)) * expdec(int(SR), .4) * .4, .3),
                at(np.sin(2 * np.pi * 2637 * t_(1.0)) * expdec(int(SR), .3) * .3, .3),
                highpass(noise(n), 4000) * expdec(n, .3) * .3)
    S['ultimate_activar'] = norm(reverb(flash, .4, .09), .85)
    n = int(SR * 1.5)
    S['explosion'] = norm(reverb(softclip(lowpass(noise(n), 900) * expdec(n, .35) * 1.4
                                          + sweep(90, 30, 1.5) * expdec(n, .3), 2.5), .3, .1), .98)
    n = int(SR * 2.2)
    S['terremoto'] = norm(softclip(lowpass(noise(n), 160) * (1 - np.linspace(0, 1, n) ** 2) * 2
                                   + sweep(55, 35, 2.2) * expdec(n, .8), 2), .98)
    n = int(SR * .8)
    ring = np.sin(2 * np.pi * (300 + 40 * np.sin(2 * np.pi * 30 * t_(.8))) * t_(.8))
    S['onda_metal'] = norm(softclip(mix(sweep(260, 120, .8, 'saw', .5) * expdec(n, .3),
                                        ring * expdec(n, .25) * .6), 3), .8)
    # acorde de guitarra eléctrica distorsionada (Karplus-Strong)
    def pluck(f, d, bright=0.5):
        n = int(SR * d); N = int(SR / f)
        buf = noise(N) * 0.8
        out = np.zeros(n)
        for i in range(n):
            out[i] = buf[i % N]
            buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N]) * 0.996
        return out
    def chord(root, d=1.4, strum=0.012):
        fs = [root, root * 1.5, root * 2, root * 2.52]
        return mix(*[at(pluck(f, d), i * strum) for i, f in enumerate(fs)])
    S['guitarra_acorde'] = norm(reverb(softclip(chord(110) * 3, 4), .25), .85)
    riff = mix(*[at(softclip(chord(f, .45, .006) * 3, 4), i * .16) for i, f in
                 enumerate([110, 110, 131, 147, 110, 165, 147, 131])])
    S['guitarra_solo'] = norm(reverb(riff, .25), .85)
    n = int(SR * .6)
    S['credencial'] = norm(np.sign(np.sin(2 * np.pi * 14 * t_(.6))) * highpass(noise(n), 2000) * .4
                           + sweep(700, 1200, .6, 'tri') * .3, .55)
    S['dash'] = norm(whoosh(.3, 600, 6000, 1.5) + sweep(300, 1200, .3, 'square', .4) * expdec(int(SR * .3), .1) * .3, .7)
    n = int(SR * .5)
    S['energia'] = norm(mix(sweep(300, 1200, .5, 'saw', .5) * expdec(n, .25) * .4,
                            np.sin(2 * np.pi * 70 * t_(.5)) * expdec(n, .2)), .75)
    n = int(SR * 3.0)
    crowd = lowpass(noise(n), 1400) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.7 * t_(3.0)) ** 2)
    S['publico'] = norm(crowd * np.minimum(1, np.linspace(0, 6, n)) * np.minimum(1, np.linspace(6, 0, n)), .5)
    n = int(SR * .08)
    S['tic'] = norm(sweep(1600, 1600, .08, 'square') * expdec(n, .02), .3)
    S['combo'] = norm(mix(*[at(sweep(f, f, .07, 'square') * expdec(int(SR * .07), .04), i * .04)
                            for i, f in enumerate([1046, 1318, 1568])]), .35)
    return S


# ------------------------------------------------------------------ voces
class Voice:
    def __init__(self):
        import espeakng_loader as e
        self.lib = ctypes.cdll.LoadLibrary(e.get_library_path())
        self.buf = []
        CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)
        def cb(wav, n, ev):
            if wav and n > 0:
                self.buf.extend(wav[:n])
            return 0
        self._cb = CB(cb)
        self.sr = self.lib.espeak_Initialize(2, 0, e.get_data_path().encode(), 0)
        self.lib.espeak_SetSynthCallback(self._cb)

    def say(self, text, voice='es-419+m3', rate=150, pitch=50, rng_=50):
        self.buf = []
        self.lib.espeak_SetVoiceByName(voice.encode())
        self.lib.espeak_SetParameter(1, rate, 0)
        self.lib.espeak_SetParameter(3, pitch, 0)
        self.lib.espeak_SetParameter(4, rng_, 0)
        t = text.encode('utf-8')
        self.lib.espeak_Synth(t, len(t) + 1, 0, 0, 0, 0x10000, None, None)  # espeakCHARS_UTF8
        self.lib.espeak_Synchronize()
        a = np.array(self.buf, dtype=np.float64) / 32768
        # remuestrear a 44.1k
        n = int(len(a) * SR / self.sr)
        return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a)


def pitch_shift(x, factor):
    """Cambia tono y duración (estilo cinta)."""
    n = int(len(x) / factor)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def announcer(x):
    x = pitch_shift(x, 0.86)
    x = softclip(norm(x) * 1.0, 2.2)
    x = lowpass(x, 5500)
    return norm(reverb(x, .35, .07), .95)


def shout(x, factor=1.0):
    x = pitch_shift(x, factor)
    x = softclip(norm(x), 3.0)
    return norm(reverb(x, .15, .05), .95)


VOICES = {   # voz espeak, tono, factor de remuestreo
    'pantoja': ('es-419+m7', 30, 0.88),
    'parada': ('es-419+m2', 55, 1.02),
    'nehuen': ('es-419+m4', 62, 1.06),
    'nico': ('es-419+m5', 36, 0.92),
    'luciano': ('es-419+m1', 45, 0.96),
}
CHAR_LINES = {
    'nico': {'especial_1': '¡Hoja de arce!', 'especial_2': '¡Reinicio forzado!',
             'ultimate_1': '¡Pantallazo azul!', 'ultimate_2': '¡Despido inmediato!', 'nombre': 'Nico'},
    'pantoja': {'especial_1': '¡Panzazo!', 'especial_2': '¡Grito metalero!',
                'ultimate_1': '¡Terremoto Pantoja!', 'ultimate_2': '¡Lluvia de cachetadas!',
                'nombre': 'Pantoja'},
    'parada': {'especial_1': '¡Ráfaga!', 'especial_2': '¡Huracán!',
               'ultimate_1': '¡Mil piñas!', 'ultimate_2': '¡Tornado verde!', 'nombre': 'Parada'},
    'nehuen': {'especial_1': '¡Acorde sónico!', 'especial_2': '¡Piluso!',
               'ultimate_1': '¡Solo infinito!', 'ultimate_2': '¡Meteoro piluso!', 'nombre': 'Nejuén'},
    'luciano': {'especial_1': '¡Credencial!', 'especial_2': '¡Gancho!',
                'ultimate_1': '¡Combo disciplinario!', 'ultimate_2': '¡Amonestación final!',
                'nombre': 'Luciano'},
}
GRUNTS = {'grito_1': 'ja', 'grito_2': 'jiá', 'grito_3': 'sha', 'dolor_1': 'uh', 'dolor_2': 'aj',
          'ko': 'aaaaaaah', 'victoria': '¡Sí! ¡Gané!'}


def voices():
    try:
        v = Voice()
    except Exception as ex:  # pragma: no cover
        print('Sin espeak-ng: se omiten las voces (', ex, ')')
        return {}
    out = {}
    A = dict(voice='es-419+m3', pitch=28, rate=130, rng_=60)
    ann = {
        'loc_ronda_1': 'Ronda uno', 'loc_ronda_2': 'Ronda dos', 'loc_ronda_final': 'Ronda final',
        'loc_pelea': '¡Peleen!', 'loc_ko': 'K. O.', 'loc_tiempo': '¡Tiempo!', 'loc_empate': 'Empate',
        'loc_perfecto': '¡Perfecto!', 'loc_titulo': 'I E S diez, Fighter',
        'loc_elegi': 'Elegí a tu pelotudo', 'loc_gana': 'gana', 'loc_continuar': '¿Continuar?',
        'loc_fin': 'Fin del juego', 'loc_nuevo_retador': '¡Nuevo retador!',
    }
    for k, txt in ann.items():
        out[k] = announcer(v.say(txt, **A))
    for c in VOICES:
        out[f'loc_{c}'] = announcer(v.say(CHAR_LINES[c]['nombre'], **A))
        out[f'loc_{c}_gana'] = announcer(v.say(CHAR_LINES[c]['nombre'] + ' gana', **A))
    for c, (vn, pitch, fac) in VOICES.items():
        for k, txt in CHAR_LINES[c].items():
            if k == 'nombre':
                continue
            out[f'{c}_voz_{k}'] = shout(v.say(txt, voice=vn, pitch=pitch, rate=175, rng_=90), fac)
        for k, txt in GRUNTS.items():
            rate = 120 if k == 'ko' else 200
            out[f'{c}_voz_{k}'] = shout(v.say(txt, voice=vn, pitch=pitch + (25 if 'dolor' in k else 0),
                                              rate=rate, rng_=99), fac)
    return out


# ------------------------------------------------------------------ música
NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def freq(n):
    name, octv = n[:-1], int(n[-1])
    midi = 12 * (octv + 1) + NOTE[name]
    return 440 * 2 ** ((midi - 69) / 12)


def parse(seq):
    """'A4:2 C5:2 -:4' -> [(nota|None, dur_en_semicorcheas)]"""
    out = []
    for tok in seq.split():
        n, d = tok.split(':')
        out.append((None if n == '-' else n, float(d)))
    return out


def osc(kind, f, n, duty=0.5, vib=0.0):
    tt = np.arange(n) / SR
    fm = f * (1 + vib * np.sin(2 * np.pi * 5.5 * tt) * np.clip(tt * 4 - 0.4, 0, 1))
    ph = np.cumsum(fm / SR) % 1
    if kind == 'square':
        return np.where(ph < duty, 1.0, -1.0)
    if kind == 'saw':
        return 2 * ph - 1
    if kind == 'tri':
        return 2 * np.abs(2 * ph - 1) - 1
    if kind == 'sine':
        return np.sin(2 * np.pi * ph)


def render_line(notes, bpm, kind, vol, duty=0.5, vib=0.0, a=0.005, d=0.12, s=0.6, r=0.04,
                detune=0.0, octave=0):
    step = 60 / bpm / 4
    total = sum(dd for _, dd in notes)
    out = np.zeros(int(total * step * SR) + SR)
    pos = 0.0
    for n, dd in notes:
        if n is not None:
            f = freq(n) * 2 ** octave
            L = int(dd * step * SR)
            w = osc(kind, f, L, duty, vib)
            if detune:
                w = 0.6 * w + 0.4 * osc(kind, f * (1 + detune), L, duty, vib)
            e = env(L, a, d, s, min(r, dd * step * 0.5))
            i0 = int(pos * step * SR)
            out[i0:i0 + L] += w * e * vol
        pos += dd
    return out[:int(total * step * SR)]


def drums(pattern, bpm, bars, vol=1.0):
    """pattern: dict instr -> string de 16 pasos ('x' golpe, '.' silencio)."""
    step = 60 / bpm / 4
    L = int(16 * step * SR)
    bar = np.zeros(L)
    n = int(SR * .25)
    kick = sweep(150, 40, .25, 'sine', .4) * expdec(n, .07)
    snare = (highpass(noise(n), 1200) * .7 + sweep(240, 180, .25, 'tri') * .5) * expdec(n, .05)
    hat = highpass(noise(int(SR * .06)), 7000) * expdec(int(SR * .06), .012)
    ohat = highpass(noise(int(SR * .2)), 6000) * expdec(int(SR * .2), .06)
    tom = sweep(220, 90, .25, 'sine', .5) * expdec(n, .09)
    inst = {'k': (kick, 1.0), 's': (snare, .65), 'h': (hat, .3), 'o': (ohat, .3), 't': (tom, .6)}
    for key, pat in pattern.items():
        smp, g = inst[key]
        for i, ch in enumerate(pat):
            if ch == 'x':
                i0 = int(i * step * SR)
                seg = smp[:L - i0]
                bar[i0:i0 + len(seg)] += seg * g
    return np.tile(bar, bars) * vol


def stereo(*tracks):
    """tracks: (señal, pan -1..1)"""
    n = max(len(t) for t, _ in tracks)
    L = np.zeros(n); R = np.zeros(n)
    for x, p in tracks:
        L[:len(x)] += x * (1 - max(0, p)); R[:len(x)] += x * (1 + min(0, p))
    return np.stack([L, R], 1)


def master(st, peak=0.85):
    st = softclip(st / (np.max(np.abs(st)) + 1e-9) * 1.2, 1.3)
    return st / np.max(np.abs(st)) * peak


def chords_to_arp(chords, steps_per_chord=16, pattern=(0, 1, 2, 1), dur=2):
    out = []
    for ch in chords:
        ns = ch.split('-')
        for i in range(steps_per_chord // dur):
            out.append((ns[pattern[i % len(pattern)] % len(ns)], dur))
    return out


def bass_octaves(roots, per=16):
    out = []
    for r in roots:
        lo = r; hi = r[:-1] + str(int(r[-1]) + 1)
        for i in range(per // 2):
            out.append((hi if i % 4 == 2 else lo, 2))
    return out


def song_fight():
    bpm = 150
    A = parse('A4:2 C5:2 E5:4 D5:2 C5:2 D5:2 E5:2 G5:4 E5:2 D5:2 B4:4 G4:4 '
              'A4:2 C5:2 F5:4 E5:2 D5:2 C5:2 A4:2 B4:4 D5:4 G5:4 F5:2 E5:2')
    A2 = parse('A4:2 C5:2 E5:4 D5:2 C5:2 D5:2 E5:2 G5:4 A5:2 G5:2 E5:4 D5:4 '
               'C5:2 D5:2 E5:4 F5:2 E5:2 D5:2 C5:2 B4:4 G#4:4 A4:8')
    B = parse('E5:6 D5:2 C5:4 B4:4 C5:2 D5:2 E5:4 G5:4 A5:4 F5:6 E5:2 D5:4 C5:4 B4:4 E5:4 G#5:8 '
              'A5:6 G5:2 F5:4 E5:4 F5:2 G5:2 A5:4 C6:4 B5:4 A5:4 G5:4 F5:4 E5:4 D5:4 E5:16')
    lead = A + A2 + B
    roots = ['A2', 'G2', 'F2', 'G2'] * 2 + ['F2', 'G2', 'A2', 'A2', 'F2', 'G2', 'E2', 'E2']
    chords = ['A3-C4-E4', 'G3-B3-D4', 'F3-A3-C4', 'G3-B3-D4'] * 2 + \
             ['F3-A3-C4', 'G3-B3-D4', 'A3-C4-E4', 'A3-C4-E4', 'F3-A3-C4', 'G3-B3-D4', 'E3-G#3-B3', 'E3-G#3-B3']
    bars = len(roots)
    lead_s = render_line(lead, bpm, 'square', .32, duty=.5, vib=.006, s=.7, detune=.003)
    harm_s = render_line([(n, d) for n, d in lead], bpm, 'square', .12, duty=.25, s=.5, octave=-1)
    bass_s = render_line(bass_octaves(roots), bpm, 'saw', .45, d=.08, s=.5)
    arp_s = render_line(chords_to_arp(chords, 16, (0, 1, 2, 1, 2, 1, 0, 2), 1), bpm, 'square', .1, duty=.125, s=.3)
    dr = drums({'k': 'x.....x.x.......', 's': '....x.......x..x', 'h': 'x.x.x.x.x.x.x.x.',
                'o': '..............x.'}, bpm, bars, .9)
    intro = drums({'k': 'x...x...x...x...', 's': '............xxxx', 'h': 'x.x.x.x.x.x.x.x.'}, bpm, 1, .9)
    body = stereo((lead_s, -0.15), (harm_s, 0.35), (bass_s, 0), (arp_s, 0.5), (dr, 0))
    return master(np.concatenate([stereo((intro, 0)), body]))


def song_menu():
    bpm = 132
    lead = parse('D5:4 A4:4 D5:2 E5:2 F5:4 E5:2 D5:2 C5:4 A4:8 '
                 'Bb4:4 C5:4 D5:2 F5:2 A5:4 G5:2 F5:2 E5:4 C5:8 '
                 'D5:4 A4:4 D5:2 E5:2 F5:4 G5:2 A5:2 Bb5:4 A5:4 G5:4 F5:4 '
                 'G5:4 F5:2 E5:2 F5:4 E5:2 C#5:2 D5:16')
    roots = ['D2', 'C2', 'Bb1', 'C2', 'D2', 'F2', 'Bb1', 'A1']
    chords = ['D3-F3-A3', 'C3-E3-G3', 'Bb2-D3-F3', 'C3-E3-G3', 'D3-F3-A3', 'F3-A3-C4', 'Bb2-D3-F3', 'A2-C#3-E3']
    lead_s = render_line(lead, bpm, 'square', .3, vib=.008, s=.75, detune=.004, a=.01)
    echo = at(lead_s * .35, 60 / bpm * .75)
    bass_s = render_line(bass_octaves(roots), bpm, 'saw', .42, s=.6)
    pad_s = sum(render_line([(c.split('-')[i], 16) for c in chords], bpm, 'saw', .07, a=.2, s=.9, r=.2)
                for i in range(3))
    arp = render_line(chords_to_arp(chords, 16, (0, 1, 2, 1), 1), bpm, 'square', .09, duty=.25, s=.3, octave=1)
    dr = drums({'k': 'x.......x.x.....', 's': '....x.......x...', 'h': 'x.x.x.x.x.x.x.x.'}, bpm, 8, .8)
    return master(stereo((lead_s, -.1), (echo, .4), (bass_s, 0), (pad_s, -.3), (arp, .3), (dr, 0)))


def song_select():
    bpm = 140
    lead = parse('C5:2 E5:2 G5:2 E5:2 A5:4 G5:4 F5:2 A5:2 G5:2 F5:2 E5:4 C5:4 '
                 'D5:2 F5:2 A5:2 F5:2 B5:4 A5:4 G5:2 F5:2 E5:2 D5:2 G5:8 '
                 'C5:2 E5:2 G5:2 E5:2 A5:4 G5:4 F5:2 A5:2 C6:2 A5:2 G5:4 E5:4 '
                 'F5:2 E5:2 D5:2 C5:2 D5:4 G4:4 C5:16')
    roots = ['C2', 'F2', 'D2', 'G2', 'C2', 'F2', 'G2', 'C2']
    chords = ['C4-E4-G4', 'F3-A3-C4', 'D4-F4-A4', 'G3-B3-D4', 'C4-E4-G4', 'F3-A3-C4', 'G3-B3-D4', 'C4-E4-G4']
    lead_s = render_line(lead, bpm, 'square', .28, duty=.25, vib=.005, s=.6)
    bass = []
    for r in roots:
        f5 = {'C2': 'G2', 'F2': 'C3', 'D2': 'A2', 'G2': 'D3'}[r]
        bass += [(r, 2), (None, 2), (f5, 2), (r, 2)] * 2
    bass_s = render_line(bass, bpm, 'tri', .55, s=.7)
    comp = render_line(chords_to_arp(chords, 16, (0, 1, 2, 1), 2), bpm, 'square', .1, duty=.5, s=.2, d=.05)
    dr = drums({'k': 'x...x...x...x...', 's': '....x.......x...', 'h': '..x...x...x...x.'}, bpm, 8, .75)
    return master(stereo((lead_s, -.2), (bass_s, 0), (comp, .35), (dr, 0)))


def song_victory():
    bpm = 120
    lead = parse('G4:2 C5:2 E5:2 G5:6 E5:2 G5:2 C6:12 -:4 A5:2 G5:2 F5:2 E5:2 D5:2 E5:2 F5:2 D5:2 '
                 'G5:4 F5:2 E5:2 D5:4 B4:4 C5:16')
    roots = ['C2', 'C2', 'F2', 'G2', 'C2']
    chords = ['C4-E4-G4', 'C4-E4-G4', 'F3-A3-C4', 'G3-B3-D4', 'C4-E4-G4']
    lead_s = render_line(lead, bpm, 'square', .33, vib=.01, s=.75, detune=.004)
    brass = render_line([(c.split('-')[0], 16) for c in chords], bpm, 'saw', .1, a=.05, s=.8)
    brass += render_line([(c.split('-')[2], 16) for c in chords], bpm, 'saw', .08, a=.05, s=.8)
    bass_s = render_line(bass_octaves(roots), bpm, 'saw', .4)
    dr = drums({'k': 'x.......x.......', 's': '....x.......x.xx', 'h': 'x.x.x.x.x.x.x.x.'}, bpm, 5, .8)
    return master(stereo((lead_s, 0), (brass, .3), (bass_s, 0), (dr, 0)))


def song_defeat():
    bpm = 78
    lead = parse('E5:4 D5:4 C5:4 B4:4 A4:8 G#4:8 F5:4 E5:4 D5:4 C5:4 B4:12 -:4 '
                 'C5:4 B4:4 A4:4 G4:4 F4:8 E4:8 F4:4 G#4:4 B4:4 D5:4 C5:4 B4:4 A4:8')
    roots = ['A1', 'E2', 'D2', 'E2', 'A1', 'D2', 'E2', 'A1']
    lead_s = render_line(lead, bpm, 'tri', .45, vib=.012, s=.8, a=.03)
    lead_s += render_line(lead, bpm, 'square', .08, duty=.125, s=.6)
    bass_s = render_line([(r, 16) for r in roots], bpm, 'saw', .25, a=.05, s=.8)
    pad_s = render_line([(r[:-1] + '3', 16) for r in roots], bpm, 'tri', .2, a=.2, s=.9)
    dr = drums({'k': 'x.......x.......', 's': '........x.......'}, bpm, 8, .5)
    return master(stereo((lead_s, 0), (bass_s, 0), (pad_s, .3), (reverb(lead_s, .4, .12) * .3, -.4), (dr, 0)), .7)


def song_intro():
    """Tema corto para la cinemática de apertura."""
    bpm = 150
    hits = parse('A2:4 -:4 A2:4 -:4 A2:2 A2:2 -:4 C3:4 D3:4 '
                 'A2:4 -:4 A2:4 -:4 E3:4 D3:4 C3:4 B2:4')
    riser_n = int(SR * 60 / bpm * 8)
    riser = sweep(200, 1600, 60 / bpm * 8, 'saw', 2) * np.linspace(0, 1, riser_n) * .25
    stab = render_line(hits, bpm, 'saw', .5, d=.1, s=.3, detune=.01)
    stab2 = render_line(hits, bpm, 'square', .3, d=.1, s=.3, octave=1)
    dr = drums({'k': 'x...x...x...x...', 's': '....x.......x...', 'h': 'x.x.x.x.x.x.x.x.'}, bpm, 2, .9)
    roll = drums({'k': 'x...x...x...x...', 's': 'x.x.x.x.xxxxxxxx', 't': 'x...x...x...x...'}, bpm, 2, .9)
    body = stereo((stab, -.2), (stab2, .2), (dr, 0))
    end = stereo((at(riser, 0), 0), (roll, 0))
    full = np.concatenate([body, end])
    # remate final
    n = int(SR * 2)
    fin = stereo((np.sin(2 * np.pi * freq('A2') * t_(2)) * expdec(n, .6) * .8, 0),
                 (osc('saw', freq('A3'), n) * expdec(n, .5) * .4, -.2),
                 (osc('saw', freq('E4'), n) * expdec(n, .5) * .3, .2))
    return master(np.concatenate([full, fin]))


def main():
    os.makedirs(SND, exist_ok=True); os.makedirs(MUS, exist_ok=True)
    CHAR_LINES['pantoja']['ultimate_3'] = '¡Colectivazo!'
    CHAR_LINES['parada']['ultimate_3'] = '¡Cien patadas!'
    CHAR_LINES['nehuen']['ultimate_3'] = '¡La Bombonera late!'
    CHAR_LINES['luciano']['ultimate_3'] = '¡Alto voltaje!'
    if '--voces' in sys.argv:          # sólo voces + sonidos nuevos (rápido)
        n = int(SR * .7)
        ray = norm(softclip(highpass(noise(n), 900) * expdec(n, .09) * 1.6
                            + sweep(1800, 90, .7, 'saw', .35) * expdec(n, .12) * .7, 3), .95)
        save('rayo', reverb(ray, .3, .06))
        for k, x in voices().items():
            save(k, x)
        return
    print('efectos...', flush=True)
    for k, x in sfx().items():
        save(k, x)
    print('voces...', flush=True)
    for k, x in voices().items():
        save(k, x)
    print('música...', flush=True)
    for name, fn in [('musica_menu', song_menu), ('musica_seleccion', song_select),
                     ('musica_combate', song_fight), ('musica_victoria', song_victory),
                     ('musica_derrota', song_defeat), ('musica_intro', song_intro)]:
        x = fn()
        save(name, x, MUS)
        print(' ', name, round(len(x) / SR, 1), 's', flush=True)


if __name__ == '__main__':
    main()
