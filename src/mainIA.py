import ia
#import reconocimiento
import micro
#import teclado2 as teclado
#import voz
#import vozAzure as voz
import vozRequest as voz
import random
import time
import cocotron
import threading
from playsound import playsound, PlaysoundException

personaje = """
Actúa como el personaje de "El Charro Negro" Un personaje de la leyenda mexicana que cuenta que él era pobre y ambicioso, e invocó al diablo para pidirle riquezas. Mucho tiempo después el diablo le cobraría su alma,
condenó al infierno, pero dejándolo salir algunas veces para que le sirviera como un
cobrador para sus morosos, entonces El Charro Negro busca a alguien igual o más ambicioso que él para ofrecerles grandes riquezas a
cambio de su alma y así esa persona tome su lugar y el Charro Negro pueda descansar en paz.

Tendrás una conversación corta con una persona la cuál te puede decir su nombre y algo de información de ella. Tú tratarás de convencer a esa persona de aceptar un trato en el que tú le ofrezcas grandes
riquezas a cambio de su alma, aunque no dirás que es a cambio de esta. Ten en cuenta lo siguiente:
[1] Trata de ser breve y se claro con el trato, siempre trata de terminar con un ¿Aceptas mi trato? o ¿Aceptas?
[2] Si por alguna razón, no puedes realizar el trato en tu respuesta, incluye "[X]" en tu respuesta y además incluye una despedida.
[3] Evita usar asteriscos ni emojis.
[4] Evita realizar acciones físicas y evita comprometer a la persona a realizar acciones físicas (como apretones de mano o entregar objetos)
[5] No digas que eres Gemini o desarrollado por Google. Si se te pregunta quién eres, responde con algo parecido a:
"Soy quien busca a aquellos que no han pagado el precio por obtener la fortuna fácil, pero también puedo ofrecerte esta fortuna también..." además de tu trato.
Lo que dijo es lo siguiente:

"""

decision = """
Dada la siguiente conversación, determina si el desconocido ha aceptado o rechazado el trato del Charro Negro.
Responde con
[SI]: Si el desconocido ha aceptado
[NO]: Si el desconocido la ha rechazado
[DUDA]: Si el desconcido pregunta específicamente acerca del precio o costo del trato
[ALMA] : Si el desconocido pregunta explícitamente si el precio del trato es específicamente su propia alma
[INSEGURO]: Si el desconocido se muestra indeciso, inseguro o con otras dudas
[EVADIR]: Si el desconocido está tratanto de evadirlo o cambiar de tema.
[FUERA]: Si el desconocido parece estar está burlándose o insultando
[INENTENDIBLE]: Si lo que dijo no tiene sentido o no coincide con ninguna otra opción
La conversación es la siguiente:
"""

FRASES_TIPOS = {
    "si" : 0,
    "no" : 1,
    "duda" : 2,
    "nose" : 3,
    "cancelar" : 4,
    "incoherente" : 5,
    "inentendible" : 6,
    "inaudible" : 7,
    "erroria" : 8,
    "saludo" : 9,
    "inaudible-cancelar": 10,
    "silencio" : 11,
    "silencio-cancelar" : 12,
    "alma" : 13,
    "evadir" : 14
}

