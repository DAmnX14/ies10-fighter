"""
Poses de referencia (imágenes provistas por el autor, 765x1024 px, mirando a la derecha).

Se usan como MODELO de postura para todos los luchadores: de cada imagen se marcaron
las articulaciones y el rig (tools/rig.py → RigCharacter.ref_params) convierte esas
posiciones a la pose de cada personaje respetando sus propias proporciones:
  - altura de la cadera según el largo de pierna del personaje,
  - inclinación del torso y de la cabeza por ángulo,
  - manos en dirección y extensión relativas al largo del brazo,
  - tobillos relativos a la cadera, escalados por el largo de pierna,
  - ángulo del pie.
b_ = brazo/pierna trasera (lado izquierdo de la imagen), f_ = delantera (hacia el rival).
"""

REF_LEG = 320.0      # largo de pierna de la referencia (cadera→tobillo estirada), px
REF_ARM = 200.0      # largo de brazo de la referencia (hombro→mano estirado), px

POSES = {
    'guardia': dict(ground=935, head=(420, 200), neck=(415, 265), pelvis=(360, 560),
                    b_sh=(240, 290), b_el=(235, 440), b_ha=(395, 345),
                    f_sh=(490, 280), f_el=(540, 435), f_ha=(550, 295),
                    b_hip=(300, 580), b_an=(205, 880), b_toe=(150, 905),
                    f_hip=(440, 580), f_an=(540, 880), f_toe=(625, 920)),
    'guardia-alta': dict(ground=940, head=(385, 185), neck=(390, 250), pelvis=(370, 560),
                         b_sh=(240, 290), b_el=(270, 450), b_ha=(390, 300),
                         f_sh=(490, 280), f_el=(530, 430), f_ha=(555, 290),
                         b_hip=(310, 580), b_an=(230, 890), b_toe=(160, 910),
                         f_hip=(440, 580), f_an=(550, 890), f_toe=(620, 925)),
    'barrida': dict(ground=915, head=(440, 430), neck=(370, 480), pelvis=(280, 710),
                    b_sh=(230, 450), b_el=(140, 480), b_ha=(210, 590),
                    f_sh=(395, 600), f_el=(390, 740), f_ha=(400, 870),
                    b_hip=(250, 730), b_an=(240, 870), b_toe=(180, 905),
                    f_hip=(340, 740), f_an=(630, 850), f_toe=(685, 790)),
    'celebrando': dict(ground=940, head=(395, 175), neck=(380, 260), pelvis=(370, 580),
                       b_sh=(265, 310), b_el=(255, 455), b_ha=(180, 370),
                       f_sh=(500, 290), f_el=(570, 240), f_ha=(585, 150),
                       b_hip=(320, 600), b_an=(200, 880), b_toe=(140, 900),
                       f_hip=(430, 600), f_an=(590, 880), f_toe=(630, 925)),
    'patada-alta': dict(ground=925, head=(255, 230), neck=(230, 330), pelvis=(290, 550),
                        b_sh=(180, 330), b_el=(125, 450), b_ha=(180, 355),
                        f_sh=(350, 320), f_el=(400, 340), f_ha=(400, 240),
                        b_hip=(280, 570), b_an=(230, 880), b_toe=(160, 910),
                        f_hip=(340, 550), f_an=(610, 230), f_toe=(660, 170)),
    'patada-media': dict(ground=920, head=(285, 205), neck=(275, 300), pelvis=(280, 550),
                         b_sh=(140, 340), b_el=(130, 450), b_ha=(250, 450),
                         f_sh=(360, 350), f_el=(420, 390), f_ha=(420, 300),
                         b_hip=(280, 590), b_an=(250, 850), b_toe=(300, 895),
                         f_hip=(320, 570), f_an=(630, 440), f_toe=(690, 390)),
    'provocando': dict(ground=940, head=(395, 180), neck=(390, 260), pelvis=(370, 570),
                       b_sh=(230, 290), b_el=(190, 400), b_ha=(260, 480),
                       f_sh=(510, 300), f_el=(530, 410), f_ha=(620, 240),
                       b_hip=(320, 590), b_an=(240, 880), b_toe=(160, 910),
                       f_hip=(430, 590), f_an=(560, 880), f_toe=(630, 925)),
    'recibiendo-golpe': dict(ground=920, head=(310, 190), neck=(340, 270), pelvis=(390, 550),
                             b_sh=(210, 320), b_el=(150, 410), b_ha=(250, 350),
                             f_sh=(480, 290), f_el=(570, 330), f_ha=(660, 380),
                             b_hip=(340, 570), b_an=(200, 870), b_toe=(230, 915),
                             f_hip=(450, 570), f_an=(490, 830), f_toe=(530, 880)),
    'salto': dict(ground=935, air=True, head=(410, 180), neck=(400, 250), pelvis=(360, 530),
                  b_sh=(230, 290), b_el=(180, 350), b_ha=(300, 310),
                  f_sh=(490, 320), f_el=(540, 400), f_ha=(560, 260),
                  b_hip=(300, 550), b_an=(340, 730), b_toe=(345, 805),
                  f_hip=(420, 550), f_an=(430, 670), f_toe=(440, 740)),
    'triste': dict(ground=940, head=(490, 230), neck=(430, 290), pelvis=(370, 570),
                   b_sh=(320, 320), b_el=(310, 480), b_ha=(330, 630),
                   f_sh=(490, 370), f_el=(500, 500), f_ha=(510, 610),
                   b_hip=(330, 590), b_an=(190, 880), b_toe=(200, 915),
                   f_hip=(420, 590), f_an=(570, 880), f_toe=(620, 925)),
}
