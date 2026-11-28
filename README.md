# IES 10 FIGHTER

Juego de lucha 2D estilo arcade de los 90, hecho en **Python + Pygame**, con diez
luchadores del IES N.º 10: **PANTOJA, PARADA, NEHUEN, LUCIANO, ANGEL, FACU, PEDRO, EMI y DENIS**,
más **NICO**, el jefe final.
Cuatro escenarios: el **aula del IES 10**, **la plaza**, **La Gloriosa** (la cancha) y **El Patio** del colegio. Una producción de **Arce Tech**.

![Logo](assets/interface/logo.png)

---

## 1. Instalación (Windows)

1. Instalá **Python 3.10 o superior** desde <https://www.python.org/downloads/>
   (en el instalador marcá **“Add Python to PATH”**).
2. Descomprimí la carpeta `IES10_FIGHTER` donde quieras.
3. Abrí una terminal (*cmd* o *PowerShell*) dentro de esa carpeta e instalá la dependencia:

   ```
   pip install pygame-ce
   ```
   (si preferís el pygame clásico: `pip install pygame` — también funciona)

4. Ejecutá el juego:

   ```
   python main.py
   ```

Una vez instalado **no necesita internet**: todos los sprites, efectos, sonidos, voces y
músicas ya están dentro de `assets/`.

También funciona en Linux y macOS con los mismos pasos.

---

## 2. Controles

| Acción            | Jugador 1 | Jugador 2            |
|-------------------|-----------|----------------------|
| Moverse           | A / D     | ← / →                |
| Saltar            | W         | ↑                    |
| Agacharse         | S         | ↓                    |
| Puñetazo          | F         | 1 (o Num 1)          |
| Patada            | G         | 2 (o Num 2)          |
| Golpe especial    | R         | 3 (o Num 3)          |
| Ultimate          | T         | 4 (o Num 4)          |
| Bloquear          | E         | 5 (o Num 5)          |

**Combinaciones** (`→` = hacia el rival):

| Movimiento                 | Entrada                               |
|----------------------------|---------------------------------------|
| Golpe fuerte               | → + Puñetazo                          |
| Patada alta (fuerte)       | → + Patada                            |
| Jab bajo                   | ↓ + Puñetazo                          |
| Barrida (derriba)          | ↓ + Patada                            |
| Patada aérea               | Puñetazo o Patada en el aire          |
| Especial 1 / Especial 2    | Especial  /  ↓ + Especial             |
| Ultimate 1 / 2 / 3         | Ultimate  /  ↓ + Ultimate  /  → + Ultimate (barra llena) |
| Bloqueo alto / bajo        | Bloquear  /  ↓ + Bloquear             |

- Las barridas sólo se bloquean **agachado**; las patadas aéreas sólo **de pie**.
- **ESC** o **P**: pausa (continuar, lista de movimientos, salir).
- **F11**: pantalla completa.
- **F9** (durante la pelea): **modo debug**. Muestra hurtbox (verde), hitboxes activas (rojo),
  caja de empuje (amarillo), rectángulo del sprite (azul), ancla y línea de los pies (magenta),
  límites del escenario, cajas de los proyectiles y, debajo de cada luchador, posición X/Y,
  escala, animación, cuadro y si los pies están apoyados. En Entrenamiento también con **F2**.
- Todos los controles se pueden cambiar en **OPCIONES → CONTROLES JUGADOR 1 / 2**.

### Joystick / mando

Se puede jugar con mando (Xbox, PlayStation o genérico USB), con teclado o con los dos a la vez.
En **OPCIONES → ENTRADA JUGADOR 1 / 2** cada jugador elige **TECLADO + MANDO**, **SÓLO TECLADO**
o **SÓLO MANDO**. Los mandos se reparten solos: el primero que se conecta es del jugador 1 y
el segundo del jugador 2 (si el jugador 1 elige *sólo teclado*, el primer mando pasa al jugador 2).
Se pueden conectar y desconectar en cualquier momento.

