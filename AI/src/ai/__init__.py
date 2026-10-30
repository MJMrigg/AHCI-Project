from whisper_mic import WhisperMic
from key_press import KeyPresser
from pynput.keyboard import Key
        
model = WhisperMic(model="base", english=True, pause=0.5)
key_presser = KeyPresser()
esc = Key.esc
paused = False

up_words = ["high", "hi", "up", "uh", "bye", "ah", "off", "ahh"]
down_words = ["low", "hello", "lo", "lowe", "love", "lobe", "loan", "down", "dow", "now"]
right_words = ["right", "write", "rite", "white", "alright", "great"]
left_words = ["left", "let", "laugh"]
pause_words = ["pause", "paws", "pawns", "oz", "cause", "pawns", "pods", "unpause", "unpods", "unpires", "continue", "resume", "zoom"]
ember_words = ["ember", "amber", "umber", "ever", "denver", "member", "remember"]
gust_words = ["gust", "gassed", "gased", "gussed", "gus", "gas", "guest", "guessed", "guess", "wind", "winned", "win", "guts", "dust"]
translate_words = ["translate", "late", "slate", "sleet", "interpret"]
open_words = ["open", "pen", "pin", "ope", "close", "clothes"]
quit_words = ["quit", "quid", "kit", "wet", "quits", "wit", "squid", "leave", "leaf"]

# Continuously transcribe microphone words into text and evaluate those words in two second chunks
for text in model.listen_continuously(phrase_time_limit=1):
    if not text:
        continue
    
    # Remove all punctunation and split the text into words
    text = text.lower().replace('.','').replace(',','').replace('!','').replace('?','').replace('[','').replace(']','').replace('(','').replace(')','')
    words = text.split(' ')
    
    # Go through the words and run any commands found
    # Some commands have multiple words for speech impendements, accents, or in case the AI misinterprets the word
    for word in words:
        if word in up_words:
            key_presser.toggle("w")
            #print("w key input")
        if word in down_words:
            key_presser.toggle("s")
            #print("s key input")
        if word in right_words:
            key_presser.toggle("d")
            #print("d key input")
        if word in left_words:
            key_presser.toggle("a")
            #print("a key input")
        if word in pause_words:
            key_presser.press_once(esc)
            paused = not paused
            if paused:
                key_presser.pause()
            else:
                key_presser.unpause()
            #print("esc key input")
        if word in ember_words:
            key_presser.press_once("f")
            #print("f key input")
        if word in gust_words:
            key_presser.press_once("g")
            #print("g key input")
        if word in translate_words:
            key_presser.press_once("t")
            #print("t key input")
        if word in open_words:
            key_presser.press_once("e")
            #print("e key input")
        if word in quit_words:
            if key_presser.key_states[esc] or paused:
                key_presser.press_once("q")
                key_presser.release_all()
                #print("quit input")
                quit()
    print(text)