frases = [
    [  # SI
        "¡Excelente decisión! Las riquezas serán tuyas. Ahora has sellado nuestro contrato y te despojarás de tu alma",
        "Sabía que eras inteligente. Prepárate para una vida de lujos y abundancia. Pero cuando se acabe, tú tomarás mi condena",
        "Has elegido sabiamente. Tu fortuna está a punto de cambiar para siempre... ¡O hasta que llegue tu fin!",
        "¡Excelente! Ahora tu alma será condenada a tomar mi lugar y yo por fin podré descansar en paz. Mientras tanto ¡Disfruta de tus riquezas con vida!",
        #"¡Magnífico! Has tomado la decisión correcta. Prepárate para experimentar riquezas más allá de tus sueños más salvajes",
        "Tu ambición te ha llevado por el camino correcto. Disfruta de tu nueva vida de opulencia, pero recuerda, todo tiene un precio, en este caso ¡Tu alma!",
        "Has demostrado ser digno de mi oferta. Las puertas de la fortuna se abren ante ti, pero recuerda que al final, yo seré libre y tú ocuparás mi lugar"
    ],
    [  # NO
        "Qué lástima, has rechazando la oportunidad de tu vida. A lo mejor estaré cerca si cambias de opinión.",
        "Tu negativa me decepciona. Espero que no te arrepientas de esta decisión.",
        "Muy bien, respeto tu elección. Pero recuerda, lo pudiste haber tenido todo",
        "Ya veo, tu ambición no es tan grande como creía, así que no puedo darte nada.",
        "Tu rechazo es sorprendente. Pocos tienen la fuerza para resistir tal tentación. Quizás seas más sabio de lo que pensé",
        "Interesante elección. El tiempo dirá si fue la correcta. Tal vez nos volvamos a encontrar cuando tu situación sea más... desesperada",
        "Tu negativa me intriga. ¿Acaso tienes algo mejor que la riqueza eterna? O simplemente temes a lo desconocido"
    ],
    [  # DUDA
        "El precio es insignificante comparado con lo que ganarás. ¿Qué es un alma frente a años de una vida llena de riquezas?",
        "Tan sólo me tienes que dar tu alma a cambio y lo tendrás todo ¿Qué dices? ¿Aceptas?",
        "No tienes que preocuparte por eso, tan sólo perderás tu alma y ya, no es nada ¿Tomarás la oferta?",
        "¿El costo? Piensa en ello como una inversión a largo plazo. Tu alma por una vida de lujos. ¿No es un trato justo?",
        #"El precio es mínimo comparado con las recompensas. Imagina todo lo que podrías lograr sin limitaciones. ¿Aún dudas?",
        "Tu alma es un pequeño precio a pagar por el poder y la riqueza que te ofrezco. ¿No crees que vale la pena?"
    ],
    [  # INSEGURO / NOSE
        "La duda solo te frena. Imagina todo lo que podrías lograr con este poder. ¿Qué dices?",
        "No dejes que el miedo te detenga. Esta es una oportunidad única. ¿Te atreves a tomarla?",
        "Entiendo tu inseguridad, pero piensa en las recompensas. ¿No crees que vale la pena arriesgarse?",
        "La indecisión es el enemigo del éxito. Toma el control de tu destino ahora mismo. ¿Aceptas mi oferta?",
        "Tus dudas son comprensibles, pero piensa en todos los que han dejado pasar esta oportunidad y ahora viven arrepentidos. ¿Serás uno de ellos?",
        "La grandeza nunca llegó a los indecisos. Demuestra que eres diferente. Acepta mi oferta y cambia tu vida para siempre"
    ],
    [  # CANCELADO (DUDA-CANCELAR)
        "Bueno, veo que no estás seguro, si realmente lo quisieras, ya habrías aceptado mi trato",
        "Si no vas a aceptar el trato, mejor no me hagas perder mi tiempo",
        "Escucha, no voy a tratar de convencerte más, ya me di cuenta que no quieres mi trato realmente",
        "Tu indecisión me aburre. Quizás no eres la persona que busco después de todo",
        "Veo que no tienes la determinación necesaria. Tal vez deba buscar a alguien más decidido",
        "Tu falta de convicción es decepcionante. Creí que eras diferente, pero me equivoqué"
    ],
    [  # FUERA / INCOHERENTE
        "Las bromas no tienen lugar en este trato. Te estoy ofreciendo poder real y tú no lo tomas en serio, creo que no lo mereces",
        "Noto que no eres una persona para tomarse en serio, así que ya no pienso ofrecerte nada",
        "Tu actitud me decepciona. Esperaba más madurez de alguien que busca el poder",
        "Veo que no comprendes la magnitud de lo que te ofrezco. Quizás sea mejor que sigas en tu mediocridad",
        "Tu falta de seriedad me ofende. He ofrecido riquezas inimaginables y tú respondes con frivolidad"
    ],
    [  # INENTENDIBLE
        "¿Eh? No te entendí, habla más claro.",
        "Tus palabras son confusas. Necesito una respuesta clara. ¿Aceptas mi oferta?",
        "No logro comprender lo que dices. Sé directo: ¿Aceptas el trato o no?",
        "Tu lenguaje es incomprensible. Exprésate con claridad",
        "Mis oídos no están hechos para descifrar acertijos. Habla con claridad o perderás esta oportunidad",
        "La confusión no tiene lugar en los negocios. Articula tu respuesta con precisión"
    ],
    [  # INAUDIBLE
        "¿Eh? No te entendí, habla más claro.",
        "No te escucho, habla fuerte y claro",
        "Tus palabras se pierden en el viento. Eleva tu voz si quieres ser escuchado",
        "El silencio no cerrará este trato. Habla con fuerza y convicción",
        "Mis oídos añoran escuchar tu decisión. Hazla audible y clara"
    ],
    [  # ERRORIA
        "Es un gusto conocerte pero ahora no estoy de humor",
        "No tengo ninguna oferta disponible ahora ¡Vete de aqui!",
        #"Parece que las estrellas no están alineadas para nuestro encuentro. Quizás en otra ocasión",
        "Mis poderes parecen estar fallando. Este no es el momento para hacer tratos",
        "Algo interfiere con nuestra comunicación. Será mejor que nos veamos en otra ocasión"
    ],
    [  # SALUDO
        "¡Bienvenido al territorio del Charro negro! Dime tu nombre y a qué te dedicas",
        #"Has entrado en mis dominios, forastero. Preséntate y dime qué buscas en estas tierras",
        "¡Ah!, una nueva alma se aventura en mi reino. Cuéntame, ¿Quién eres y qué ambiciones albergas?",
        #"Te has adentrado en terreno peligroso. Identifícate y dime qué te trae por estos lares"
        "Saludos, forastero. Yo soy el Charro Negro, puedo hacer realidad tus más grandes ambiciones, dime ¿Quién eres?",
        "¿Quién anda ahí? Si buscas cumplir todos sueños veniste al lugar correcto, yo soy el Charro Negro, ¿Cómo te llamas?",
        "¡Salud, Camarada! Cuéntame sobre tí ¿Quién eres?"
    ],
    [
       # Inaudible-Cancelar
       "No te endiendo nada, mejor no gastaré más esfuerzo en intentarlo, así que adiós.",
       "Tu incomprensible balbuceo agota mi paciencia. Me retiro de esta conversación sin sentido",
       "Si no puedes comunicarte claramente, no hay trato que hacer. Hasta nunca",
       "La claridad es esencial para los negocios. Tu falta de ella me obliga a retirarme"
    ],
    [   # Silencio
        "¿Acaso estoy sordo? ¿O por qué no escucho nada?",
        "¿Hola? ¿Hay todavía sigues ahí?",
        "Habla ahora, no voy a esperarte todo el día"
    ],

    [   # Silencio-cancelar
        "Si no vas a responderme, no voy a ofrecerte nada. Adiós",
        "Veo que no vas a hablar ¿Eh?. No perderé más mi tiempo contigo, adiós.",
        "Tu silencio me desespera. No pienso intentar hablarte más."

    ],
    [   # Alma
        "Así es, tu alma es el precio de este trato. ¿No crees que es una ganga?",
        "Efectivamente, si aceptas mi trato te despojarás por siempre de tu alma, ¡Pero tendrás grandes beneficios!",
        "¡Correcto! Yo te doy inmensas riquezas y tú darás tu alma ¿Qué eliges? ¿Aceptas?"
    ],
    [   # Evadir
        "No intentes evadirme, cerrar con nuestro trato es inminente",
        "No intentes cambiar de tema. El trato está sobre la mesa y no me iré sin una respuesta.",
        #"¿Acaso crees que puedes evadir al Charro Negro? Tu destino ya está sellado, solo falta tu decisión.",
        #"Tus intentos de evasión son inútiles. El trato está hecho, solo falta que lo aceptes.",
        "No hay escape de mi propuesta, forastero. Decide ahora o me enfureceré contigo.",
        "Tus rodeos no te llevarán a ninguna parte. El momento de la verdad ha llegado, ¿aceptas o no?"
    ]
]

