from collections import defaultdict
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