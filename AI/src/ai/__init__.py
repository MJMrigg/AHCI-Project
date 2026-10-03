from whisper_mic import WhisperMic
import os

# Create the model
model = WhisperMic(model="base", english=True)

# Listen to the microphone and analyze the audio data
while(1):
    
    words = []
    try:
        # Get the model's transcription
        text = model.listen(timeout=1)
        text = text.lower()
        print(text)
        
        # Convert the text to an array of words
        words = text.split(' ')
        print(words)
        
        # Remove all punctuation(just in case)
        for i in range(0,len(words)):
            words[i] = words[i].replace('.','')
            words[i] = words[i].replace('!','')
            words[i] = words[i].replace('?','')
            words[i] = words[i].replace(',','')
            words[i] = words[i].replace('\'','')
        print(words)
    except Exception as error:
        print(error)
    
    # Go through the words and run any commands found
    # Some commands have multiple words for speech impendements or accents
    if "up" in words or "uh" in words or "bye" in words or "ah" in words or "off" in words:
        print("w key input")
    elif "down" in words or "dow" in words or "now" in words:
        print("s key input")
    elif "right" in words or "write" in words or "rite" in words or "white" in words:
        print("d key input")
    elif "left" in words or "let" in words:
        print("a key input")
    elif "pause" in words or "paws" in words or "unpause" in words or "pawns" in words or "continue" in words:
        print("esc key input")
    elif "ember" in words or "umber" in words or "ever" in words or "amber" in words or "denver" in words:
        print("f key input")
    elif "gust" in words or "guts" in words or "wind" in words or "winned" in words or "gus" in words or "gussed" in words or "gas" in words or "guest" in words or "dust" in words:
        print("g key input")
    elif "translate" in words or "interpret" in words or "late" in words or "sleet" in words:
        print("t key input")
    elif "open" in words or "close" in words or "clothes" in words:
        print("e key input")
    elif "quit" in words or "kit" in words or "leave" in words or "leaf" in words or "wit" in words or "wet" in words or "quid" in words:
        print("quit input")
        quit()