# Documentación de sprites y animaciones

## Formato de los spritesheets

Cada animación de cada personaje es **una tira horizontal PNG con fondo transparente**:

`assets/characters/<personaje>/<personaje>_<animación>.png`

- Todos los cuadros miden **240 × 176 px** (resolución nativa pixel-art).
- El cuadro *i* se recorta en el rectángulo `x = i * 240, y = 0, ancho = 240, alto = 176`.
- El **ancla** (punto del suelo bajo la pelvis del personaje) está en **(112, 170)** de cada cuadro;
  el juego coloca ese punto sobre la posición del luchador.
- En el juego los sprites se dibujan a escala **x3** (vecino más cercano) → 720 × 528 px.
- Los personajes miran hacia la **derecha**; para mirar a la izquierda se espejan horizontalmente.
- `<personaje>_spritesheet_completo.png` reúne todas las animaciones (una fila por animación,
  en el orden de la tabla) como vista previa.
- `<personaje>_retrato.png` (72 × 72) es el retrato para menús y HUD.

### Metadatos (`<personaje>_meta.json`)

```json
{
  "frame_w": 240, "frame_h": 176, "anchor": [112, 170],
  "animations": {
    "golpe": {
      "file": "pantoja_golpe.png", "frames": 5,
      "dur": 3,            // ticks (a 60 fps) por cuadro
      "loop": false,
      "joints": [ {"f_ha": [x, y], "b_ha": ..., "f_an": ..., ...}, ... ],
      "bbox":   [ [x0, y0, x1, y1], ... ]   // caja del cuerpo por cuadro
    }
  }
}
```

`joints` guarda, para cada cuadro, la posición de manos (`f_ha`/`b_ha`), tobillos (`f_an`/`b_an`),
puntas de pie, codos, rodillas, cabeza, cuello y pelvis. El sistema de combate los usa para
ubicar las **hitboxes** exactamente donde está el puño o el pie en ese cuadro, y `bbox` para la
**hurtbox** del cuerpo.

## Cómo se generaron

1. `tools/rig.py` separa a cada luchador del fondo cuadriculado de la ilustración original
   (`assets/source/<personaje>.jpg`).
2. Define un esqueleto (pelvis, cuello, cabeza, hombros, codos, manos, caderas, rodillas, tobillos,
   puntas de pie) y asigna cada píxel a su hueso: torso, cabeza, brazo y antebrazo, muslo, pierna y pie
   de cada lado. Las zonas del torso tapadas por los brazos se rellenan (inpainting).
3. `tools/anim_defs.py` describe cada animación como poses clave (inclinación del torso, posición de
   manos y tobillos, rotación del cuerpo, squash & stretch, objetos como la guitarra de Nehuen).
4. Cada pose se resuelve con cinemática inversa, se compone a 4x, se reduce a la resolución nativa y
   se cuantiza a la paleta de 40 colores del personaje para conservar el estilo pixel-art.

Para regenerar: `python tools/build_sprites.py` (o `python tools/build_sprites.py nehuen` para uno solo).

## PANTOJA — El Marido De Parada

Altura nativa: 114 px · 32 animaciones · 228 cuadros

