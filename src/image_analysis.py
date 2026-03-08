import pandas as pd
import os, shutil, cv2

df = pd.read_excel('BrEaST-Lesions-USG-clinical-data-Dec-15-2023.xlsx', usecols='B,C,S,T')

with open('dataset/annotations/notes.csv', 'a') as csvfile:
    for row in df.itertuples():
        if 'confirmed' not in row[3]:
            continue
        if 'not applicable' in row[4]:
            continue

        diagnoses = row[4].split('&')
        for diagnosis in diagnoses:
            if diagnosis is not None:
                img = cv2.imread(f'BrEaST-Lesions_USG-images_and_masks/{row[2]}', cv2.IMREAD_UNCHANGED)
                b, g, r, a = cv2.split(img)
                _, mask = cv2.threshold(a, 1, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    continue

                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                csvfile.write(f'{row[1]},{x},{y},{x + w},{y + h},{diagnosis}\n')