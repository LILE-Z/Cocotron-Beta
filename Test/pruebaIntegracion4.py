import sounddevice as sd
import numpy as np
from pynput import keyboard
import threading
import io
import speech_recognition as sr
import wave

SAMPLE_RATE  = 44100
CHANNELS = 2
GAIN = 3.0

audio_data = []
recording = False
stream = None

recognizer = sr.Recognizer()

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
        print("Te estoy escuchando...")

def on_release(key):
    global recording
    if key == keyboard.Key.space and recording:
        recording = False
        print("Ya terminé de escuchar", flush=True)
        
        # Convertir la lista de audio a un array de numpy
        audio_array = np.array(audio_data)
        
        # Aplicar ganancia y recortar valores fuera del rango [-1, 1]
        audio_array = audio_array * GAIN
        audio_array = np.clip(audio_array, -1.0, 1.0)
        
        # Convertir a formato PCM WAV adecuado
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 2 bytes por muestra (16 bits)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())

        audio_buffer.seek(0)  # Resetear el puntero del buffer al inicio

        # Pasar el buffer a un objeto AudioFile de speech_recognition
        with sr.AudioFile(audio_buffer) as source:
            audio = recognizer.record(source)
            try:
                # Reconocimiento de voz utilizando Google
                text = recognizer.recognize_google(audio, language="es-ES")
                print("Esto es lo que entendí: " + text)
            except sr.UnknownValueError:
                print("No entendí lo que dijiste.")
            except sr.RequestError as e:
                print("No se pudo solicitar resultados del servicio de Google; {0}".format(e))

        print("Presiona el espacio para hablar")
        return False

def main():
    print("Presiona el espacio para hablar")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
