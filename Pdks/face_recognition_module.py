# -*- coding: utf-8 -*-
# face_recognition_module.py
import face_recognition
import os
import numpy as np
import cv2

def load_known_faces(folder_path="known_faces"):
    encodings = []
    names = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(folder_path, filename)
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                encodings.append(encoding[0])
                name = os.path.splitext(filename)[0]
                names.append(name)
    return encodings, names

def recognize_face(frame, known_encodings, known_names):
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        if True in matches:
            matched_idx = matches.index(True)
            return known_names[matched_idx]
    return None