| Acción          | Mando (Xbox)      | Mando (PlayStation) |
|-----------------|-------------------|---------------------|
| Moverse / saltar / agacharse | Cruceta o stick izquierdo | Cruceta o stick izquierdo |
| Puñetazo        | X                 | □                   |
| Patada          | A                 | ✕                   |
| Especial        | Y                 | △                   |
| Ultimate        | RB o RT           | R1 o R2             |
| Bloquear        | B o LB            | ○ o L1              |
| Pausa           | START             | OPTIONS             |

En los menús: cruceta/stick para moverse, **A (✕)** o **START** para aceptar y **B (○)** para volver.
Los botones del mando también se reasignan en **OPCIONES → CONTROLES JUGADOR 1 / 2**
(elegís la acción, ENTER, y apretás el botón del mando).

---

## 3. Modos de juego

| Menú                          | Descripción |
|-------------------------------|-------------|
| **JUGAR → 1 JUGADOR VS CPU**  | Elegís tu luchador y el rival; combate rápido contra la computadora. |
| **JUGAR → ENTRENAMIENTO**     | Vida que se regenera y barra de ultimate infinita. **F1** cambia el comportamiento del rival (quieto / agachado / salta / bloquea todo / CPU), **F2** muestra las hitboxes, **F3** reinicia posiciones. |
| **MODO ARCADE**               | Enfrentás a 5 luchadores al azar con dificultad creciente y, al final, a **NICO, el jefe de ArceTech**, en la plaza. Hay pantalla de “¿Continuar?” y final propio para cada personaje. |
| **VERSUS**                    | Dos jugadores en el mismo teclado, con mandos o mezclando teclado y mando. En la pantalla «VS» se elige el escenario con ← →. |
| **PERSONAJES**                | Galería: todas las animaciones de cada luchador, estadísticas y lista de movimientos. |
| **OPCIONES**                  | Volumen de música / efectos / voces, tiempo por ronda (30/60/99/∞), rondas (1, mejor de 3, mejor de 5), dificultad de la CPU (Fácil/Normal/Difícil/Extremo), pantalla completa, filtro CRT, intro y controles. |

Cada combate es **al mejor de tres rondas** (configurable), con temporizador, KO, tiempo
agotado, empate, “¡Perfecto!”, contador de combos y pantalla **«PANTOJA WINS»**, etc.

---

## 4. Los luchadores

| | Fuerza | Velocidad | Resistencia | Alcance | Ejecución | Estilo |
|---|:-:|:-:|:-:|:-:|:-:|---|
| **PANTOJA** – *El Marido de Parada* | 9 | 4 | 9 | 5 | 5 | Pesado, mucha vida, golpes demoledores |
| **PARADA** – *El Besa Perro* | 6 | 9 | 5 | 6 | 9 | Velocísimo, combos de impacto múltiple |
| **NEHUEN** – *El Bostero* (hincha de Boca) | 6 | 6 | 6 | 9 | 6 | Gran alcance, ataques aéreos y a distancia; todo en azul y oro |
| **LUCIANO** – *Voltio* | 7 | 7 | 7 | 6 | 8 | Equilibrado, combos y remate brutal |
| **NICO** – *El Jefe de ArceTech* (jefe final) | 8 | 7 | 8 | 7 | 8 | Completo y peligroso: proyectil, rodillazo y ultimates de pantalla completa |
| **ANGEL** – *El Compilador Humano* (programador) | 8 | 5 | 8 | 6 | 7 | Robusto: código como proyectil, combo en bucle y lluvia de código |
| **FACU** – *El Domador de la IA* (y su gato naranja) | 5 | 8 | 5 | 9 | 8 | A distancia: gato proyectil, rayo de IA y lluvia de michis |
| **PEDRO** – *El Hombre de la Paz* | 6 | 6 | 9 | 7 | 7 | Defensivo: paloma, onda zen y una bandera blanca muy engañosa |
| **EMI** – *El Alumno Ejemplar* | 6 | 8 | 6 | 7 | 8 | Veloz y técnico: avión de papel, mochilazo y prueba sorpresa |
| **DENIS** – *El Millonario* (hincha de River) | 8 | 7 | 6 | 8 | 6 | Ofensivo: pelotazos, la banda roja y el golazo de media cancha |