| Animación | Archivo | Cuadros | Ticks/cuadro | Bucle | Descripción |
|---|---|:-:|:-:|:-:|---|
| `idle` | `pantoja_idle.png` | 8 | 7 | sí | Posición de combate en reposo (respiración) |
| `caminar` | `pantoja_caminar.png` | 8 | 5 | sí | Caminar hacia adelante |
| `caminar_atras` | `pantoja_caminar_atras.png` | 8 | 6 | sí | Retroceder |
| `saltar` | `pantoja_saltar.png` | 7 | 6 | no | Salto vertical (impulso, ascenso, recogido, caída, aterrizaje) |
| `saltar_adelante` | `pantoja_saltar_adelante.png` | 8 | 6 | no | Salto hacia adelante con voltereta |
| `agacharse` | `pantoja_agacharse.png` | 3 | 3 | no | Agacharse (transición + posición) |
| `bloquear` | `pantoja_bloquear.png` | 3 | 3 | no | Defensa de pie |
| `bloquear_agachado` | `pantoja_bloquear_agachado.png` | 2 | 3 | no | Defensa agachado |
| `presentacion` | `pantoja_presentacion.png` | 12 | 6 | no | Animación de presentación |
| `golpe` | `pantoja_golpe.png` | 5 | 3 | no | Puñetazo rápido |
| `patada` | `pantoja_patada.png` | 6 | 3 | no | Patada rápida |
| `golpe_fuerte` | `pantoja_golpe_fuerte.png` | 7 | 4 | no | Golpe potente (cross con torsión) |
| `patada_fuerte` | `pantoja_patada_fuerte.png` | 8 | 4 | no | Patada alta potente |
| `golpe_agachado` | `pantoja_golpe_agachado.png` | 4 | 3 | no | Puñetazo agachado |
| `patada_agachado` | `pantoja_patada_agachado.png` | 6 | 4 | no | Barrida |
| `patada_aerea` | `pantoja_patada_aerea.png` | 4 | 4 | no | Patada en el aire |
| `recibir_golpe` | `pantoja_recibir_golpe.png` | 4 | 4 | no | Reacción al impacto |
| `caida` | `pantoja_caida.png` | 8 | 5 | no | Caída al suelo (derribo) |
| `levantarse` | `pantoja_levantarse.png` | 6 | 5 | no | Levantarse |
| `victoria` | `pantoja_victoria.png` | 10 | 7 | no | Celebración de victoria |
| `derrota` | `pantoja_derrota.png` | 8 | 8 | no | Animación de derrota |
| `especial_1` | `pantoja_especial_1.png` | 9 | 4 | no | Ataque especial 1 — **Panzazo** |
| `especial_2` | `pantoja_especial_2.png` | 9 | 5 | no | Ataque especial 2 — **Grito Metalero** |
| `ultimate_1` | `pantoja_ultimate_1.png` | 16 | 5 | no | Ultimate 1 — **Terremoto Pantoja** |
| `ultimate_2` | `pantoja_ultimate_2.png` | 18 | 4 | no | Ultimate 2 — **Lluvia De Cachetadas** |
| `ultimate_3` | `pantoja_ultimate_3.png` | 14 | 4 | no | Ultimate 3 — **Colectivazo** |
| `enamorado` | `pantoja_enamorado.png` | 4 | 10 | sí |  |
| `abrazo` | `pantoja_abrazo.png` | 4 | 8 | no |  |
| `saludo` | `pantoja_saludo.png` | 7 | 7 | no |  |
| `provocar` | `pantoja_provocar.png` | 4 | 6 | sí |  |
| `enojado` | `pantoja_enojado.png` | 4 | 3 | sí |  |
| `confundido` | `pantoja_confundido.png` | 4 | 9 | no |  |

## PARADA — El Besa Perro

Altura nativa: 126 px · 32 animaciones · 235 cuadros

