"""Genera documentation/sprites_documentation.md a partir de los metadatos reales."""
import os, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CH = ['pantoja', 'parada', 'nehuen', 'luciano', 'nico']
DESC = {
    'idle': 'Posición de combate en reposo (respiración)', 'caminar': 'Caminar hacia adelante',
    'caminar_atras': 'Retroceder', 'saltar': 'Salto vertical (impulso, ascenso, recogido, caída, aterrizaje)',
    'saltar_adelante': 'Salto hacia adelante con voltereta', 'agacharse': 'Agacharse (transición + posición)',
    'bloquear': 'Defensa de pie', 'bloquear_agachado': 'Defensa agachado', 'presentacion': 'Animación de presentación',
    'golpe': 'Puñetazo rápido', 'patada': 'Patada rápida', 'golpe_fuerte': 'Golpe potente (cross con torsión)',
    'patada_fuerte': 'Patada alta potente', 'golpe_agachado': 'Puñetazo agachado', 'patada_agachado': 'Barrida',
    'patada_aerea': 'Patada en el aire', 'recibir_golpe': 'Reacción al impacto', 'caida': 'Caída al suelo (derribo)',
    'levantarse': 'Levantarse', 'victoria': 'Celebración de victoria', 'derrota': 'Animación de derrota',
    'especial_1': 'Ataque especial 1', 'especial_2': 'Ataque especial 2', 'ultimate_1': 'Ultimate 1', 'ultimate_2': 'Ultimate 2', 'ultimate_3': 'Ultimate 3',
}


