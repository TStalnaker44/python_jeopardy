import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import tempfile
import unittest
from unittest.mock import patch
import pygame
import jeopardyGame as app
from utils.settings import SettingsMenu
from polybius.managers import SOUNDS


class SettingsTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1200, 800))

    def tearDown(self):
        pygame.quit()

    def test_volume_persists_and_is_clamped(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"LOCALAPPDATA": folder}):
            settings = SettingsMenu((1200, 800))
            settings.set_volume(settings.slider.left - 100)
            self.assertEqual(settings.volume, 0)
            settings.set_volume(settings.slider.right + 100)
            self.assertEqual(settings.volume, 100)
            settings.volume = 37
            settings.save()
            self.assertEqual(SettingsMenu((1200, 800)).volume, 37)
            self.assertTrue(SettingsMenu((1200, 800)).fullscreen)
            self.assertFalse(SettingsMenu((1200, 800), False).fullscreen)

    def test_display_is_a_maximized_normal_window(self):
        for maximized in (True, False, True):
            with patch("jeopardyGame.Window") as window, patch("jeopardyGame.setWindowDarkMode") as dark:
                surface = app.setDisplay((1200, 800), maximized)
                self.assertTrue(surface.get_flags() & pygame.RESIZABLE)
                self.assertFalse(surface.get_flags() & (pygame.FULLSCREEN | pygame.NOFRAME))
                self.assertEqual(surface.get_size(), (1200, 800))
                dark.assert_called_once()
                if maximized:
                    window.from_display_module.return_value.maximize.assert_called_once()
                else:
                    window.from_display_module.assert_not_called()

    @unittest.skipUnless(os.name == "nt", "Windows native caption API")
    def test_dark_caption_and_legacy_fallback(self):
        calls = []
        def attribute(handle, key, value, size):
            calls.append((key, value._obj.value))
            return 1 if key == 20 else 0
        with patch("pygame.display.get_wm_info", return_value={"window": 123}), patch("ctypes.WinDLL") as dll:
            dll.return_value.DwmSetWindowAttribute.side_effect = attribute
            app.setWindowDarkMode()
        self.assertEqual(calls, [(20, 1), (19, 1), (35, 0x202020), (36, 0xFFFFFF)])
