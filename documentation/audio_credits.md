# Créditos y licencias de audio

## Resumen

Todo el audio de **IES 10 FIGHTER** es **original** y fue generado por el script
`tools/build_audio.py` (síntesis digital con NumPy/SciPy). No se descargó ni se extrajo
ningún sonido ni música de terceros.

> **Nota honesta:** el pedido original sugería buscar sonidos en Freesound, OpenGameArt,
> Pixabay y Kenney. El entorno donde se desarrolló el juego tenía **bloqueado el acceso a
> esos sitios**, así que se optó por sintetizar todo desde cero. Si querés usar sonidos
> de esas bibliotecas, descargalos, verificá su licencia y guardalos en `assets/sounds/` o
> `assets/music/` con **el mismo nombre de archivo** que el que reemplazan; el juego los
> carga automáticamente (acepta `.ogg` y `.wav`). Anotá el autor y la licencia en este archivo.

| Recurso | Autor / origen | Licencia |
|---|---|---|
| Efectos de sonido (`assets/sounds/*.ogg`, salvo voces) | Síntesis original, `tools/build_audio.py` | CC0 / dominio público (obra propia del proyecto) |
| Música (`assets/music/*.ogg`) | Composiciones chiptune originales, `tools/build_audio.py` | CC0 / dominio público (obra propia del proyecto) |
| Voces del locutor y de los personajes (`loc_*`, `*_voz_*`) | Generadas con **eSpeak NG** (motor de síntesis de voz libre) a partir de textos propios, con efectos | El audio generado es del proyecto; eSpeak NG se distribuye bajo GPL v3 pero sólo se usó como herramienta, no se incluye en el juego |
| Fuente *Press Start 2P* (`assets/fonts/`) | CodeMan38 (cody@zone38.net) | SIL Open Font License 1.1 (ver `OFL_PressStart2P.txt`) |
| Ilustraciones de personajes y escenario (`assets/source/`, `assets/backgrounds/`) | Provistas por el autor del proyecto | — |

## Música

| Archivo | Uso | Duración del bucle |
|---|---|---|
| `musica_combate.ogg` | Combates (bucle) | 27.6 s |
| `musica_derrota.ogg` | Pantalla de derrota (bucle) | 25.0 s |
| `musica_intro.ogg` | Cinemática de apertura | 11.6 s |
| `musica_menu.ogg` | Menú principal y opciones (bucle) | 15.3 s |
| `musica_seleccion.ogg` | Selección de personajes, galería y arcade (bucle) | 13.7 s |
| `musica_victoria.ogg` | Pantalla de victoria (bucle) | 10.0 s |

## Efectos de sonido

| Archivo | Uso |
|---|---|
| `aire_debil.ogg` | Silbido de golpe rápido |
| `aire_fuerte.ogg` | Silbido de golpe fuerte |
| `aterrizaje.ogg` | Aterrizaje |
| `bloqueo.ogg` | Bloqueo |
| `cachetada.ogg` | Cachetada (ultimate de Pantoja) |
| `caida_suelo.ogg` | Impacto contra el suelo |
| `carga.ogg` | Carga de energía |
| `combo.ogg` | Combo |
| `credencial.ogg` | Credencial girando (especial de Luciano) |
| `dash.ogg` | Embestida veloz |
| `energia.ogg` | Pulso de energía |
| `explosion.ogg` | Explosión |
| `golpe_debil.ogg` | Puñetazo / golpe rápido |
| `golpe_fuerte.ogg` | Golpe potente |
| `gong.ogg` | Inicio de ronda |
| `guitarra_acorde.ogg` | Acorde de guitarra eléctrica (Karplus-Strong) |
| `guitarra_solo.ogg` | Riff de guitarra (ultimate de Nehuen) |
| `ko_impacto.ogg` | K.O. / fin de ronda |
| `menu_atras.ogg` | Volver / cancelar |
| `menu_mover.ogg` | Navegación del menú |
| `menu_ok.ogg` | Confirmar en menú |
| `moneda.ogg` | Crédito / inicio |
| `onda_metal.ogg` | Grito metalero (especial de Pantoja) |
| `patada_debil.ogg` | Patada rápida |
| `patada_fuerte.ogg` | Patada potente |
| `proyectil.ogg` | Disparo de proyectil |
| `publico.ogg` | Público del aula |
| `salto.ogg` | Salto |
| `seleccion.ogg` | Selección de personaje |
| `terremoto.ogg` | Terremoto (ultimate de Pantoja) |
| `tic.ogg` | Cuenta regresiva del reloj |
| `ultimate_activar.ogg` | Activación de ultimate (super flash) |

