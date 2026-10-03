import speech_recognition, asyncio

async def speech_mode():
    # Create the recorder
    recorder = speech_recognition.Recognizer()

    # Listen to the microphone and analyze the audio data
    with speech_recognition.Microphone() as source:
        while(1):
            # Get the microphone data
            print("Start")
            audio_data = recorder.listen(source)
            print("Stop")
            
            words = []
            try:
                # Convert it to text using gemini model
                text = recorder.recognize_google(audio_data).lower()
                print(text)
                
                # Convert the text to an array of words
                words = text.split(" ")
                print(words)
            except Exception as error:
                print(error)
            
            # Go through the words and run the first command found
            # Some commands have multiple words for speech impendements or accents
            if "up" in words or "uh" in words:
                print("w key input")
            elif "down" in words or "dow" in words:
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
            elif "translate" in words or "interpret" in words:
                print("t key input")
            elif "open" in words or "close" in words or "clothes" in words:
                print("e key input")
            elif "quit" in words or "kit" in words or "leave" in words or "leaf" in words or "wit" in words or "wet" in words:
                print("quit input")
                return

            # Wait a split second before getting more input from the microphone
            await asyncio.sleep(1)

asyncio.run(speech_mode())