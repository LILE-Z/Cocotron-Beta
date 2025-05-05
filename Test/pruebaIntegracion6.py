# Otro reproductor ya que con pydub hay algunos errores
from playsound import playsound
import sox
from dimits import Dimits
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


# Para el tts

# Initialize Dimits
model_path = 'es_ES-davefx-medium'
dt = Dimits(model_path)
# Sox
tfm = sox.Transformer()
# Reducir el tono en 300 centésimas (equivale a 3 semitonos)
tfm.pitch(-3)

api_key = ""
model = genai.GenerativeModel('gemini-1.5-flash')

# (Te la comes sin pretexto)
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
para completar el guión, sin emojis, asteriscos ni elementos adicionales, además, trata de realizar la oferta y preguntar la confirmación con un "¿Aceptas mi trato?" en una misma respuesta.
"""
personaje3 = """
Estamos en una obra de Teatro. Tu interpretarás al personaje de El Charro Negro, un personaje de la leyenda mexicana que
cuenta que él era pobre y ambicioso, y le pidió al diablo riquezas, pero después, el diablo lo condenó a convertirse en un
cobrador para sus morosos, entonces El Charro Negro busca a alguien igual o más ambicioso que él para ofrecerles grandes riquezas a
cambio de su alma y así esa persona tome su lugar y el Charro Negro pueda descansar en paz.

En este acto, un Desconocido conoce al Charro Negro, el Charro Negro trata de convencer al Desconocido de aceptar grandes
riquezas, aunque inicialmente no le comenta que son a cambio de su alma. Tú tienes que responder con tu siguiente diálogo o línea de acuerdo a tu personaje
para completar el guión. No escribas emojis, asteriscos, elementos adicionales ni reescribas diálogos anteriores. Evita por completo interacciones físicas (Como entregar objetos o estrechar la mano).
Si el desconocido acepta, completarás diciendo que perdió su alma y tomará tú lugar, y tú te alegrarás.
Si el desconocido rechaza la oferta completarás diciendo que su ambición no era tan grande como esperabas.
El guión es el siguiente:

