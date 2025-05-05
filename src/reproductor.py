# Reproduce Audios
"""import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment

def reproducirAudio(archivo):  
    audio = AudioSegment.from_mp3(archivo)
    audio.export('temp.wav', format='wav')
    # Leer el archivo WAV usando soundfile
    data, samplerate = sf.read('temp.wav')
    # Reproducir el audio usaalndo sounddevice
    sd.play(data, samplerate)
    sd.wait()  
    # Esperar a que termine la reproducción"""

from playsound import playsound

def reproducirAudio(archivo):
    playsound('ruta/al/archivo.mp3')

def main():
    reproducirAudio('output.mp3')
    pass

if __name__ == "__main__":
    main()