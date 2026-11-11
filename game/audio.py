"""Gestor de audio: efectos, voces y música en bucle con volumen configurable."""
import os
import random
import pygame
import config as C


class Audio:
    def __init__(self, settings):
        self.settings = settings
        self.ok = True
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.set_num_channels(32)
        except pygame.error:
            self.ok = False
        self.sounds = {}
        self.current_music = None
        self.voice_channel = None
        if self.ok:
            for fn in os.listdir(C.SND_DIR):
                name, ext = os.path.splitext(fn)
                if ext.lower() in ('.ogg', '.wav'):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(os.path.join(C.SND_DIR, fn))
                    except pygame.error:
                        pass
            self.voice_channel = pygame.mixer.Channel(31)
            self.ann_channel = pygame.mixer.Channel(30)
            pygame.mixer.set_reserved(2)

    def play(self, name, vol=1.0):
        if not self.ok:
            return
        s = self.sounds.get(name)
        if s:
            s.set_volume(min(1.0, vol * self.settings['sfx_volume']))
            s.play()

    def voice(self, char, key, vol=1.0):
        """Voz de un personaje (interrumpe su voz anterior)."""
        if not self.ok:
            return
        s = self.sounds.get(f'{char}_voz_{key}')
        if s:
            s.set_volume(min(1.0, vol * self.settings['voice_volume']))
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.play(s)

    def announce(self, key):
        if not self.ok:
            return
        s = self.sounds.get(key)
        if s:
            s.set_volume(min(1.0, self.settings['voice_volume']))
            self.ann_channel.play(s)

    def grunt(self, char, kind):
        opts = {'ataque': ['grito_1', 'grito_2', 'grito_3'], 'dolor': ['dolor_1', 'dolor_2']}[kind]
        self.voice(char, random.choice(opts), 0.8)

    def music(self, name, loop=True, fade=600):
        if not self.ok or name == self.current_music:
            return
        self.current_music = name
        path = None
        for ext in ('.ogg', '.wav'):
            p = os.path.join(C.MUS_DIR, name + ext)
            if os.path.exists(p):
                path = p
                break
        if not path:
            return
        try:
            pygame.mixer.music.fadeout(150)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.settings['music_volume'])
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade)
        except pygame.error:
            pass

    def stop_music(self, fade=400):
        if self.ok:
            pygame.mixer.music.fadeout(fade)
        self.current_music = None

    def refresh_volume(self):
        if self.ok:
            pygame.mixer.music.set_volume(self.settings['music_volume'])
