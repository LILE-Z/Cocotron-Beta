from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

try:
    while True:
        line = input('>>: ').split()
        if len(line) != 2:
            print('El formato es: canal ángulo. Ej. 0 120.5')
            continue

        channel, angle = line
        channel = int(channel)
        angle = float(angle)

        if channel < 0 or channel > 15:
            print('El canal debe estar entre 0 y 15.')

        if angle < 0 or angle > 180:
            print('El ángulo debe estar entre 0 y 180')

        kit.servo[channel].angle = angle

except KeyboardInterrupt:
    for i in range(16):
        kit.servo[i].angle = None
