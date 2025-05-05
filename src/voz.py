import os
from gtts import gTTS as gt
from gtts.tts import gTTSError
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO



# Genera y reproduce la voz
def generarVoz(texto):
    try:
        suprimir_salida = True
        language = 'es'

        vozObj = gt(text=texto, lang=language, slow=False)

        vozObj.write_to_fp(resultVoz := NamedTemporaryFile())

        #mp3_fp = BytesIO()
        #vozObj.write_to_fp(mp3_fp)
        #with open("output.mp3", "wb") as f:
        #    f.write(mp3_fp.getbuffer())

        if suprimir_salida:
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
        return 0
    except gTTSError:
        return 1
    
def main():
    generarVoz("El Otorrinolaringólogo de parangaricutirimícuaro me diagnosticó hipopotomonstrosesquipedaliofobia");

if __name__ == "__main__":
    main()