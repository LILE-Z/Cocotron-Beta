# pyright: strict
from __future__ import annotations
from adafruit_servokit import ServoKit # pyright: ignore
from consts import Motors

class MotionControl:
    """
    Class responsible for servo interaction.
    """

    def __init__(
        self,
        channels: int = 16,
    ):
        self.kit: ServoKit = ServoKit(channels=channels)
        self._MOTOR_SWEEP_TIMES = [
            0.800
            for _ in range(channels)
        ]
        self.angles = [
            0.0
            for _ in range(channels)
        ]

    def calculate_movement_time(self, angle_diff: float, motor: Motors) -> float:
        """
        Calculates the time needed to get to the desired angle.
        """

        st = self._MOTOR_SWEEP_TIMES[motor.value]
        return st * angle_diff / 180

    def move(self, motor: Motors, angle: float | None):
        """
        Moves the motor to a specified location.
        """

        # a, b = VALID_ANGLES[motor]
        # assert a >= angle >= b

        if angle != None:
            angle = round(angle)

        self.kit.servo[motor.value].angle = angle # pyright: ignore[reportUnknownMemberType]

        if angle != None:
            self.angles[motor.value] = angle
