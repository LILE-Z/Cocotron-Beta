# Clase que graba el audio del micrófono
import sounddevice as sd
import io
import wave
import numpy as np
import threading
import time
from pydub import AudioSegment

SAMPLE_RATE  = 44100
CHANNELS = 1
GAIN = 3.0
audio_data = []
recording = False
ready = False

# Aumentar el volumen del audio
def __normalizarAudio(audio_data):
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
    return audio_buffer

# Método que se llama al terminar de grabar
def __callback(indata, frames, time, status):
    global audio_data, ready
    audio_data.extend(indata.copy())
    ready = True

# Hilo de grabar audio 
def __grabar_audio():
    global stream, recording
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=__callback) as stream:
        while recording:
            sd.sleep(100)
    
# Crea un hilo nuevo e inicia la grabación
def iniciarGrabacion():
    global audio_data, recording, ready
    audio_data = []
    recording = True
    ready = False
    threading.Thread(target=__grabar_audio).start()
    
# Detiene la grabación 
def deternerGrabacion():
    global recording
    time.sleep(0.5)
    recording = False

# Devuelve el objeto de audio
def devolverAudio():
    global audio_data
    while not ready:
        pass
    return __normalizarAudio(audio_data)

def reproducirAudioWAV(audio_buffer):
    # Leer el audio del buffer
    with wave.open(audio_buffer, 'rb') as wf:
        audio_data = wf.readframes(wf.getnframes())
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_array = audio_array.astype(np.float32) / 32767.0  # Normalizar a [-1.0, 1.0]

    # Reproducir el audio
    sd.play(audio_array, samplerate=SAMPLE_RATE)
    sd.wait()  # Esperar hasta que termine la reproducción

def reproducirAudioMP3(audio_buffer):
    # Leer el audio MP3 del buffer
    audio = AudioSegment.from_file(io.BytesIO(audio_buffer.getvalue()), format="mp3")

    # Convertir el audio a un array numpy
    audio_array = np.array(audio.get_array_of_samples()).astype(np.float32) / 32767.0

    # Reproducir el audio
    sd.play(audio_array, samplerate=16000)  # Usar 16kHz como frecuencia de muestreo
    sd.wait()  # Esperar hasta que termine la reproducción


def main():
    global audio_data
    print("Escuchando... ")
    iniciarGrabacion()
    time.sleep(5)
    print("Terminado de escuchar")
    deternerGrabacion()

    objeto = devolverAudio()

    print("Reproduciendo audio...")
    reproducirAudioWAV(objeto)
    print("Reproducción terminada")
    pass

if __name__ == "__main__":
    main()