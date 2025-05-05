# Clase para detectar pulsaciones de teclado
from pynput import keyboard
import threading

class TecladoControlador:

    TECLAS_MAPEADAS = {
        'space': keyboard.Key.space,
        'enter': keyboard.Key.enter,
        'esc': keyboard.Key.esc,
    }

    # Construir el teclado, usando una tecla
    def __init__(self, tecla_txt):
        self.tecla = self.TECLAS_MAPEADAS.get(tecla_txt.lower(), None)
        if self.tecla is None:
            raise ValueError(f"Tecla '{tecla_txt}' no reconocida")

    # SI es la tecla con la que se inicializó, devolver verdadero
    def __on_press(self, key):
        if key == keyboard.Key.space:
            return False
        
    # SI es la tecla con la que se inicializó, devolver verdadero    
    def __on_release(self, key):
        if key == keyboard.Key.space:
            return False

    def __nada(self, key):
        pass

    # Esperar a que el usuario presione una tecla
    def esperarTeclaPress(self):
        with keyboard.Listener(on_press=self.__on_press, on_release=self.__nada) as listener:
            listener.join()
        
    def esperarTeclaRelease(self):
        with keyboard.Listener(on_press=self.__nada,on_release=self.__on_release) as listener:
            listener.join()
     
def main():
    tecladoCon = TecladoControlador("Space")
    print("Esperando presionar")
    tecladoCon.esperarTeclaPress()
    print("Esperando release")
    tecladoCon.esperarTeclaRelease()
    print("Fin")

if __name__ == "__main__":
    main()