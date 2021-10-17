#!/usr/bin/python3
# With files in memory but no threading
import face_recognition
import picamera
import numpy as np
import sys
import os.path
import time
import socket
import io

unknownpictures = False
maxpictures = 100
picturestore = 'Faces/Unknown{}.jpg' # empty for not storing
sendaddress = '192.168.44.{}' # empty for not sending
PORT = 65432
WAIT = 20
echo = False

def client(where, msg, who, description):
    host = sendaddress.format(where)
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
stream = io.BytesIO()

waituntil = {}
numshots, numpictures = 0, 0

while numpictures < maxpictures:
    stream.seek(0)
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    image = face_recognition.load_image_file(stream)
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
                if picturestore: ## and len(qfaceslst) == 1:
                    numpictures += 1
                    filename = picturestore.format(numpictures)
                    print(f"Storing {filename}")
                    stream.seek(0)
                    open(filename, 'wb').write(stream.read())
                for tgt in addrs: tgts.add(tgt)
                qname, pname = '?', f'#{numpictures}'
            visitors.append(pname)
            if nresults: tgts.add(addrs[ibest])
        print(len(qfaceslst), tgts or '{}', ', '.join(visitors))
        if sendaddress and tgts:
            stream.seek(0)
            im = stream.read()
            for tgt in tgts: client(tgt, im, qname, pname)
    else:
        print(f"Found nobody {numshots}")
    numshots += 1
print("Total {} faces in files.".format(numpictures))
