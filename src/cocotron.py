# pyright: strict

from servo import MotionControl
from consts import SEQUENCES, Motors, Pause, LED, Loop
import RPi.GPIO as GPIO # pyright: ignore
import time, sys

LED_PIN = 17
BUTTON_PIN = 27 # Checkar si este será el pin final

class Cocotron:
    def __init__(self):
        """
        """
        self.mc = MotionControl(16)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        # Esta es el pin del boton
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def eyes(self, mode: bool):
        """
        """

        GPIO.output(LED_PIN, GPIO.HIGH if mode else GPIO.LOW)

    def match_jaw_to_voice(self, audio: None):
        """
        Moves the jaw according to the audio file played.
        """

        raise Exception('Not implemented!')

    def sequence(self, seq_name: str):
        """
        Executes the specified `seq` movements. Each step is executed only
        after the previous one is done.
        """

        seq = SEQUENCES[seq_name]

        loop_point = 0
        i = 0
        while i < len(seq):
            step = seq[i]
            action, spec = step

            if type(action) == Motors:
                if type(spec) != float and spec != None: # pyright: ignore
                    raise Exception(f'{action, spec}: El ángulo debe ser de tipo flotante o None')

                angle_diff = abs(self.mc.angles[action.value] - spec) if spec != None else 0 # pyright: ignore

                self.mc.move(action, spec)
                time.sleep(self.mc.calculate_movement_time(angle_diff, action)) # pyright: ignore

            elif type(action) == Pause:
                if type(spec) not in (int, float): # pyright: ignore
                    raise Exception(f'{action, spec}: El tiempo de pausa debe ser numérico')

                time.sleep(spec) # pyright: ignore

            elif type(action) == LED:
                if type(spec) != bool: # pyright: ignore
                    raise Exception(f'{action, spec}: el valor de el encendido debe ser booleano!')

                self.eyes(spec)

            elif type(action) == Loop:
                if type(spec) != int: # pyright: ignore
                    raise Exception(f'{action, spec}: la cantidad de veces a repetir debe ser entera!')

                if spec > 0:
                    seq[i][1] = spec - 1 # pyright: ignore
                    i = loop_point
                else:
                    loop_point = i

            i += 1

    # Métodos del boton
    def esperarTeclaPress(self):
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING)

    def esperarTeclaRelease(self):
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)
    #######

    def main(self):
        if len(sys.argv) > 1:
            self.sequence(sys.argv[1])
        GPIO.cleanup()