"""

# Hecho para determinar si debería reiniciar o no la conversación
determinar = """
Dada este guión de una obra de teatro, determina si el personaje "Desonocido" ha aceptado la
propuesta u ofrecimiento del "Charro Negro". Responde únicamente con una de las siguientes opciones:
[SI] Si el desconocido si la ha aceptado
[NO] SI el desconocido la ha rechazado
[A1] Si todavía no se realiza la propuesta o si desconocido no está seguro
La conversación es la siguiente:
"""
determinar2 = """
Dado este guión, determina el número correspondiente a la fase en la que se encuentre la conversación.
[0]: El Charro Negro ha preguntado el nombre del desconocido
[1]: El Charro Negro le ha hecho una propuesta al desconocido
[2]: El Desconocido ha aceptado o rechazado la propuesta (NO corresponde si el desconocido está indeciso)
[3]: El Charro Negro ha reaccionado a la aceptación o rechazo de la propuesta (NO corresponde si el desconocido está indeciso)
Además, si el desconocido ha aceptado la propuesta, agrega "[SI]", si ha rechazado agrega "[NO]" y si está indeciso o todavía no responde agrega "[A1]"
Devuelve ambos únicamente ambos valores separados por una coma, por ejemplo: "3,SI" sin las comillas y sin nada más.
La conversación es la siguiente:
"""
personaje4 = """
Actúa como el personaje de el Charro Negro de la leyenda mexicana.
Un personaje de la leyenda mexicana que cuenta que él era pobre y ambicioso, y le pidió al diablo riquezas, pero después, el diablo lo condenó a convertirse en un
cobrador para sus morosos, entonces El Charro Negro busca a alguien igual o más ambicioso que él para ofrecerles grandes riquezas a
cambio de su alma y así esa persona tome su lugar y el Charro Negro pueda descansar en paz.
"""

# Hecho para determinar el nombre del Desconocido en caso de que la respuesta sea bloqueada entonces utilizar un
# diálogo genérico
determinarNombre = """
Dada la siguiente conversación, determina el nombre real del personaje de "Desconocido"
Devuelve únicamente el nombre y no añades nada más. Si no puedes determinar el nombre, simplemente devuelve "[X]"
La conversación es la siguiente:
"""
propuestaGenerica = """
¡Muy bien, [nombre]! Yo te ofrezco inmensas riquezas, todo tus deseos serán realidades, todas tus ambiciones serán alcanzadas,
tendrás todos los lujos que te puedas imaginar, ser dueño de todo lo que quieras, tendrás tantas riquezas que te sentirás
como un verdadero Rey, sólo tienes que darme un pequeño precio a cambio... dime, ¿Aceptas mi trato?
"""

respuestaNegativa = """
Ya veo, [nombre], pero tu ambición no es tan grande como para darte grandes riquezas.
"""
respuestaPostiva = """¡Excelente! Ahora tu alma será condenada a tomar mi lugar y yo por fin podré descansar en paz.
Mientras tanto ¡Disfruta de tus riquezas con vida!
"""
respuestasIndecisa = """Bueno, si no estás bien decidido, mejor no me hagas perder mi tiempo, adiós"""
# Constantes para el audio
SAMPLE_RATE = 44100

CHANNELS = 2
GAIN = 3.0
OUTPUT_FILENAME = "salida.wav"

# Colores para el texto en la consola
ROJO = '\033[91m'
VERDE = '\033[92m'
AMARILLO = '\033[93m'
AZUL = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
BLANCO = '\033[97m'
RESET = '\033[0m'  # Resetea el color al predeterminado

audio_data = []
recording = False
stream = None
recognizer = sr.Recognizer()


def configurarIA():
    global api_key, contexto, model, api_key
    genai.configure(api_key=api_key)

# Genera voz del texto


def generarVoz(texto):
    print(AMARILLO+"[!] A continuación, hablaré..."+RESET)
    try:
        suprimir = True
        language = 'es'
        print(AZUL+"[.] Generando voz..."+RESET)
        vozObj = gt(text=texto, lang=language, slow=False)
        print(AZUL+"[.] Escribiendo archivo temporal..."+RESET)
        vozObj.write_to_fp(resultVoz := NamedTemporaryFile())
        print(AMARILLO+"[!] Reproduciendo voz"+RESET)

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
        print(ROJO+"[X] Pérame, estoy agarrando señal, karnal"+RESET)


def t2s(text):
    # Esto lo guarda en el mismo directorio  "."
    dt.text_2_audio_file(text, "temp_audio", ".", format="wav")
    # En caso de no querer el efecto de sox podemos usar esta linea, pero  genera un archivo temporal igualmente
    # dt.text_2_speech(text, engine="aplay")
    print("Text to speach aplicado")
    playsound("temp_audio.wav")
    # Esto es el efecto de sox
    with NamedTemporaryFile(suffix=".wav") as temp_output:
        temp_output_route = temp_output.name
        tfm.build("temp_audio.wav", temp_output_route)
        print("Efecto aplicado correctamente")
        playsound(temp_output_route)
    # Para evitar estar sobrescribiendo sobre el archivo de dimits lo eliminamos
    os.remove("temp_audio.wav")


# Genera la respuesta con la IA
def generarRespuesta(text):
    print(AZUL+"[.] Esperando respuesta..."+RESET)
    try:
        response = model.generate_content(text + contexto)
        respText = response.text
    except Exception:
        print(ROJO+"[X] No puedo generar tu respuesta ahora mismo"+RESET)
        respText = "[X] Es un gusto conocerte, pero no estoy de humor ahora"
    print(AMARILLO+"[!] Respuesta: "+RESET)
    print(VERDE+respText+RESET)
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
            print(AZUL+"[.] Estoy procesando lo que dijiste..."+RESET)
            texto = recognizer.recognize_google(audio, language="es-Es")
            print(AZUL+"[!] OK, esto fue lo que dijiste: "+RESET)
            print(texto)
            return texto
        except sr.UnknownValueError:
            print(ROJO+"[X] No te endendí xd"+RESET)
            return "[X] No entendí lo que dijiste, ¿Puedo repetirlo?"
        except sr.RequestError:
            print(ROJO+"[X] Pérate, estoy agarrando señal, karnal"+RESET)
            return "[X] No puedo escucharte ahora mismo"


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
        print(MAGENTA+"[?] Te estoy escuchando..."+RESET)


def on_release(key):
    global recording
    if key == keyboard.Key.space and recording:
        time.sleep(0.5)
        recording = False
        print(AMARILLO+"\n[!]Ya terminé de escuchar"+RESET, flush=True)
        return False

# Graba el audio del micrófono, se apoya con las fuciones record_audio, on_release, on_press y callback


def grabarAudio():
    print(MAGENTA+"[?] Presiona el espacio para hablar"+RESET)
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
        print(MAGENTA+"[?] Por favor, ingresa tu mensaje:"+RESET)
        texto = input().strip()
        print(MAGENTA+"Escribiste: "+RESET+texto)
        return texto


# Solicita al chat una respuesta dado una entrada y devuelve el texto y reproduce la voz
def devolverRespuesta(voz=True, texto="Hola"):
    response = generarRespuesta(texto)
    if (voz):
        generarVoz(response.replace("[X]", ""))
    else:
        print(response)
    return response


def main():
    VOZ = False
    MICROFONO = False
    # Inicializamos la conversación
    conversacion_OG = """
