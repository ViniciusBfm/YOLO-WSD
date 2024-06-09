import cv2
import os
import datetime
import time
from ultralytics import YOLO
import sqlite3
import base64

# Conecte-se ao banco de dados
conn = sqlite3.connect('../controle.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS capturas_cam1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        msg TEXT NOT NULL,
        imagem TEXT NOT NULL
    );
''')

modelo = YOLO('best_1400.pt')

video = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Inicialize o tempo para o primeiro salvamento
ultimo_salvamento = time.time()

while True:
    check, img = video.read()
    resultado = modelo.predict(img, verbose=False)

    for obj in resultado:
        nomes = obj.names
        for item in obj.boxes:
            conf = round(float(item.conf[0]), 2)
            if conf > 0.5:
                x1, y1, x2, y2 = int(item.xyxy[0][0]), int(item.xyxy[0][1]), int(item.xyxy[0][2]), int(item.xyxy[0][3])
                cls = int(item.cls[0])
                nomeClasse = nomes[cls]
                texto = f'{nomeClasse} - {conf}'
                cv2.putText(img, texto, (x1, y1 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 0), 2)

                # Verifique se a classe é relevante (sem capacete, sem luva ou sem colete)
                if nomeClasse in ['Sem capacete', 'Sem luva', 'Sem colete']:
                    if time.time() - ultimo_salvamento >= 10:
                        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                        # Converter a imagem para base64
                        _, buffer = cv2.imencode('.jpg', img)
                        img_base64 = base64.b64encode(buffer).decode('utf-8')

                        texto = "Sistema encontrou alguém sem EPI"

                        # Salve a imagem diretamente no banco de dados
                        cursor.execute('INSERT INTO capturas_cam1 (timestamp, imagem, msg) VALUES (?, ?, ?)',
                                       (timestamp, img_base64, texto))
                        conn.commit()
                        print(f"Imagem salva para classe: {nomeClasse} com timestamp {timestamp}")
                        ultimo_salvamento = time.time()

                # Desenhe o retângulo na imagem
                if nomeClasse == 'Capacete' or nomeClasse == 'Luva' or nomeClasse == 'Colete':
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
                elif nomeClasse == 'Sem capacete' or nomeClasse == 'Sem luva' or nomeClasse == 'Sem colete':
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
                elif nomeClasse == 'Pessoa':
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 220, 0), 2)

    cv2.imshow('IMG', img)
    if cv2.waitKey(1) == 27:
        break

conn.close()
