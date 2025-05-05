import json, sys
from src.consts import Motors, VALID_ANGLES

BODYPARTS = {
    'rforearmx' : Motors.ElbowR,
    'lforearmx' : Motors.ElbowL,
    'rupperarmx' : Motors.ShoulderRX,
    'rupperarmz' : Motors.ShoulderRZ,
    'lupperarmx' : Motors.ShoulderLX,
    'lupperarmz' : Motors.ShoulderLZ,
    'headx' : Motors.NeckX,
    'heady' : Motors.NeckY,
}

json_seq_filename = sys.argv[1]
with open(json_seq_filename, 'r') as f:
    seq_json = json.load(f)

seq = {}
for i, s in enumerate(seq_json):
    frame = []

    for k in s:
        for j in s[k]:
            bodypart = BODYPARTS[f'{k}{j}']
            angle = float(s[k][j])

            if bodypart in (Motors.ShoulderLX, Motors.ElbowL):
                angle = max(VALID_ANGLES[bodypart]) - angle

            step = [BODYPARTS[f'{k}{j}'], angle]
            frame.append(step)

    seq[i] = frame

# delete duplicates
dups = {}
for i in list(seq.keys())[1:]:
    for j in range(len(seq[i])):
        if seq[i][j] == seq[i - 1][j]:
            dups.setdefault(i, [])
            dups[i].append(j)

for i in dups:
    for j in dups[i]:
        seq[i].pop(j)

out_str = ''
for frame in seq:
    out_str += f'{frame}: [\n'
    for pose in seq[frame]:
        out_str += f'    {pose},\n'

    out_str += f']\n\n'

with open('secuencia_convertida.txt', 'w') as f:
    f.write(out_str)