def main():
    import sys
    sys.path.insert(0, ROOT)
    from game.characters_data import CHARACTERS
    L = ['# Documentación de sprites y animaciones', '',
         '## Formato de los spritesheets', '',
         'Cada animación de cada personaje es **una tira horizontal PNG con fondo transparente**:',
         '', '`assets/characters/<personaje>/<personaje>_<animación>.png`', '',
         '- Todos los cuadros miden **240 × 176 px** (resolución nativa pixel-art).',
         '- El cuadro *i* se recorta en el rectángulo `x = i * 240, y = 0, ancho = 240, alto = 176`.',
         '- El **ancla** (punto del suelo bajo la pelvis del personaje) está en **(112, 170)** de cada cuadro;',
         '  el juego coloca ese punto sobre la posición del luchador.',
         '- En el juego los sprites se dibujan a escala **x3** (vecino más cercano) → 720 × 528 px.',
         '- Los personajes miran hacia la **derecha**; para mirar a la izquierda se espejan horizontalmente.',
         '- `<personaje>_spritesheet_completo.png` reúne todas las animaciones (una fila por animación,',
         '  en el orden de la tabla) como vista previa.',
         '- `<personaje>_retrato.png` (72 × 72) es el retrato para menús y HUD.', '',
         '### Metadatos (`<personaje>_meta.json`)', '',
         '```json', '{', '  "frame_w": 240, "frame_h": 176, "anchor": [112, 170],', '  "animations": {',
         '    "golpe": {', '      "file": "pantoja_golpe.png", "frames": 5,',
         '      "dur": 3,            // ticks (a 60 fps) por cuadro',
         '      "loop": false,', '      "joints": [ {"f_ha": [x, y], "b_ha": ..., "f_an": ..., ...}, ... ],',
         '      "bbox":   [ [x0, y0, x1, y1], ... ]   // caja del cuerpo por cuadro', '    }', '  }', '}', '```', '',
         '`joints` guarda, para cada cuadro, la posición de manos (`f_ha`/`b_ha`), tobillos (`f_an`/`b_an`),',
         'puntas de pie, codos, rodillas, cabeza, cuello y pelvis. El sistema de combate los usa para',
         'ubicar las **hitboxes** exactamente donde está el puño o el pie en ese cuadro, y `bbox` para la',
         '**hurtbox** del cuerpo.', '',
         '## Cómo se generaron', '',
         '1. `tools/rig.py` separa a cada luchador del fondo cuadriculado de la ilustración original',
         '   (`assets/source/<personaje>.jpg`).',
         '2. Define un esqueleto (pelvis, cuello, cabeza, hombros, codos, manos, caderas, rodillas, tobillos,',
         '   puntas de pie) y asigna cada píxel a su hueso: torso, cabeza, brazo y antebrazo, muslo, pierna y pie',
         '   de cada lado. Las zonas del torso tapadas por los brazos se rellenan (inpainting).',
         '3. `tools/anim_defs.py` describe cada animación como poses clave (inclinación del torso, posición de',
         '   manos y tobillos, rotación del cuerpo, squash & stretch, objetos como la guitarra de Nehuen).',
         '4. Cada pose se resuelve con cinemática inversa, se compone a 4x, se reduce a la resolución nativa y',
         '   se cuantiza a la paleta de 40 colores del personaje para conservar el estilo pixel-art.', '',
         'Para regenerar: `python tools/build_sprites.py` (o `python tools/build_sprites.py nehuen` para uno solo).', '']
    for c in CH:
        meta = json.load(open(os.path.join(ROOT, 'assets', 'characters', c, f'{c}_meta.json')))
        d = CHARACTERS[c]
        total = sum(a['frames'] for a in meta['animations'].values())
        L += [f'## {d["display"]} — {d["title"].title()}', '',
              f'Altura nativa: {meta["height"]} px · {len(meta["animations"])} animaciones · {total} cuadros', '',
              '| Animación | Archivo | Cuadros | Ticks/cuadro | Bucle | Descripción |', '|---|---|:-:|:-:|:-:|---|']
        for an, a in meta['animations'].items():
            desc = DESC.get(an, '')
            if an in d['moves']:
                desc += f' — **{d["moves"][an]["name"].title()}**'
            L.append(f'| `{an}` | `{a["file"]}` | {a["frames"]} | {a["dur"]} | {"sí" if a["loop"] else "no"} | {desc} |')
        L.append('')
    fx = json.load(open(os.path.join(ROOT, 'assets', 'effects', 'effects_meta.json')))
    L += ['## Efectos especiales (`assets/effects/`)', '',
          'Mismo formato: tira horizontal, cuadros de tamaño uniforme (indicado abajo), escala x3 en el juego.', '',
          '| Efecto | Archivo | Cuadro | Cuadros | Uso |', '|---|---|:-:|:-:|---|']
    use = {'chispa_golpe': 'Impacto de golpe rápido', 'chispa_fuerte': 'Impacto de golpe fuerte / especial',
           'chispa_bloqueo': 'Golpe bloqueado', 'polvo': 'Polvo al caer, aterrizar o embestir',
           'onda_metal': 'Proyectil «Grito metalero» (Pantoja)', 'notas': 'Proyectil «Acorde sónico» (Nehuen)',
           'rayo_notas': 'Rayo de la ultimate «Solo infinito» (Nehuen)', 'credencial': 'Proyectil «Credencial voladora» (Luciano)',
           'onda_choque': 'Ondas del «Terremoto Pantoja»', 'explosion': 'Explosiones (ultimates, choque de proyectiles)',
           'aura': 'Aura de energía durante las ultimates (se tiñe con el color del personaje)',
           'tornado': '«Tornado verde» (Parada)', 'puno_energia': 'Puño de energía de «Amonestación final» (Luciano)',
           'estela': 'Estela de velocidad', 'destello': 'Destello'}
    for k, m in fx.items():
        L.append(f'| `{k}` | `{m["file"]}` | {m["w"]}×{m["h"]} | {m["frames"]} | {use.get(k, "")} |')
    L += ['', '## Interfaz (`assets/interface/`)', '', '- `logo.png`: logotipo original «IES 10 FIGHTER».',
          '- `icono.png`: ícono de la ventana.', '- `vs.png`: gráfico «VS».', '']
    open(os.path.join(ROOT, 'documentation', 'sprites_documentation.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('ok', len(L))


if __name__ == '__main__':
    main()