| Animación | Archivo | Cuadros | Ticks/cuadro | Bucle | Descripción |
|---|---|:-:|:-:|:-:|---|
| `idle` | `parada_idle.png` | 8 | 7 | sí | Posición de combate en reposo (respiración) |
| `caminar` | `parada_caminar.png` | 8 | 5 | sí | Caminar hacia adelante |
| `caminar_atras` | `parada_caminar_atras.png` | 8 | 6 | sí | Retroceder |
| `saltar` | `parada_saltar.png` | 7 | 6 | no | Salto vertical (impulso, ascenso, recogido, caída, aterrizaje) |
| `saltar_adelante` | `parada_saltar_adelante.png` | 8 | 6 | no | Salto hacia adelante con voltereta |
| `agacharse` | `parada_agacharse.png` | 3 | 3 | no | Agacharse (transición + posición) |
| `bloquear` | `parada_bloquear.png` | 3 | 3 | no | Defensa de pie |
| `bloquear_agachado` | `parada_bloquear_agachado.png` | 2 | 3 | no | Defensa agachado |
| `presentacion` | `parada_presentacion.png` | 12 | 6 | no | Animación de presentación |
| `golpe` | `parada_golpe.png` | 5 | 3 | no | Puñetazo rápido |
| `patada` | `parada_patada.png` | 6 | 3 | no | Patada rápida |
| `golpe_fuerte` | `parada_golpe_fuerte.png` | 7 | 4 | no | Golpe potente (cross con torsión) |
| `patada_fuerte` | `parada_patada_fuerte.png` | 8 | 4 | no | Patada alta potente |
| `golpe_agachado` | `parada_golpe_agachado.png` | 4 | 3 | no | Puñetazo agachado |
| `patada_agachado` | `parada_patada_agachado.png` | 6 | 4 | no | Barrida |
| `patada_aerea` | `parada_patada_aerea.png` | 4 | 4 | no | Patada en el aire |
| `recibir_golpe` | `parada_recibir_golpe.png` | 4 | 4 | no | Reacción al impacto |
| `caida` | `parada_caida.png` | 8 | 5 | no | Caída al suelo (derribo) |
| `levantarse` | `parada_levantarse.png` | 6 | 5 | no | Levantarse |
| `victoria` | `parada_victoria.png` | 10 | 7 | no | Celebración de victoria |
| `derrota` | `parada_derrota.png` | 8 | 8 | no | Animación de derrota |
| `especial_1` | `parada_especial_1.png` | 8 | 4 | no | Ataque especial 1 — **Ráfaga Esmeralda** |
| `especial_2` | `parada_especial_2.png` | 10 | 4 | no | Ataque especial 2 — **Patada Huracán** |
| `ultimate_1` | `parada_ultimate_1.png` | 21 | 3 | no | Ultimate 1 — **Mil Piñas** |
| `ultimate_2` | `parada_ultimate_2.png` | 16 | 4 | no | Ultimate 2 — **Tornado Verde** |
| `ultimate_3` | `parada_ultimate_3.png` | 18 | 3 | no | Ultimate 3 — **Cien Patadas** |
| `enamorado` | `parada_enamorado.png` | 4 | 10 | sí |  |
| `abrazo` | `parada_abrazo.png` | 4 | 8 | no |  |
| `saludo` | `parada_saludo.png` | 7 | 7 | no |  |
| `provocar` | `parada_provocar.png` | 4 | 6 | sí |  |
| `enojado` | `parada_enojado.png` | 4 | 3 | sí |  |
| `confundido` | `parada_confundido.png` | 4 | 9 | no |  |

## NEHUEN — El Bostero

Altura nativa: 128 px · 32 animaciones · 223 cuadros

| Animación | Archivo | Cuadros | Ticks/cuadro | Bucle | Descripción |
|---|---|:-:|:-:|:-:|---|
| `idle` | `nehuen_idle.png` | 8 | 7 | sí | Posición de combate en reposo (respiración) |
| `caminar` | `nehuen_caminar.png` | 8 | 5 | sí | Caminar hacia adelante |
| `caminar_atras` | `nehuen_caminar_atras.png` | 8 | 6 | sí | Retroceder |
| `saltar` | `nehuen_saltar.png` | 7 | 6 | no | Salto vertical (impulso, ascenso, recogido, caída, aterrizaje) |
| `saltar_adelante` | `nehuen_saltar_adelante.png` | 8 | 6 | no | Salto hacia adelante con voltereta |
| `agacharse` | `nehuen_agacharse.png` | 3 | 3 | no | Agacharse (transición + posición) |
| `bloquear` | `nehuen_bloquear.png` | 3 | 3 | no | Defensa de pie |
| `bloquear_agachado` | `nehuen_bloquear_agachado.png` | 2 | 3 | no | Defensa agachado |
| `presentacion` | `nehuen_presentacion.png` | 12 | 6 | no | Animación de presentación |
| `golpe` | `nehuen_golpe.png` | 5 | 3 | no | Puñetazo rápido |
| `patada` | `nehuen_patada.png` | 6 | 3 | no | Patada rápida |
| `golpe_fuerte` | `nehuen_golpe_fuerte.png` | 7 | 4 | no | Golpe potente (cross con torsión) |
| `patada_fuerte` | `nehuen_patada_fuerte.png` | 8 | 4 | no | Patada alta potente |
| `golpe_agachado` | `nehuen_golpe_agachado.png` | 4 | 3 | no | Puñetazo agachado |
| `patada_agachado` | `nehuen_patada_agachado.png` | 6 | 4 | no | Barrida |
| `patada_aerea` | `nehuen_patada_aerea.png` | 4 | 4 | no | Patada en el aire |
| `recibir_golpe` | `nehuen_recibir_golpe.png` | 4 | 4 | no | Reacción al impacto |
| `caida` | `nehuen_caida.png` | 8 | 5 | no | Caída al suelo (derribo) |
| `levantarse` | `nehuen_levantarse.png` | 6 | 5 | no | Levantarse |
| `victoria` | `nehuen_victoria.png` | 10 | 7 | no | Celebración de victoria |
| `derrota` | `nehuen_derrota.png` | 8 | 8 | no | Animación de derrota |
| `especial_1` | `nehuen_especial_1.png` | 8 | 5 | no | Ataque especial 1 — **Acorde Sónico** |
| `especial_2` | `nehuen_especial_2.png` | 9 | 4 | no | Ataque especial 2 — **Patada Del Piluso** |
| `ultimate_1` | `nehuen_ultimate_1.png` | 16 | 4 | no | Ultimate 1 — **Solo Infinito** |
| `ultimate_2` | `nehuen_ultimate_2.png` | 15 | 5 | no | Ultimate 2 — **Meteoro Piluso** |
| `ultimate_3` | `nehuen_ultimate_3.png` | 13 | 5 | no | Ultimate 3 — **La Bombonera Late** |
| `enamorado` | `nehuen_enamorado.png` | 4 | 10 | sí |  |
| `abrazo` | `nehuen_abrazo.png` | 4 | 8 | no |  |
| `saludo` | `nehuen_saludo.png` | 7 | 7 | no |  |
| `provocar` | `nehuen_provocar.png` | 4 | 6 | sí |  |
| `enojado` | `nehuen_enojado.png` | 4 | 3 | sí |  |
| `confundido` | `nehuen_confundido.png` | 4 | 9 | no |  |