## Voces

| Archivo | Contenido |
|---|---|
| `loc_continuar.ogg` | Locutor: continuar |
| `loc_elegi.ogg` | Locutor: elegi |
| `loc_empate.ogg` | Locutor: empate |
| `loc_fin.ogg` | Locutor: fin |
| `loc_gana.ogg` | Locutor: gana |
| `loc_ko.ogg` | Locutor: ko |
| `loc_luciano.ogg` | Locutor: luciano |
| `loc_luciano_gana.ogg` | Locutor: luciano gana |
| `loc_nehuen.ogg` | Locutor: nehuen |
| `loc_nehuen_gana.ogg` | Locutor: nehuen gana |
| `loc_nuevo_retador.ogg` | Locutor: nuevo retador |
| `loc_pantoja.ogg` | Locutor: pantoja |
| `loc_pantoja_gana.ogg` | Locutor: pantoja gana |
| `loc_parada.ogg` | Locutor: parada |
| `loc_parada_gana.ogg` | Locutor: parada gana |
| `loc_pelea.ogg` | Locutor: pelea |
| `loc_perfecto.ogg` | Locutor: perfecto |
| `loc_ronda_1.ogg` | Locutor: ronda 1 |
| `loc_ronda_2.ogg` | Locutor: ronda 2 |
| `loc_ronda_final.ogg` | Locutor: ronda final |
| `loc_tiempo.ogg` | Locutor: tiempo |
| `loc_titulo.ogg` | Locutor: titulo |
| `luciano_voz_dolor_1.ogg` | Luciano: dolor 1 |
| `luciano_voz_dolor_2.ogg` | Luciano: dolor 2 |
| `luciano_voz_especial_1.ogg` | Luciano: especial 1 |
| `luciano_voz_especial_2.ogg` | Luciano: especial 2 |
| `luciano_voz_grito_1.ogg` | Luciano: grito 1 |
| `luciano_voz_grito_2.ogg` | Luciano: grito 2 |
| `luciano_voz_grito_3.ogg` | Luciano: grito 3 |
| `luciano_voz_ko.ogg` | Luciano: ko |
| `luciano_voz_ultimate_1.ogg` | Luciano: ultimate 1 |
| `luciano_voz_ultimate_2.ogg` | Luciano: ultimate 2 |
| `luciano_voz_victoria.ogg` | Luciano: victoria |
| `nehuen_voz_dolor_1.ogg` | Nehuen: dolor 1 |
| `nehuen_voz_dolor_2.ogg` | Nehuen: dolor 2 |
| `nehuen_voz_especial_1.ogg` | Nehuen: especial 1 |
| `nehuen_voz_especial_2.ogg` | Nehuen: especial 2 |
| `nehuen_voz_grito_1.ogg` | Nehuen: grito 1 |
| `nehuen_voz_grito_2.ogg` | Nehuen: grito 2 |
| `nehuen_voz_grito_3.ogg` | Nehuen: grito 3 |
| `nehuen_voz_ko.ogg` | Nehuen: ko |
| `nehuen_voz_ultimate_1.ogg` | Nehuen: ultimate 1 |
| `nehuen_voz_ultimate_2.ogg` | Nehuen: ultimate 2 |
| `nehuen_voz_victoria.ogg` | Nehuen: victoria |
| `pantoja_voz_dolor_1.ogg` | Pantoja: dolor 1 |
| `pantoja_voz_dolor_2.ogg` | Pantoja: dolor 2 |
| `pantoja_voz_especial_1.ogg` | Pantoja: especial 1 |
| `pantoja_voz_especial_2.ogg` | Pantoja: especial 2 |
| `pantoja_voz_grito_1.ogg` | Pantoja: grito 1 |
| `pantoja_voz_grito_2.ogg` | Pantoja: grito 2 |
| `pantoja_voz_grito_3.ogg` | Pantoja: grito 3 |
| `pantoja_voz_ko.ogg` | Pantoja: ko |
| `pantoja_voz_ultimate_1.ogg` | Pantoja: ultimate 1 |
| `pantoja_voz_ultimate_2.ogg` | Pantoja: ultimate 2 |
| `pantoja_voz_victoria.ogg` | Pantoja: victoria |
| `parada_voz_dolor_1.ogg` | Parada: dolor 1 |
| `parada_voz_dolor_2.ogg` | Parada: dolor 2 |
| `parada_voz_especial_1.ogg` | Parada: especial 1 |
| `parada_voz_especial_2.ogg` | Parada: especial 2 |
| `parada_voz_grito_1.ogg` | Parada: grito 1 |
| `parada_voz_grito_2.ogg` | Parada: grito 2 |
| `parada_voz_grito_3.ogg` | Parada: grito 3 |
| `parada_voz_ko.ogg` | Parada: ko |
| `parada_voz_ultimate_1.ogg` | Parada: ultimate 1 |
| `parada_voz_ultimate_2.ogg` | Parada: ultimate 2 |
| `parada_voz_victoria.ogg` | Parada: victoria |