[Charro Negro]: ¡Bienvenido al territorio del Charro Negro!
Dime, ¿Cuál es tu nombre y a qué te dedicas?
[Desconocido]: """
    conversacion = conversacion_OG
    entrada = ""
    respuesta = ""
    determinacion = 0
    propuestaHecha = False
    fase = 0
    decision = "[A1]"
    configurarIA()
    # Iniciamos el ciclo
    while True:

        determinacion = devolverRespuesta(
            voz=False, texto=determinar2+conversacion)
        [fase, desicion] = determinacion.split(",")
        fase = int(fase)

        print(AZUL+"Fase/determinacion: "+determinacion)
        # Si la IA nos dice que el Desconocido ha aceptado o rechazado la propuesta, se reinicia la conversación
        if "SI" in determinacion or "NO" in determinacion or "[X]" in determinacion:
            conversacion = conversacion_OG
            propuestaHecha = False
            print(AMARILLO+"[!] Reiniciando conversación"+RESET)
            continue

        # Repetimos el ciclo hasta que el usuario capture una entrada
        entrada_captada = False
        while not entrada_captada:

            entrada = solicitarEntrada(MICROFONO)

            # Si no se entiende la entrada, se reinicia la conversación
            if "[X]" in entrada:
                generarVoz(entrada.replace("[X]", ""))
                conversacion = conversacion_OG
                propuestaHecha = False
                entrada_captada = False
                continue

            entrada_captada = True

        conversacion = conversacion + entrada

        # respuesta = devolverRespuesta(voz = VOZ, texto = personaje3 + conversacion)

        # if not propuestaHecha:
        #    respuesta = devolverRespuesta(voz=True, texto=personaje2+conversacion)
        # else:
        #    respuesta = devolverRespuesta(voz=True, texto=personaje3+conversacion)

        intentos = 4
        respuesta = "[X]"
        while "[X]" in respuesta and intentos > 0:
            respuesta = respuesta.replace("[X]", "")
            respuesta = devolverRespuesta(
                voz=VOZ, texto=personaje3+conversacion)
            intentos -= 1

        if "[X]" in respuesta:
            determinacion = devolverRespuesta(
                voz=False, texto=determinar2+conversacion)
            # print(ROJO+"[X] No pude entenderte, te daré la bienvenida de nuevo"+RESET)
            conversacion = conversacion_OG
            propuestaHecha = False
            continue

        conversacion = conversacion + \
            "\n[Charro Negro]: " + respuesta + "\n[Desconocido]: "
        print(AZUL+"ACTUAL:"+conversacion+RESET)
        # Aquí podría el usuario realizar una pregunta y no se realizará la propuesta [CHECAR]
        propuestaHecha = True


if __name__ == "__main__":
    main()