## LUCIANO — Voltio

Altura nativa: 126 px · 32 animaciones · 226 cuadros

| Animación | Archivo | Cuadros | Ticks/cuadro | Bucle | Descripción |
|---|---|:-:|:-:|:-:|---|
| `idle` | `luciano_idle.png` | 8 | 7 | sí | Posición de combate en reposo (respiración) |
| `caminar` | `luciano_caminar.png` | 8 | 5 | sí | Caminar hacia adelante |
| `caminar_atras` | `luciano_caminar_atras.png` | 8 | 6 | sí | Retroceder |
| `saltar` | `luciano_saltar.png` | 7 | 6 | no | Salto vertical (impulso, ascenso, recogido, caída, aterrizaje) |
| `saltar_adelante` | `luciano_saltar_adelante.png` | 8 | 6 | no | Salto hacia adelante con voltereta |
| `agacharse` | `luciano_agacharse.png` | 3 | 3 | no | Agacharse (transición + posición) |
| `bloquear` | `luciano_bloquear.png` | 3 | 3 | no | Defensa de pie |
| `bloquear_agachado` | `luciano_bloquear_agachado.png` | 2 | 3 | no | Defensa agachado |
| `presentacion` | `luciano_presentacion.png` | 12 | 6 | no | Animación de presentación |
| `golpe` | `luciano_golpe.png` | 5 | 3 | no | Puñetazo rápido |
| `patada` | `luciano_patada.png` | 6 | 3 | no | Patada rápida |
| `golpe_fuerte` | `luciano_golpe_fuerte.png` | 7 | 4 | no | Golpe potente (cross con torsión) |
| `patada_fuerte` | `luciano_patada_fuerte.png` | 8 | 4 | no | Patada alta potente |
| `golpe_agachado` | `luciano_golpe_agachado.png` | 4 | 3 | no | Puñetazo agachado |
| `patada_agachado` | `luciano_patada_agachado.png` | 6 | 4 | no | Barrida |
| `patada_aerea` | `luciano_patada_aerea.png` | 4 | 4 | no | Patada en el aire |
| `recibir_golpe` | `luciano_recibir_golpe.png` | 4 | 4 | no | Reacción al impacto |
| `caida` | `luciano_caida.png` | 8 | 5 | no | Caída al suelo (derribo) |
| `levantarse` | `luciano_levantarse.png` | 6 | 5 | no | Levantarse |
| `victoria` | `luciano_victoria.png` | 10 | 7 | no | Celebración de victoria |
| `derrota` | `luciano_derrota.png` | 8 | 8 | no | Animación de derrota |
| `especial_1` | `luciano_especial_1.png` | 8 | 4 | no | Ataque especial 1 — **Credencial Voladora** |
| `especial_2` | `luciano_especial_2.png` | 9 | 4 | no | Ataque especial 2 — **Gancho Preceptor** |
| `ultimate_1` | `luciano_ultimate_1.png` | 18 | 4 | no | Ultimate 1 — **Combo Disciplinario** |
| `ultimate_2` | `luciano_ultimate_2.png` | 16 | 5 | no | Ultimate 2 — **Amonestación Final** |
| `ultimate_3` | `luciano_ultimate_3.png` | 13 | 5 | no | Ultimate 3 — **Alto Voltaje** |
| `enamorado` | `luciano_enamorado.png` | 4 | 10 | sí |  |
| `abrazo` | `luciano_abrazo.png` | 4 | 8 | no |  |
| `saludo` | `luciano_saludo.png` | 7 | 7 | no |  |
| `provocar` | `luciano_provocar.png` | 4 | 6 | sí |  |
| `enojado` | `luciano_enojado.png` | 4 | 3 | sí |  |
| `confundido` | `luciano_confundido.png` | 4 | 9 | no |  |

