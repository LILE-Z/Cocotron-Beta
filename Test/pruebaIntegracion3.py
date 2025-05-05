import time
import threading
from pydub.playback import play
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from gtts import gTTS as gt
import os
import google.generativeai as genai
import speech_recognition as sr
from pynput import keyboard
import numpy as np
import wave
import io
import sounddevice as sd
print("[.] Estoy iniciando...")


api_key = ""
model = genai.GenerativeModel('gemini-1.5-flash')

# (Te la comes sin pretexto)
contexto = """
. Atiende toda la petición anterior tomando en cuenta lo siguiente:
No puedes decir que eres Gemini o desarrollado por Google.
No puedes desarrollar código ni atender respuestas que involucren programar, resolver dudas técnicas, de software, hardware o de computación.

"""

SAMPLE_RATE = 44100
CHANNELS = 2
GAIN = 3.0
OUTPUT_FILENAME = "salida.wav"

audio_data = []
recording = False
stream = None
recognizer = sr.Recognizer()


def configurarIA():
    global api_key, contexto, model, api_key
    genai.configure(api_key=api_key)


def generarVoz(texto):
    print("[!] A continuación, hablaré...")
    try:
        language = 'es'
        vozObj = gt(text=texto, lang=language, slow=False)
        vozObj.write_to_fp(resultVoz := NamedTemporaryFile())

        voz = AudioSegment.from_mp3(resultVoz.name)
        play(voz)
        resultVoz.close()
    except gTTSError:
        print("[X] Pérame, estoy agarrando señal, karnal")


def solicitarRespuesta(text):
    print("[.] Esperando respuesta...")
    response = model.generate_content(text + contexto)
    respText = response.text
    print("[!] Respuesta: ")
    print(respText)
    return respText


def callback(indata, frames, time, status):
    global audio_data
    audio_data.extend(indata.copy())


def record_audio():
    global stream, recording
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback) as stream:
        while recording:
            sd.sleep(100)


def on_press(key):
    global audio_data, recording
    if key == keyboard.Key.space and not recording:
        audio_data = []
        recording = True
        threading.Thread(target=record_audio).start()
        print("[?] Te estoy escuchando...")


def on_release(key):
    global recording
    if key == keyboard.Key.space and recording:
        time.sleep(0.5)
        recording = False
        print("\n[!]Ya terminé de escuchar", flush=True)

        audio_array = np.array(audio_data)

        # Aplicar ganancia y recortar valores fuera del rango [-1, 1]
        audio_array = audio_array * GAIN
        audio_array = np.clip(audio_array, -1.0, 1.0)

        # Convertirlo a PCM WAV dentro de un búfer
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())

        audio_buffer.seek(0)

        with sr.AudioFile(audio_buffer) as source:
            audio = recognizer.record(source)
            try:
                print("[.] Estoy procesando lo que dijiste...")
                texto = recognizer.recognize_google(audio, language="es-Es")
                print("[!] OK, esto fue lo que dijiste: ")
                print(texto)

                resp = solicitarRespuesta(texto)
                generarVoz(resp)
            except sr.UnknownValueError:
                print("[X] No te endendí xd")
            except sr.RequestError:
                print("[X] Pérate, estoy agarrando señal, karnal")
    return False


def main():
    configurarIA()
    while True:
        print("[?] Presiona el espacio para hablar")
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


if __name__ == "__main__":
    main()