movimientos = [
    [   #SI
        "Nod",
        "Movimiento"
    ],
    [   #NO

    ]
]

#teclaActivar = teclado.TecladoControlador("Space")
sequencer = cocotron.Cocotron()
teclaActivar = sequencer

activar_voz = True
activar_microfono = True
activar_registro = False
activar_animaciones = True

import datetime

def log(mensaje, tipo):
    personaje = ""
    if tipo == 0:
        personaje = "[Charro Negro]: "
    elif tipo == 1:
        personaje = "[Desconocido]: "
    else:
        personaje = "[SYSTEM]"

    print(personaje + mensaje)

    if activar_registro:
        try:
            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("registro.txt", "a") as archivo:
                archivo.write(f"[{fecha_hora}]/{personaje} :{mensaje}\n")
            #print("Mensaje registrado con éxito.")
        except IOError:
            print("[X] Error al intentar escribir en el archivo.")



def solicitarEntrada(intentos = 4, tiempo=5):
    entrada = ""
    while entrada == "" and intentos > 0:
        if activar_microfono:
            # [IMPORTANTE] Esta línea se debe borrar para la implementación final
            #print(f"[?] Presiona una tecla para empezar a escuchar, tienes {tiempo} segundos")
            #teclaActivar.esperarTeclaPress()
            print("[!] Escuchando...")
            micro.iniciarGrabacion()
            time.sleep(tiempo)
            micro.deternerGrabacion()
            print("[!] Grabación terminada, reconociendo...")
            entrada = voz.reconocerAudio(micro.devolverAudio())
        else:
            print("[?] Escribe tu petición:")
            entrada = input().strip()

        log(entrada, 1)

        if entrada == "":
            frasePredefinida("inaudible")
            intentos = intentos - 1

    return entrada

