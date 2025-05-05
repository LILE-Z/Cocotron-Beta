from enum import Enum, auto

class Motors(Enum):
    Jaw = 0
    NeckX = 1
    NeckY = 2
    ShoulderLX = 3 # "hacia afuera"
    ShoulderLZ = 4
    ShoulderRX = 5 # "hacia adelante"
    ShoulderRZ = 6
    ElbowL = 7
    ElbowR = 8

    def __repr__(self):
        return 'Motors.' + self.name

class Pause: pass
class LED: pass
class Loop: pass

Angle = float | None
SeqValidLeft = Motors | Pause | LED | Loop
SeqValidRight = Angle | bool | int
Sequence = list[list[SeqValidLeft, SeqValidRight]]

VALID_ANGLES = {
    Motors.Jaw : (5, 115), # 115 max
    Motors.NeckX : (0, 90),
    Motors.NeckY : (35, 70),
    Motors.ShoulderLX : (0, 180), # 0 max
    Motors.ShoulderLZ : (0, 90),
    Motors.ShoulderRX : (0, 180), # 180 max
    Motors.ShoulderRZ : (90, 170),
    Motors.ElbowL : (0, 90), # 0 max
    Motors.ElbowR : (0, 90), # 90 max
}

SEQUENCES: dict[str, Sequence] = {
    'Stop': [
        [k, None]
        for k in VALID_ANGLES.keys()
    ] + [
        [LED(), False],
    ],
    'Eyes': [
        [LED(), True],
        [Pause(), 5],
        [LED(), False],
        [Pause(), 5],
        [Loop(), 2],
    ],
    'Jaw': [
        [Motors.Jaw, 5.0],
        [Loop(), 0],
        [LED(), True],
        [Motors.Jaw, 115.0],
        [LED(), False],
        [Motors.Jaw, 5.0],
        [Loop(), 5],
        [Motors.Jaw, None],
    ],
    'Test neck': [
        [Motors.NeckX, 0.0],
        [Motors.NeckX, 90.0],
        [Motors.NeckX, 0.0],
        [Pause(), 1],
        [Motors.NeckY, 35.0],
        [Motors.NeckY, 70.0],
        [Motors.NeckY, 35.0],
        [Motors.NeckX, None],
        [Motors.NeckY, None],
    ],
    'Test left arm': [
        [Motors.ShoulderLX, 0.0],
        [Motors.ShoulderLX, 180.0],
        [Motors.ShoulderLX, 0.0],
        [Pause(), 1],
        [Motors.ShoulderLZ, 0.0],
        [Motors.ShoulderLZ, 90.0],
        [Motors.ShoulderLZ, 0.0],
        [Pause(), 1],
        [Motors.ElbowL, 0.0],
        [Motors.ElbowL, 90.0],
        [Motors.ElbowL, 0.0],
        [Motors.ShoulderLZ, None],
        [Motors.ShoulderLX, None],
        [Motors.ElbowL, None],
    ],
    'Test right arm': [
        [Motors.ShoulderRX, 180.0],
        [Motors.ShoulderRX, 0.0],
        [Motors.ShoulderRX, 180.0],
        [Pause(), 1],
        [Motors.ShoulderRZ, 0.0],
        [Motors.ShoulderRZ, 90.0],
        [Motors.ShoulderRZ, 0.0],
        [Pause(), 1],
        [Motors.ElbowR, 0.0],
        [Motors.ElbowR, 90.0],
        [Motors.ElbowR, 0.0],
        [Motors.ShoulderRZ, None],
        [Motors.ShoulderRX, None],
        [Motors.ElbowR, None],
    ],
}
