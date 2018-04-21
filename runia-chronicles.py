import functools
import importlib
import os
import time
import traceback

# These are not hot-reloadable (Stateful)
import pyxelen
import model

# These are hot-reloadable (Stateless)
import view
import screens


TITLE = 'Runia Chronicles'
WIDTH = 512
HEIGHT = 288


class EventHandler:

    def __init__(self, pyxelen):
        self.pyxelen = pyxelen
        self.width = WIDTH
        self.height = HEIGHT
        self.music_playing = ""
        self.window = self.pyxelen.open_window(TITLE, WIDTH, HEIGHT)
        self.renderer = self.window.create_renderer()
        self.buffer = self.renderer.create_texture(WIDTH, HEIGHT)
        self.state = model.initial_model

    @property
    def screen(self):
        return screens.screens[self.state.scene.screen]

    def reload(self):
        importlib.reload(screens)
        self._to_sprites.cache_clear()
        self.load_image.cache_clear()

    @functools.lru_cache()
    def load_music(self, filename):
        return self.pyxelen.audio.load_music(filename)

    @functools.lru_cache()
    def load_effect(self, filename):
        return self.pyxelen.audio.load_effect(filename)

    @functools.lru_cache()
    def load_image(self, filename):
        return self.renderer.create_texture_from_image(filename)

    @functools.lru_cache()
    def _to_sprites(self, font, text, x, y, centered):
        if centered:
            offset_x = 0
            for c in text:
                offset_x += font.offsets.get(
                    c, (int(font.size_x / 2), 0)
                )[0]
            offset_x = - int(offset_x / 2)
            offset_y = - int(font.size_y / 2)
        else:
            offset_x = 0
            offset_y = 0
        results = []
        for c in text:
            if c in font.glyphs:
                results.append(
                    (
                        font.glyphs[c],
                        view.Box(
                            x + offset_x,
                            y + offset_y + font.offsets[c][1],
                            font.size_x,
                            font.size_y
                        )
                    )
                )
            offset_x += font.offsets.get(
                c, (int(font.size_x / 2), 0)
            )[0]
        return results

    def draw_sprite(self, image, dest):
        clip = image.clip
        self.renderer.copy(
            self.load_image(image.filename),
            clip.x, clip.y, clip.w, clip.h,
            dest.x, dest.y, dest.w, dest.h
        )

    def draw_text(self, font, text, x, y, centered):
        sprites = self._to_sprites(font, text, x, y, centered)
        for image, dest in sprites:
            self.draw_sprite(image, dest)

    def play_music(self, filename):
        music = self.load_music(filename)
        self.pyxelen.audio.play_music(music)
        self.music_playing = filename

    def play_effect(self, filename):
        effect = self.load_effect(filename)
        self.pyxelen.audio.play_effect(effect, self.state.effects_volume)

    def on_key_down(self, window, key, modifiers, repeat):
        try:
            new_state = self.screen.on_key_down(key, self.state)
            assert isinstance(new_state, model.Model)
            self.state = new_state
        except Exception:
            traceback.print_exc()
            # self.reload()

    def process_audio(self):
        self.pyxelen.audio.set_music_volume(self.state.music_volume)
        if self.music_playing != self.state.music:
            self.play_music(self.state.music)
        for filename in self.state.effects:
            self.play_effect(filename)
        self.state = self.state.clear_effects()

    def on_update_and_render(self):
        try:
            # self.reload()
            new_state = self.screen.on_update(self.state)
            assert isinstance(new_state, model.Model)
            self.state = new_state
            self.render()
            self.process_audio()
        except Exception:
            traceback.print_exc()

    def render(self):
        self.renderer.target = self.buffer
        self.renderer.draw_color = 0, 0, 0, 255
        self.renderer.clear()

        self.screen.view(self, self.state)

        self.renderer.target = None
        self.renderer.copy(
            self.buffer,
            0, 0, *self.size,
            *self.offset, *self.scaled_size
        )
        self.renderer.present()

    @property
    def size(self):
        return self.width, self.height

    @property
    def scale(self):
        aspect = self.width / self.height
        w, h = self.window.size
        window_aspect = w / h
        # Window is wider than desired, scale with Y
        if window_aspect > aspect:
            return h / self.height
        # Window is narrower than desired, scale with X
        else:
            return w / self.width

    @property
    def offset(self):
        w, h = self.window.size
        scaled_w, scaled_h = self.scaled_size
        return int((w - scaled_w) // 2), int((h - scaled_h) // 2)

    @property
    def scaled_size(self):
        scale = self.scale
        return int(self.width * scale), int(self.height * scale)


def main():
    pyxelen.init()
    platform = pyxelen.Pyxelen()
    handler = EventHandler(platform)
    platform.run(handler, 30)


if __name__ == '__main__':
    main()