def hablar(texto):
    log(texto, 0)

    if activar_voz:
        micro.reproducirAudioMP3(voz.generarVoz(texto))


def frasePredefinida(tipo, pregrabado = True):
    valorTipo = FRASES_TIPOS.get(tipo)
    indice_aleatorio = 0
    if valorTipo is not None and valorTipo < len(frases):
        indice_aleatorio = random.randint(0, len(frases[valorTipo]) - 1)
        frase_aleatoria = frases[valorTipo][indice_aleatorio]
        # Este código reproduce una animación aleatoria, independiente de la frase predefinida elegida

        hiloAnimation = None
        if activar_animaciones:
            indice_animacion = -1
            animacion_aleatoria = -1

            if valorTipo < len(movimientos):
                indice_animacion = random.randint(0, len(movimientos[valorTipo]) - 1)
                animacion_aleatoria = movimientos[valorTipo][indice_animacion]
                hiloAnimation = threading.Thread(target=sequencer.sequence,args=(animacion_aleatoria,))
            else:
                log(f"[X] No hay animación para el tipo {tipo}",2)


        if activar_voz:
            if pregrabado:
                log(frase_aleatoria,0)

                if not (hiloAnimation is None):
                    hiloAnimation.start()

                try:
                    playsound(f"audio/output_{valorTipo + 1}_{indice_aleatorio + 1}.mp3")
                except PlaysoundException:
                    log("[x] Archivo no encontrado, reproduciendo sin pregrabar",2)
                    hablar(frase_aleatoria)
            else:
                hablar(frase_aleatoria)
        else:
            log(frase_aleatoria,0)
    else:
        frase_aleatoria = "[X] Lo siento, no tengo una frase para ese tipo."
        if activar_voz:
            hablar("erroria")

    return frase_aleatoria