### Especiales y Ultimates (14 ultimates distintas)

| Personaje | Especial 1 | Especial 2 | Ultimate 1 | Ultimate 2 | Ultimate 3 (→ + Ultimate) |
|---|---|---|---|---|---|
| Pantoja | **Panzazo** (embestida con la panza) | **Grito metalero** (onda sonora con cuernos) | **Terremoto Pantoja**: salto gigante y golpe al suelo que sacude toda el aula | **Lluvia de cachetadas**: 10 cachetadas + gancho final | **Colectivazo**: embestida que arrastra al rival por toda el aula |
| Parada | **Ráfaga esmeralda** (dash con puño) | **Patada huracán** (doble patada ascendente) | **Mil piñas**: ráfaga supersónica de 14 puñetazos + empujón final | **Tornado verde**: cruces relámpago a través del rival + patada al cielo | **Cien patadas**: ráfaga de patadas + patada final al cielo |
| Nehuen | **Bufandazo** (revolea y tira la bufanda azul y oro) | **Chilena xeneize** (anti-aérea) | **Azul y oro**: rayo que atrapa al rival + explosión | **La Doce salta**: salto altísimo y caída en picada con lluvia de papelitos | **La Bombonera late**: tres pisotones que hacen temblar el piso |
| Luciano | **Credencial voladora** (boomerang) | **Gancho preceptor** (uppercut) | **Combo disciplinario**: combo de 6 golpes que termina en uppercut | **Amonestación final**: carga de poder y un único puñetazo devastador | **Alto voltaje**: tres rayos que caen sobre el rival |
| Nico | **Hoja de arce** (proyectil) | **Reinicio forzado** (rodillazo volador) | **Pantallazo azul**: golpe a toda la pantalla | **Despido inmediato**: combo y patada que manda al rival a volar | — |
| Angel | **Bug en producción** (proyectil de código) | **Deploy forzado** (uppercut) | **Bucle infinito**: combo de 6 golpes en loop | **Stack overflow**: tres columnas de código caen sobre el rival | — |
| Facu | **Michi naranja** (su gato corre hacia el rival) | **Zarpazo gatuno** (dash con zarpazo) | **Prompt definitivo**: rayo de IA que atrapa al rival | **Lluvia de michis**: gatos naranjas caen del cielo | — |
| Pedro | **Paloma de la paz** (proyectil) | **Onda zen** (onda alrededor) | **Paz interior**: medita y cae una columna de luz | **Bandera blanca**: se rinde... y pega un puñetazo devastador | — |
| Emi | **Avión de papel** (proyectil) | **Mochilazo** (uppercut) | **Prueba sorpresa**: combo de 6 golpes | **Tabla del nueve**: lluvia de números sobre el rival | — |
| Denis | **Pelotazo** (pelota de fútbol) | **Banda roja** (embestida que derriba) | **El Monumental ruge**: la hinchada hace temblar el piso | **Golazo de media cancha**: patea una pelota gigante | — |

### Encuentros antes de pelear

Antes de la primera ronda, algunas parejas tienen su propia escena (se saltea con ACEPTAR / START):

- **Parada y Pantoja**: son pareja → se acercan enamorados, con corazones.
- **Nico y Angel**: se dan un abrazo antes de pelear.
- **Pedro con Emi, Nico o Luciano**: saludo de amistad bien amigable.
- **Denis y Nehuen** (River – Boca): cara a cara, rayos y cargadas: **¡SUPERCLÁSICO!**
- **Angel, Facu, Pedro, Emi o Denis contra Parada**: todos lo odian → **¡TODOS CONTRA PARADA!**

### Fondos animados

Los cuatro escenarios están animados (`game/stage_anim.py`): el público se balancea y salta
—y se agita más con los golpes fuertes y estalla con el K.O.—, las banderas flamean, las
luces brillan y parpadean, la fuente de la plaza tira agua y en el patio cruzan pájaros al
atardecer. Las zonas animadas de cada fondo se configuran en `STAGE_ANIM`.

### Música