## NICO — El Jefe De Arcetech

Altura nativa: 126 px · 31 animaciones · 201 cuadros

| Animación | Archivo | Cuadros | Ticks/cuadro | Bucle | Descripción |
|---|---|:-:|:-:|:-:|---|
| `idle` | `nico_idle.png` | 8 | 7 | sí | Posición de combate en reposo (respiración) |
| `caminar` | `nico_caminar.png` | 8 | 5 | sí | Caminar hacia adelante |
| `caminar_atras` | `nico_caminar_atras.png` | 8 | 6 | sí | Retroceder |
| `saltar` | `nico_saltar.png` | 7 | 6 | no | Salto vertical (impulso, ascenso, recogido, caída, aterrizaje) |
| `saltar_adelante` | `nico_saltar_adelante.png` | 8 | 6 | no | Salto hacia adelante con voltereta |
| `agacharse` | `nico_agacharse.png` | 3 | 3 | no | Agacharse (transición + posición) |
| `bloquear` | `nico_bloquear.png` | 3 | 3 | no | Defensa de pie |
| `bloquear_agachado` | `nico_bloquear_agachado.png` | 2 | 3 | no | Defensa agachado |
| `presentacion` | `nico_presentacion.png` | 12 | 6 | no | Animación de presentación |
| `golpe` | `nico_golpe.png` | 5 | 3 | no | Puñetazo rápido |
| `patada` | `nico_patada.png` | 6 | 3 | no | Patada rápida |
| `golpe_fuerte` | `nico_golpe_fuerte.png` | 7 | 4 | no | Golpe potente (cross con torsión) |
| `patada_fuerte` | `nico_patada_fuerte.png` | 8 | 4 | no | Patada alta potente |
| `golpe_agachado` | `nico_golpe_agachado.png` | 4 | 3 | no | Puñetazo agachado |
| `patada_agachado` | `nico_patada_agachado.png` | 6 | 4 | no | Barrida |
| `patada_aerea` | `nico_patada_aerea.png` | 4 | 4 | no | Patada en el aire |
| `recibir_golpe` | `nico_recibir_golpe.png` | 4 | 4 | no | Reacción al impacto |
| `caida` | `nico_caida.png` | 8 | 5 | no | Caída al suelo (derribo) |
| `levantarse` | `nico_levantarse.png` | 6 | 5 | no | Levantarse |
| `victoria` | `nico_victoria.png` | 10 | 7 | no | Celebración de victoria |
| `derrota` | `nico_derrota.png` | 8 | 8 | no | Animación de derrota |
| `especial_1` | `nico_especial_1.png` | 7 | 4 | no | Ataque especial 1 — **Hoja De Arce** |
| `especial_2` | `nico_especial_2.png` | 8 | 4 | no | Ataque especial 2 — **Reinicio Forzado** |
| `ultimate_1` | `nico_ultimate_1.png` | 10 | 5 | no | Ultimate 1 — **Pantallazo Azul** |
| `ultimate_2` | `nico_ultimate_2.png` | 14 | 5 | no | Ultimate 2 — **Despido Inmediato** |
| `enamorado` | `nico_enamorado.png` | 4 | 10 | sí |  |
| `abrazo` | `nico_abrazo.png` | 4 | 8 | no |  |
| `saludo` | `nico_saludo.png` | 7 | 7 | no |  |
| `provocar` | `nico_provocar.png` | 4 | 6 | sí |  |
| `enojado` | `nico_enojado.png` | 4 | 3 | sí |  |
| `confundido` | `nico_confundido.png` | 4 | 9 | no |  |

