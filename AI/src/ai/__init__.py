from whisper_mic import WhisperMic    
        
model = WhisperMic(model="base", english=True, pause=0.5)

# Continuously transcribe microphone words into text and evaluate those words in two second chunks
for text in model.listen_continuously(phrase_time_limit=2):
    if not text:
        continue
    
    # Remove all punctunation and split the text into words
    text = text.lower().replace('.','').replace(',','').replace('!','').replace('?','').replace('[','').replace(']','')
    words = text.split(' ')
    
    # Go through the words and run any commands found
    # Some commands have multiple words for speech impendements, accents, or in case the AI misinterprets the word
    if "up" in words or "uh" in words or "bye" in words or "ah" in words or "off" in words:
        print("w key input")
    if "down" in words or "dow" in words or "now" in words:
        print("s key input")
    if "right" in words or "write" in words or "rite" in words or "white" in words:
        print("d key input")
    if "left" in words or "let" in words:
        print("a key input")
    if "pause" in words or "paws" in words or "unpause" in words or "pawns" in words or "continue" in words:
        print("esc key input")
    if "ember" in words or "umber" in words or "ever" in words or "amber" in words or "denver" in words:
        print("f key input")
    if "gust" in words or "guts" in words or "wind" in words or "winned" in words or "gus" in words or "gussed" in words or "gas" in words or "guest" in words or "dust" in words:
        print("g key input")
    if "translate" in words or "interpret" in words or "late" in words or "sleet" in words:
        print("t key input")
    if "open" in words or "close" in words or "clothes" in words:
        print("e key input")
    if "quit" in words or "kit" in words or "leave" in words or "leaf" in words or "wit" in words or "wet" in words or "quid" in words:
        print("quit input")
        quit()