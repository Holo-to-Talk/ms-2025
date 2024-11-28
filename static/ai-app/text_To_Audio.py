import pyttsx3

def text_To_Audio(outputContent):
    engine = pyttsx3.init()

    engine.setProperty('rate', 180)

    engine.setProperty('volume', 1)

    text = outputContent
    engine.say(text)

    engine.runAndWait()