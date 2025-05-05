import requests
import json
import io
# Configuración
subscription_key = ""
region = "eastus"


def text2Speech(text):
    endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"

    # Configura los encabezados
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
        'User-Agent': 'YOUR_RESOURCE_NAME'
    }

    # Define el contenido en SSML
    ssml = f"""
    <speak version='1.0' xml:lang='es-ES'>
        <voice xml:lang='es-ES' xml:gender='Male' name='es-MX-JorgeNeural'>
            <prosody pitch="-17%"> {text} </prosody>
        </voice>
    </speak>
    """

    # Realiza la solicitud a la API
    response = requests.post(endpoint, headers=headers,
                             data=ssml.encode('utf-8'))
    # Verifica la respuesta y guarda el audio resultante
    if response.status_code == 200:

        audio_bytes = io.BytesIO(response.content)
        return audio_bytes
        # print("El archivo de audio se guardó como 'output.mp3'")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def speech2Text(audio_bytes):
    endpoint = f"https://{
        region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=es-MX"

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'audio/wav',
        'Accept': 'application/json'
    }

    audio_data = audio_bytes.read()
    # Solicita el reconocimiento de voz
    response = requests.post(endpoint, headers=headers, data=audio_data)

    # Muestra el resultado
    if response.status_code == 200:
        dict = json.loads(response.text)
        return dict["DisplayText"]
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def reconocerAudio(audio_bytes):
    return speech2Text(audio_bytes)


def generarVoz(text):
    return text2Speech(text)


if __name__ == "__main__":
    import micro
    if False:

        import time

        micro.iniciarGrabacion()
        print("Grabando")
        time.sleep(5)
        micro.deternerGrabacion()
        print("Terminado")
        obj = micro.devolverAudio()
        print(speech2Text(obj))
    else:
        # micro.reproducirAudioMP3(text2Speech("¡jááááá jááá jááá jááá jááá jáá, jáááá!"))
        micro.reproducirAudioMP3(text2Speech(
            "¡Jaah jaaah jaah jah jah jaaah!"))
