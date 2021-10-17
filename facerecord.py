#!/usr/bin/python3
import face_recognition
import picamera

unknownpictures = False
maxpictures = 100
pictureformat = 'Faces/Unknown{}.jpg'

camera = picamera.PiCamera()
camera.resolution = (320, 240)

numpictures = 0

while numpictures < maxpictures:
    filename = pictureformat.format(numpictures)
    camera.capture(filename)
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 1:
        numpictures += 1
        print(f"Found image {numpictures}.")
    else:
        print("Found {} faces in image.".format(len(face_locations)))
print("Total {} faces in files.".format(numpictures))
