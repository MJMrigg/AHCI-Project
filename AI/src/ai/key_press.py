from collections import defaultdict
import time
from pynput.keyboard import Key, KeyCode, Controller

class KeyPresser:
    def __init__(self):
        # keep track of if key is pressed, defaults to
        # key not being pressed
        self.key_states: defaultdict[Key | KeyCode, bool] = defaultdict(bool)
        # handles the key pressing
        self.controller = Controller()

    def press(self, key: str | Key | KeyCode) -> None:
        resolved = self.controller._resolve(key)
        self.controller.press(resolved)
        self.key_states[resolved] = True

    def release(self, key: str | Key | KeyCode) -> None:
        resolved = self.controller._resolve(key)
        self.controller.release(resolved)
        self.key_states[resolved] = False

    def toggle(self, key: str | Key | KeyCode) -> None:
        resolved = self.controller._resolve(key)

        if self.key_states[resolved]:
            # if pressed then release
            self.release(key)
        else:
            # if not pressed then press
            self.press(key)
    
    def press_once(self, key: str| Key | KeyCode) -> None:
        self.press(key)
        self.release(key)
    
    def release_all(self):
        for key in ["a", "s", "d", "w", "t", "f", "q", "g", "e", Key.esc]:
            self.release(key)
    
    def pause(self):
        for key in ["a", "s", "d", "w"]:
            if self.key_states[key]:
                self.toggle(key)
    
    def unpause(self):
        pass # movement does not resume after unpausing
        # for key in ["a", "s", "d", "w"]:
        #     if self.key_states[key]:
        #         self.controller.press(key)
