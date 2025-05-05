from gpiozero import Button

button = Button(17)

class TecladoControlador:

    def __init__(self, tecla_txt):
        pass
        
    def esperarTeclaPress(self):
        button.wait_for_release()
    
    def esperarTeclaRelease(self):
        button.wait_for_press()

if __name__ == "__main__":

    lol = 0
    b = TecladoControlador("");
    while True:
        b.esperarTeclaPress()
        print(f"{lol} Button was Pressed")
        b.esperarTeclaRelease()
        print(f"{lol} Button was Released")
        #sleep(2)
        lol = lol + 1
