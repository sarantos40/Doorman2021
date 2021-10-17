#!/usr/bin/python3
# The simple version, with files on disk and no threading
import face_recognition
import picamera
import numpy as np
import sys
import os.path
import time
import socket

unknownpictures = False
pictureformat = 'Faces/Unknown{}.jpg'
maxpictures = 100
sendaddr = '192.168.44.{}'
PORT = 65432
WAIT = 20
echo = False

def client(where, msg, who, description):
    host = sendaddr.format(where)
    t = time.time()
    if host in waituntil and t < waituntil[host]:
        print(f'Already notified {host} - still {int(waituntil[host] - t)} sec')
        return
    waituntil[host] = t + WAIT
    print(f'Notify host {host} ....... {description} .......')
    try:
        with socket.socket() as s:
            s.connect((host, PORT))
            s.sendall(msg)
            if echo: print('Sent', len(msg))
    except (ConnectionRefusedError) as e:
        print(f'Unable to communicate to {host}: {e}')

kfilenames = sys.argv[1:]

names = [os.path.splitext(os.path.basename(fn))[0] for fn in kfilenames]
addrs = [os.path.basename(os.path.dirname(fn)) for fn in kfilenames]
pictures = [face_recognition.load_image_file(fn) for fn in kfilenames]
faceencs = [face_recognition.face_encodings(im)[0] for im in pictures]

print(f'Ready {len(faceencs)} faces: {",".join(names)}')

camera = picamera.PiCamera()
camera.resolution = (320, 240)

waituntil = {}
numshots, numpictures = 0, 0

while numpictures < maxpictures:
    filename = pictureformat.format(numpictures)
    camera.capture(filename)
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image)
    if face_locations:
        tgts, visitors = set(), []
        qfaceslst = face_recognition.face_encodings(image)
        for x in qfaceslst:
            results = face_recognition.compare_faces(faceencs, x)
            nresults = results.count(True)
            if nresults > 1:
                face_distances = face_recognition.face_distance(faceencs, x)
                ibest = np.argmin(face_distances)
                qname = names[ibest]
                pname = f"{qname} ({'|'.join([nam for nam, q in zip(names, results) if q])})"
            elif nresults:
                ibest = results.index(True)
                pname = qname = names[ibest]
            else:
                # if len(qfaceslst) == 1:
                numpictures += 1
                for tgt in addrs: tgts.add(tgt)
                qname, pname = '?', filename
            visitors.append(pname)
            if nresults: tgts.add(addrs[ibest])
        print(len(qfaceslst), tgts or '{}', ', '.join(visitors))
        if sendaddr and tgts:
            for tgt in tgts: client(tgt, open(filename, 'rb').read(), qname, pname)
    else:
        print(f"Found nobody {numshots}.")
    numshots += 1
print("Total {} faces in files.".format(numpictures))
