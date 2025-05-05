import speech_recognition as sr

recognizer = sr.Recognizer()

def reconocerAudio(audio_buffer):
    with sr.AudioFile(audio_buffer) as source:
        audio = recognizer.record(source)
        try:       
            texto = recognizer.recognize_google(audio, language="es-Es")
            return texto
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:          
            return ""

def main():
    import micro
    from time import sleep

    micro.iniciarGrabacion()
    print("Grabando...")
    sleep(5)
    print("Terminado de escuchar")
    micro.deternerGrabacion()
    resp = reconocerAudio(micro.devolverAudio())
    if resp:
        print("Dijiste: "+ resp)
    else:
        print("No te endendí")

if __name__ == "__main__":
    main()