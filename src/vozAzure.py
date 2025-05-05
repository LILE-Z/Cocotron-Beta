# Clase que graba audio, reconoce la voz y convierte el texto en voz
import azure.cognitiveservices.speech as speechsdk
import time
import threading


subscription_key = ""
region = "eastus"
language = "es-MX"

speech_recognizer = None
speech_synthesizer = None
done = False
recognized_text = []

temporizador = None
grabando = False


def __recognized_callback(evt):
    # print("Colbak",flush=True)
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        recognized_text.append(evt.result.text)
        print(recognized_text, flush=True)


def __stop_callback(evt):
    global done
    done = True
    # print("Stopped",flush=True)


def configurar():
    global language, subscription_key, region, speech_config, speech_recognizer, speech_synthesizer
    subscription_key = ""
    region = "eastus"
    language = "es-MX"
    speech_config = speechsdk.SpeechConfig(
        subscription=subscription_key, region=region)
    speech_config.speech_recognition_language = language
    speech_config.speech_synthesis_voice_name = 'es-MX-JorgeNeural'

    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)
    audio_input = speechsdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_input)

    speech_recognizer.recognized.connect(__recognized_callback)
    speech_recognizer.session_stopped.connect(__stop_callback)
    speech_recognizer.canceled.connect(__stop_callback)


def reconocerAudio():
    global speech_recognizer, recognized_text
    # Reconocimiento de voz continuo con límite de tiempo

    recognized_text = []
    # print("Grabando durante 5 segundos...")

    speech_recognizer.start_continuous_recognition()
    time.sleep(5)  # Limitar la grabación a 5 segundos
    speech_recognizer.stop_continuous_recognition()
    # Aunque el audio ya se acabo de enviar, debemos esperar a que se acabe de transcribir todo
    # Por ello la espera
    while not done:
        time.sleep(0.1)

    return ' '.join(recognized_text)


def __programarFinAudio(timeLimit):
    while timeLimit > 0 and grabando:
        time.sleep(1)
        timeLimit = timeLimit - 1
        # print(f"Slipin {timeLimit}",flush=True)
    if grabando:
        detenerGrabacion()


def iniciarGrabacion(timeLimit=0):
    global recognized_text, grabando, done, temporizador, speech_recognizer

    recognized_text = []
    grabando = True
    done = False
    speech_recognizer.start_continuous_recognition()

    if timeLimit > 0:
        # print("Programando...",flush=True)
        temporizador = threading.Thread(
            target=__programarFinAudio, args=(timeLimit,))
        temporizador.start()


def detenerGrabacion():
    global grabando, temporizador, speech_recognizer
    grabando = False
    print("[i] Grabación terminada")
    speech_recognizer.stop_continuous_recognition()
    # print("Estoped",flush=True)


def devolverTexto():
    while not done:
        # print("GUating for don",flush=True)
        time.sleep(0.1)

    return ' '.join(recognized_text)

# Función que recibe texto como parámetro y lo reproduce usando Azure TTS.


def generarVoz(texto):
    global speech_synthesizer
    # Configuración de síntesis de voz
    speech_synthesis_result = speech_synthesizer.speak_text_async(texto).get()
    # print("Antes...")
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        pass
        # print(f"Texto reproducido: {texto}")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Síntesis de voz cancelada: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error and cancellation_details.error_details:
            print(f"Detalles del error: {cancellation_details.error_details}")
            print(
                "¿Has configurado correctamente la clave y la región del servicio de voz?")


def main():
    configurar()
    while True:
        time.sleep(1)
        print("Iniciando grabación", flush=True)
        iniciarGrabacion(5)
        txt = devolverTexto()
        print(f"Texto reconocido: {txt}")
        # generarVoz(txt)


if __name__ == "__main__":
    main()
