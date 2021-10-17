#!/usr/bin/python3
import face_recognition
import cv2
import numpy as np
import sys
import os.path

usegray = False

if len(sys.argv) > 2 and sys.argv[1] == '-s':
    scaledown = int(sys.argv[2])
    scaleup = 1 / scaledown
    afilenames = sys.argv[3:]
else:
    scaledown = scaleup = 1
    afilenames = sys.argv[1:]

if '.' in afilenames:
    kfilenames = afilenames[:afilenames.index('.')]
    qfilenames = afilenames[afilenames.index('.')+1:]
else:
    kfilenames = afilenames[:-1]
    qfilenames = afilenames[-1:]
    
names = [os.path.splitext(os.path.basename(fn))[0] for fn in kfilenames]
addrs = [os.path.basename(os.path.dirname(fn)) for fn in kfilenames]
pictures = [face_recognition.load_image_file(fn) for fn in kfilenames]
if scaledown == 1:
    picsdown = pictures
else:
    picsdown = [cv2.resize(im, (0, 0), fx=scaleup, fy=scaleup) for im in pictures]
if usegray: picsdown = [cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) for im in picsdown]


faceslst = [face_recognition.face_encodings(im) for im in picsdown]
print([f'{nam}:{len(xx)}' for nam, xx in zip(names, faceslst)])
faceencs = [xx[0] for xx in faceslst] # one face per picture

# faceencs now contains a universal 'encoding' of each facial features that can be compared to any other picture of a face!

# Now we can see the two face encodings are of the same person with `compare_faces`!

for fn in qfilenames:
    tgts, visitors = set(), []
    qim = face_recognition.load_image_file(fn)

    if scaledown == 1:
        qsd = qim
    else:
        qsd = cv2.resize(qim, (0, 0), fx=scaleup, fy=scaleup)
    if usegray: qsd = cv2.cvtColor(qsd, cv2.COLOR_BGR2GRAY)
    qfaceslst = face_recognition.face_encodings(qsd)

    for x in qfaceslst:
        results = face_recognition.compare_faces(faceencs, x)
        nresults = results.count(True)
        if nresults > 1:
            face_distances = face_recognition.face_distance(faceencs, x)
            ibest = np.argmin(face_distances)
            pname = f"{names[ibest]} ({'|'.join([nam for nam, q in zip(names, results) if q])})"
        elif nresults:
            pname = names[results.index(True)]
        else:
            pname = '?'
        visitors.append(pname)
        for tgt, q in zip(addrs, results):
            if q: tgts.add(tgt)
    print(fn, len(qfaceslst), tgts or '{}', ', '.join(visitors))