Cada escenario tiene su propio tema de pelea (aula, plaza, La Gloriosa y El Patio), más temas nuevos para el menú y la
selección de personajes, con sonido FM de placa arcade de 16 bits. Todo es composición original.

Cada ultimate tiene: animación de preparación, “super flash” con pantalla congelada,
recuadro cinematográfico con el retrato y el nombre del ataque, aura, animación de ataque,
efectos de impacto, reacción del rival, zoom y temblor de cámara, voz y sonido propios y
animación de finalización.

---

## 5. Estructura del proyecto

```
IES10_FIGHTER/
├── main.py                 ← ejecutar este archivo
├── config.py               ← resolución, rutas, controles, opciones (settings.json)
├── requirements.txt
├── game/
│   ├── player.py           ← luchador: estados, física, movimientos
│   ├── combat.py           ← rondas, daño, bloqueo, combos, proyectiles, ultimates, HUD
│   ├── characters_data.py  ← estadísticas, frases y TODOS los movimientos
│   ├── animations.py       ← reproducción de animaciones desde los spritesheets
│   ├── assets.py           ← carga/caché de spritesheets, efectos y fuentes
│   ├── collisions.py       ← hitboxes (círculo) vs hurtboxes (rectángulo por cuadro)
│   ├── controls.py         ← entrada con búfer
│   ├── ai.py               ← IA con 4 niveles de dificultad
│   ├── audio.py  particles.py  camera.py  stage.py  ui.py
├── screens/                ← intro, menú, selección, versus, combate, arcade,
│                             entrenamiento, opciones, galería, resultados
├── assets/
│   ├── characters/<nombre>/  ← spritesheets PNG + <nombre>_meta.json + retrato
│   ├── backgrounds/escenario.jpg
│   ├── effects/  sounds/  music/  interface/  fonts/
│   └── source/              ← ilustraciones originales de cada personaje
├── tools/                  ← generadores de sprites, efectos, audio y logo + test
└── documentation/
    ├── sprites_documentation.md
    ├── audio_credits.md
    └── capturas/           ← capturas de pantalla del juego
```

---

## 6. Cómo se hicieron los recursos (y qué tener en cuenta)

- **Sprites**: cada luchador se generó a partir de su ilustración original
  (`assets/source/*.jpg`). El script `tools/rig.py` separa la figura del fondo, la divide en
  partes (cabeza, torso, brazos, antebrazos, muslos, piernas y pies) y las vuelve a posar
  con cinemática directa e inversa para crear **cada cuadro** de **25 animaciones por
  personaje (≈ 230 cuadros cada uno)**, cuantizados a la paleta original para mantener el
  estilo pixel-art. Es una animación por recortes (*cut-out*), no dibujada a mano cuadro a
  cuadro: los rasgos, la ropa y los colores son exactamente los de la ilustración, pero en
  poses extremas pueden verse uniones algo duras en hombros o caderas.
- **Sonido y música**: el entorno donde se creó el juego no tenía acceso a Freesound,
  OpenGameArt, Pixabay ni Kenney, así que **todo el audio es original**, sintetizado por
  `tools/build_audio.py` (golpes, efectos, temas chiptune) y `tools/build_audio_v2.py` (golpes nuevos, efectos de los personajes nuevos, voces de los encuentros y la música FM de cada escenario) y las voces con el
  sintetizador libre **eSpeak NG** (suenan robóticas, al estilo de los locutores arcade).
  Si querés reemplazar cualquier sonido, poné un archivo `.ogg` o `.wav` con **el mismo
  nombre** en `assets/sounds/` o `assets/music/` (ver `documentation/audio_credits.md`).
- **Fuente**: *Press Start 2P* (SIL Open Font License).

### Cuadros dibujados (SpriteCook)