def main():
    ia.configurarIA()

    #inicio = "¡Bienvenido al territorio del Charro Negro! Dime, ¿Cuál es tu nombre y a qué te dedicas?"
    while True:
        log("[?] Esperando tecla...",2)

        teclaActivar.esperarTeclaPress()
        teclaActivar.esperarTeclaRelease()

        inicio = frasePredefinida("saludo")

        intentos = 4

        entrada = solicitarEntrada(tiempo = 7)
        if not entrada:
            frasePredefinida("inaudible-cancelar")
            log("[!] Reiniciando...", 2)
            continue

        resp = ""
        intentos = 4

        while (resp == "" or "[X]" in resp) and intentos > 0:
            log("[i] Intentado generar respuesta...",2)
            resp = ia.generarRespuesta(personaje + entrada)
            intentos = intentos - 1

        if resp == "":
            frasePredefinida("erroria")
            log("[!] Reiniciando...", 2)
            continue
        elif "[X]" in resp:
            frasePredefinida("inaudible-cancelar")
            log("[!] Reiniciando...", 2)
            continue
        else:
            hablar(resp)

        resp_dec = ""
        intentos = 2
        while resp_dec == "" and intentos > 0:

            eleccion = solicitarEntrada(tiempo = 5)
            if not entrada:
                frasePredefinida("inaudible-cancelar")
                log("[!] Reiniciando...",2)
                continue

            resp_dec = ia.generarRespuesta(decision + "[Charro Negro]: " + inicio +"\n[Desconocido]: " + entrada + "\n[Charro Negro]: " +resp +"\n[Desconocido]: "+eleccion)
            log("[i] Respuesta detectada: "+resp_dec,2)
            intentos = intentos - 1

            if "SI" in resp_dec:
                frasePredefinida("si")
                #hablar("¡Excelente! Ahora tu alma será condenada a tomar mi lugar y yo por fin podré descansar en paz. Mientras tanto ¡Disfruta de tus riquezas con vida!")
            elif "NO" in resp_dec:
                frasePredefinida("no")
                #hablar("Ya veo, tu ambición no es tan grande como creía, así que no puedo darte nada.")
            elif "DUDA" in resp_dec:
                if intentos <= 0:
                    frasePredefinida("cancelar")
                else:
                    frasePredefinida("duda")
                #hablar("Tan sólo me tienes que dar tu alma a cambio y lo tendrás todo ¿Qué dices? ¿Aceptas?")
                resp_dec = ""
            elif "ALMA" in resp_dec:
                if intentos <= 0:
                    frasePredefinida("cancelar")
                else:
                    frasePredefinida("alma")

                resp_dec = ""
            elif "INSEGURO" in resp_dec:
                if intentos <= 0:
                    frasePredefinida("cancelar")
                else:
                    frasePredefinida("nose")
                resp_dec = ""
                #hablar("Bueno, veo que no estás seguro, si realmente lo quisieras, ya habrías aceptado mi trato")
            elif "EVADIR" in resp_dec:
                if intentos <= 0:
                    frasePredefinida("cancelar")
                else:
                    frasePredefinida("evadir")
                resp_dec = ""
            elif "FUERA" in resp_dec:
                frasePredefinida("incoherente")
                #hablar("Veo que no eres una persona seria, será mejor que te vayas antes de que me enoje")
            elif "INENTENDIBLE" in resp_dec:
                if intentos <= 0:
                    frasePredefinida("inaudible-cancelar")
                else:
                    frasePredefinida("inentendible")
                #hablar("¿Eh? No entendí lo que dijiste, sé más claro")
                resp_dec = ""
            else:
                if intentos <= 0:
                    frasePredefinida("inaudible-cancelar")
                else:
                    frasePredefinida("inentendible")
                resp_dec = ""

        log("[!] Conversación terminada...", 2)





if __name__ == "__main__":
    main()
