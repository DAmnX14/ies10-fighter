# Prompts para generar los sprites de PANTOJA

## Cómo usarlos

1. En la herramienta de imágenes, adjuntá **siempre** dos imágenes de referencia:
   - `assets/source/pantoja.jpg` → **cómo es Pantoja** (cara, ropa, cuerpo).
   - un dibujo de Denis, por ejemplo `assets/characters/denis/dibujados/guardia.png` → **el estilo** (mismo pixel art, mismo tamaño, mismo encuadre).
2. Pegá el **BLOQUE BASE** y, abajo, el prompt de **una sola pose**. Una imagen por pose.
3. Guardá cada resultado con el **nombre de archivo** indicado (por ejemplo `patada-media.png`).
4. Revisá que la pose sea la del nombre, que mire a la derecha y que se vea el cuerpo entero.
   Si sale distinto (otra cara, otra ropa, otro tamaño), regenerala.
5. Mandame todo en un zip: `pantoja.zip`.

---

## BLOQUE BASE (pegarlo siempre antes de cada pose)

```
16-bit arcade fighting game sprite, pixel art, same art style, outline and shading as the
attached style reference. Exactly the same character as the attached character reference:
PANTOJA, a chubby adult man with a round belly, short messy black hair, light brown skin and
light stubble, wearing a plain pink short-sleeve t-shirt, blue jeans, barefoot, with red
fingerless hand wraps on both hands. Full body visible from head to feet, side view, facing
RIGHT, centered, same size and scale as the reference, plain light checkered background
(or transparent), no text, no logos, no extra people, no shadows on the background.
```

---

## Poses base (24)

| Archivo | Prompt de la pose |
|---|---|
| `guardia.png` | Fighting stance: knees bent, feet apart, both fists up in front of the chest, ready to fight. |
| `guardia-alta.png` | Blocking: both forearms raised in front of the face, leaning slightly back, bracing. |
| `caminar-1.png` | Walking forward in guard, fists up, left foot forward, right foot back (step 1 of 4). |
| `caminar-2.png` | Walking forward in guard, fists up, feet passing each other, weight centered (step 2 of 4). |
| `caminar-3.png` | Walking forward in guard, fists up, right foot forward, left foot back (step 3 of 4). |
| `caminar-4.png` | Walking forward in guard, fists up, feet passing each other again (step 4 of 4). |
| `agachado.png` | CROUCHING low, knees fully bent, butt close to the floor, fists up in guard. The body must be much lower than standing. |
| `agachado-guardia.png` | CROUCHING low and blocking: forearms crossed in front of the face. |
| `golpe-agachado.png` | CROUCHING low and throwing a straight punch forward at belly height. |
| `barrida.png` | Low sweep kick: crouched, one hand on the floor, front leg extended straight forward along the floor. |
| `golpe.png` | Quick jab: front arm fully extended forward at face height, back fist near the chin, feet planted. |
| `golpe-fuerte.png` | Heavy straight punch: whole body twisted forward, back arm fully extended, front foot stepping in. |
| `patada-media.png` | Mid kick: standing on the back leg, front leg extended straight forward at belly height, fists up. |
| `patada-alta.png` | High kick: standing on the back leg, front leg kicking up to head height, fists up. |
| `salto.png` | Jumping straight up in the air, knees tucked up, fists in guard. |
| `salto-adelante.png` | Forward somersault in mid-air, body curled in a ball, rotating. |
| `patada-aerea.png` | Flying kick in mid-air, front leg extended diagonally down-forward. |
| `recibiendo-golpe.png` | Getting hit in the face: head snapped back with a pained grimace, torso bent back, arms loose. |
| `cayendo.png` | Knocked into the air, flying backwards, body tilted back almost horizontal, arms and legs loose. |
| `tirado.png` | Knocked out, lying flat on his back on the floor, head on the LEFT and feet on the RIGHT, eyes closed. Horizontal. |
| `levantandose.png` | Getting up from the floor: one knee and one hand on the ground, pushing himself up. |
| `celebrando.png` | Victory: big smile, one fist raised high above the head, standing proud. |
| `triste.png` | Defeated: head down, shoulders slumped, arms hanging, sad expression. |
| `provocando.png` | Taunting: confident smile, beckoning the opponent with one open hand ("come on"). |

## Poderes de Pantoja (5)

| Archivo | Poder | Prompt de la pose |
|---|---|---|
| `panzazo.png` | Panzazo (especial 1) | Belly charge: leaning back and thrusting his big belly forward, running into the opponent, arms back. |
| `grito-metalero.png` | Grito metalero (especial 2) | Heavy-metal scream: head tilted back shouting, one hand raised doing the "metal horns" hand sign. |
| `terremoto.png` | Terremoto Pantoja (ultimate 1) | Ground pound: landing from a jump, crouched, both fists slamming the floor. |
| `cachetadas.png` | Lluvia de cachetadas (ultimate 2) | Fast slapping: one open hand swinging forward in a slap, the other hand pulled back, leaning forward. |
| `colectivazo.png` | Colectivazo (ultimate 3) | Full-body charge like a bus: running hard, shoulder and belly forward, head down. |

## Escena antes de pelear (1)

| Archivo | Cuándo | Prompt de la pose |
|---|---|---|
| `enamorado.png` | Contra Parada | In love: hands clasped on his chest, head tilted, dreamy smile. |

---

**Total: 30 imágenes.** Si no llegás a todas, empezá por estas 12, que son las que más se ven:
`guardia`, `caminar-1` a `caminar-4`, `golpe`, `patada-media`, `agachado`, `recibiendo-golpe`,
`tirado`, `celebrando` y `salto`. Lo que falte sigue con los cuadros generados por el juego.