Además de los cuadros generados por el rig, un personaje puede tener **poses dibujadas** en
`assets/characters/<nombre>/dibujados/` (por ejemplo, generadas con SpriteCook a partir de su
ilustración). `dibujados.json` indica qué cuadros de qué animación reemplaza cada dibujo y su
tamaño; `tools/apply_drawn_frames.py` los escala sin deformar, los apoya en el suelo, ajusta el
recorte y pone la hitbox en el puño o el pie. Se aplica solo al regenerar los sprites.
Hoy los tiene **Denis**, con dibujos del autor en guardia (con respiración), caminar,
agachado, bloqueos, golpe, golpe fuerte, patadas, barrida, salto, salto adelante, patada aérea,
recibir golpe, caída, levantarse, victoria, derrota, provocación, sus dos especiales y el golazo;
el tirado en el piso es de SpriteCook. El cartel de «El Monumental ruge» usa el arte del autor
(`cutins` en `dibujados.json`).

**Cómo pasar sprites dibujados de otro personaje:** una imagen por pose, de cuerpo entero,
mirando a la derecha, todas al mismo tamaño y estilo (sirve con fondo cuadriculado o liso,
igual que el zip de Denis). Con el nombre de la pose alcanza: guardia, guardia-alta,
patada-media, patada-alta, barrida, recibiendo-golpe, salto, celebrando, triste, provocando,
golpe, agachado, tirado…
Los IDs de SpriteCook de cada dibujo están en `spritecook-assets.json`.

### Inspector de animaciones (debug)

En **PERSONAJES** apretá **F8**: se abre un inspector con cada animación de cada luchador.
Permite pausar (ESPACIO), avanzar o retroceder cuadro por cuadro (`,` `.`), cambiar la
velocidad (`-` `+`), girar al personaje (F) y reiniciar (R). Muestra el cuadro a escala de
juego con el ancla, el suelo, la hurtbox y las articulaciones, los datos del cuadro (recorte,
ticks, bucle, escala, corrección de pies) y la tira completa con el recorte de cada cuadro;
los cuadros que tocan el borde del lienzo se marcan en rojo.

### Poses de referencia

Las poses de guardia, bloqueo, patada media, patada alta, barrida, recibir golpe, salto,
victoria, derrota y presentación de **todos** los luchadores salen de las imágenes de
referencia del autor (`tools/ref_poses.py`). Allí están marcadas las articulaciones de cada
imagen; `tools/rig.py` adapta esa postura a cada personaje según el largo de sus piernas y
brazos. Para cambiar una pose basta con corregir esas coordenadas y regenerar los sprites.

### Render de los luchadores (para agregar o ajustar personajes)

Todos los luchadores se dibujan con el mismo sistema (`game/render.py`):

- **Ancla en los pies (bottom-center)**: cada cuadro de 240×176 px tiene su punto de suelo en
  (112, 170). Ese punto se dibuja en la posición del luchador, que está sobre el suelo del
  escenario (`stage.ground_y`, definido en `config.STAGES`). Al generar los sprites, cada cuadro
  apoyado se alinea para que su punto más bajo quede exactamente en esa línea; si un personaje
  nuevo trajera cuadros desalineados, el render los corrige igual (hasta 6 px).
- **Escala entera** (x3 en combate, x2 en menús) con vecino más cercano: el pixel art no se
  deforma ni se ve borroso. Los retratos se amplían por enteros y recién después se ajustan.
- **Hurtbox por cuerpo real** (cabeza, torso y piernas del cuadro), **hitboxes** sobre la
  articulación que golpea, y **caja de empuje** según el ancho del luchador: todas usan la
  misma transformación que el dibujo, así nunca se desalinean.
- **Perfil por luchador** (`FighterProfile`): escala, offsets, ancla, tamaño de referencia,
  empuje, márgenes de la hurtbox y velocidad de animación; se ajusta sin tocar código en
  `config.FIGHTER_PROFILES`.

### Regenerar recursos (opcional)

```
pip install -r requirements.txt
python tools/build_sprites.py     # spritesheets de los 10 personajes (~12 min)
python tools/build_sprites.py emi # o sólo uno
python tools/build_effects.py     # efectos especiales
python tools/build_interface.py   # logo e ícono
python tools/build_audio.py       # efectos, voces y música originales
python tools/build_audio_v2.py    # golpes nuevos, voces nuevas y música por escenario
python tools/test_headless.py     # prueba automática + capturas
```