## Versión 1.1

Se agregaron, generados con el mismo método (`python tools/build_audio.py --voces`): `rayo.ogg` (ultimate «Alto voltaje»), las voces `*_voz_ultimate_3.ogg` de Pantoja, Parada, Nehuen y Luciano, y todas las voces de **Nico** (`nico_voz_*.ogg`, `loc_nico.ogg`, `loc_nico_gana.ogg`).

La imagen `assets/backgrounds/plaza.png` y la ilustración `assets/source/nico.png` fueron provistas por el autor del proyecto.

## Versión 1.3

Generado con `python tools/build_audio_v2.py` (síntesis original, sin muestras de otros juegos):

- **Golpes nuevos** más contundentes estilo arcade de los 90: `golpe_debil`, `golpe_fuerte`, `patada_debil`, `patada_fuerte`.
- **Efectos nuevos**: `maullido` (gato de Facu), `aleteo` (paloma de Pedro), `campana` (onda zen), `tiza` (Emi),
  `hinchada` (Denis), `corazones`, `amistad`, `bronca` y `rival` (encuentros antes de pelear).
- **Voces** de Angel, Facu, Pedro, Emi y Denis (`<nombre>_voz_*.ogg`, `loc_<nombre>.ogg`, `loc_<nombre>_gana.ogg`)
  y las frases de los encuentros (`*_voz_amor`, `*_voz_abrazo`, `*_voz_saludo`, `*_voz_rival`, `*_voz_odio`).
- **Música** con síntesis FM de 2 operadores (sonido de placa arcade de 16 bits), composiciones originales:
  `musica_aula` (pelea en el aula), `musica_plaza` (pelea en la plaza), `musica_menu` y `musica_seleccion`.

Las ilustraciones `assets/source/angel.jpg`, `facu.jpg`, `pedro.jpg`, `emi.jpg` y `denis.jpg` fueron provistas por el autor del proyecto.

Las ilustraciones de Angel, Facu, Pedro, Emi y Denis se reemplazaron en la versión 1.3.1 por skins nuevas provistas por el autor del proyecto.


## Versión 1.5

- Música nueva: `musica_gloriosa` y `musica_patio` (síntesis FM original, `python tools/build_audio_v2.py musica_gloriosa musica_patio`).
- Los fondos `assets/backgrounds/la_gloriosa.jpg` y `el_patio.jpg` fueron provistos por el autor del proyecto.
