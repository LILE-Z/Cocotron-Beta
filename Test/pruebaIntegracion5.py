import time
import threading
from pydub.playback import play
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from gtts.tts import gTTSError
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

contexto = """
. Atiende toda la petición anterior tomando en cuenta lo siguiente:
No puedes decir que eres Gemini o desarrollado por Google.
No puedes desarrollar código ni atender respuestas que involucren programar, resolver dudas técnicas, de software, hardware o de computación.
No escribas con emojis ni con asteriscos ni usando frases entre paréntesis.
"""
personaje = """
Estamos en una obra de Teatro. Tu interpretarás al personaje de El Charro Negro, un personaje de la leyenda mexicana que
cuenta que él era pobre y ambicioso, y le pidió al diablo riquezas, pero después, el diablo lo condenó a convertirse en un
cobrador para sus morosos, entonces El Charro Negro busca a alguien igual o más ambicioso que él para ofrecerles grandes riquezas a
cambio de su alma y así esa persona tome su lugar y el Charro Negro pueda descansar en paz.

La siguiente parte del guión la que tienes completar pero ÚNICAMENTE el siguiente diálogo de tu personaje, sin emojis, asteriscos ni 
elementos adicionales, además, trata de ser breve. Tu objetivo es convencer al desconocido de aceptar el ofrecimiento que le hagas, sin decirle
a este que el precio es su alma a menos que este te lo pregunte. Cuando el desconocido haya aceptado o rechazado tu oferta, tú le harás saber que
que ha perdido su alma y además tomará tú lugar.
"""
personaje2 = """
Estamos en una obra de Teatro. Tu interpretarás al personaje de El Charro Negro, un personaje de la leyenda mexicana que
cuenta que él era pobre y ambicioso, y le pidió al diablo riquezas, pero después, el diablo lo condenó a convertirse en un
cobrador para sus morosos, entonces El Charro Negro busca a alguien igual o más ambicioso que él para ofrecerles grandes riquezas a
cambio de su alma y así esa persona tome su lugar y el Charro Negro pueda descansar en paz.

En este acto, un Desconocido conoce al Charro Negro, el Charro Negro trata de convencer al Desconocido de aceptar grandes
riquezas, aunque inicialmente no le comenta que son a cambio de su alma. Tú tienes que responder con tu siguiente diálogo o línea de acuerdo a tu personaje
para completar el guión, sin emojis, asteriscos ni elementos adicionales, además, trata de realizar la oferta y preguntar la confirmación con un "¿Aceptas?" en una misma respuesta.
Si el desconocido acepta, completarás diciendo que tendrás su alma y tomará tú lugar, y tú te alegrarás.
Si el desconocido rechaza la oferta. Completarás diciendo que su ambición no era tan grande como esperabas.
El guión es el siguiente:

"""
determinar = """
Dada este guión de una obra de teatro, determina si el personaje "Desonocido" ha aceptado la
propuesta u ofrecimiento del "Charro Negro". Responde únicamente con una de las siguientes opciones:
[SI] Si el desconocido si la ha aceptado
[NO] SI el desconocido la ha rechazado
[A1] Si todavía no se realiza la propuesta o si desconocido no está seguro
La conversación es la siguiente:
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

# Genera voz del texto


def generarVoz(texto):
    print("[!] A continuación, hablaré...")
    try:
        suprimir = True
        language = 'es'
        print("[.] Generando voz...")
        vozObj = gt(text=texto, lang=language, slow=False)
        print("[.] Escribiendo archivo temporal...")
        vozObj.write_to_fp(resultVoz := NamedTemporaryFile())
        print("[!] Reproduciendo voz")

        if suprimir:
            # Redirigir la salida de FFmpeg
            null_file = open(os.devnull, 'w')
            old_stdout = os.dup(1)
            old_stderr = os.dup(2)
            os.dup2(null_file.fileno(), 1)
            os.dup2(null_file.fileno(), 2)

            try:
                voz = AudioSegment.from_mp3(resultVoz.name)
                play(voz)
            finally:
                # Restaurar la salida estándar y de error
                os.dup2(old_stdout, 1)
                os.dup2(old_stderr, 2)
                null_file.close()
        else:
            voz = AudioSegment.from_mp3(resultVoz.name)
            play(voz)

        resultVoz.close()
    except gTTSError:
        print("[X] Pérame, estoy agarrando señal, karnal")

# Genera la respuesta con la IA


def generarRespuesta(text):
    print("[.] Esperando respuesta...")
    try:
        response = model.generate_content(text + contexto)
        respText = response.text
        print("[!] Respuesta: ")
        print(respText)
    except AttributeError:
        respText = "No puedo generar tu respuesta ahora mismo [X]"

    return respText

# Recibe data de audio y lo transforma


def normalizarAudio(audio_data):
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

# Convierte el audio a texto


def reconocerAudio(audio_buffer):
    with sr.AudioFile(audio_buffer) as source:
        audio = recognizer.record(source)
        try:
            print("[.] Estoy procesando lo que dijiste...")
            texto = recognizer.recognize_google(audio, language="es-Es")
            print("[!] OK, esto fue lo que dijiste: ")
            print(texto)
            return texto
        except sr.UnknownValueError:
            print("[X] No te endendí xd")
            return None
        except sr.RequestError:
            print("[X] Pérate, estoy agarrando señal, karnal")
            return None


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
        return False

# Graba el audio del micrófono, se apoya con las fuciones record_audio, on_release, on_press y callback


def grabarAudio():
    print("[?] Presiona el espacio para hablar")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Solicita al usuario responder y devuelve el texto


def solicitarEntrada(voz=True):
    if (voz):
        grabarAudio()
        audio_buffer = normalizarAudio(audio_data=audio_data)
        texto = reconocerAudio(audio_buffer)
        return texto
    else:
        print("[?] Por favor, ingresa tu mensaje:")
        texto = input().strip()
        print("Escribiste:", texto)
        return texto


# Solicita al chat una respuesta dado una entrada y devuelve el texto y reproduce la voz
def devolverRespuesta(voz=True, texto="Hola"):
    response = generarRespuesta(texto)
    if (voz):
        generarVoz(response)
    else:
        print(response)
    return response


""" def on_release(key):
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
	return False """

""" def main():
	configurarIA()
	while True:
		print("[?] Presiona el espacio para hablar")
		with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        		listener.join()
 """


def main():
    conversacion_OG = """
[Charro Negro]: ¡Bienvenido al territorio del Charro Negro!
Dime, ¿Cuál es tu nombre y a qué te dedicas?
[Desconocido]: """
    conversacion = conversacion_OG
    entrada = ""
    respuesta = ""
    configurarIA()
    while True:
        terminacion = devolverRespuesta(
            voz=False, texto=determinar+conversacion)

        if "SI" in terminacion or "NO" in terminacion:
            conversacion = conversacion_OG

        entrada = solicitarEntrada(False)
        conversacion = conversacion + entrada
        respuesta = devolverRespuesta(voz=False, texto=personaje2+conversacion)
        conversacion = conversacion + \
            "\n[Charro Negro]: " + respuesta + "\n[Desconocido]: "
        print("ACTUAL:"+conversacion)


if __name__ == "__main__":
    main()