## Efectos especiales (`assets/effects/`)

Mismo formato: tira horizontal, cuadros de tamaño uniforme (indicado abajo), escala x3 en el juego.

| Efecto | Archivo | Cuadro | Cuadros | Uso |
|---|---|:-:|:-:|---|
| `rayo` | `rayo.png` | 48×176 | 4 |  |
| `hoja` | `hoja.png` | 30×30 | 6 |  |
| `chispa_golpe` | `chispa_golpe.png` | 40×40 | 7 | Impacto de golpe rápido |
| `chispa_fuerte` | `chispa_fuerte.png` | 64×64 | 8 | Impacto de golpe fuerte / especial |
| `chispa_bloqueo` | `chispa_bloqueo.png` | 36×36 | 6 | Golpe bloqueado |
| `polvo` | `polvo.png` | 48×24 | 7 | Polvo al caer, aterrizar o embestir |
| `onda_metal` | `onda_metal.png` | 56×48 | 4 | Proyectil «Grito metalero» (Pantoja) |
| `notas` | `notas.png` | 48×36 | 4 | Proyectil «Acorde sónico» (Nehuen) |
| `rayo_notas` | `rayo_notas.png` | 96×64 | 4 | Rayo de la ultimate «Solo infinito» (Nehuen) |
| `credencial` | `credencial.png` | 28×28 | 8 | Proyectil «Credencial voladora» (Luciano) |
| `onda_choque` | `onda_choque.png` | 140×48 | 6 | Ondas del «Terremoto Pantoja» |
| `explosion` | `explosion.png` | 96×96 | 11 | Explosiones (ultimates, choque de proyectiles) |
| `aura` | `aura.png` | 80×130 | 6 | Aura de energía durante las ultimates (se tiñe con el color del personaje) |
| `tornado` | `tornado.png` | 64×110 | 6 | «Tornado verde» (Parada) |
| `puno_energia` | `puno_energia.png` | 90×64 | 4 | Puño de energía de «Amonestación final» (Luciano) |
| `estela` | `estela.png` | 48×24 | 3 | Estela de velocidad |
| `destello` | `destello.png` | 64×64 | 1 | Destello |
| `codigo` | `codigo.png` | 44×30 | 4 |  |
| `gato` | `gato.png` | 40×28 | 4 |  |
| `gatos` | `gatos.png` | 48×176 | 4 |  |
| `paloma` | `paloma.png` | 36×28 | 4 |  |
| `avion` | `avion.png` | 32×20 | 4 |  |
| `pelota` | `pelota.png` | 26×26 | 4 |  |
| `pelota_gigante` | `pelota_gigante.png` | 72×72 | 4 |  |
| `rayo_ia` | `rayo_ia.png` | 96×64 | 4 |  |
| `lluvia_codigo` | `lluvia_codigo.png` | 48×176 | 4 |  |
| `numeros` | `numeros.png` | 48×176 | 4 |  |
| `luz` | `luz.png` | 48×176 | 4 |  |
| `papelitos` | `papelitos.png` | 96×176 | 4 |  |
| `corazon` | `corazon.png` | 24×24 | 4 |  |
| `enojo` | `enojo.png` | 24×24 | 4 |  |
| `brillo` | `brillo.png` | 32×32 | 4 |  |

## Interfaz (`assets/interface/`)

- `logo.png`: logotipo original «IES 10 FIGHTER».
- `icono.png`: ícono de la ventana.
- `vs.png`: gráfico «VS».
