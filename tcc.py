import cv2
import numpy as np
from pymongo import MongoClient

vaga1 = [1, 279, 24, 145]
vaga2 = [48, 278, 57, 144]
vaga3 = [123, 278, 65, 139]
vaga4 = [200, 274, 69, 145]
vaga5 = [276, 275, 72, 141]
vaga6 = [353, 276, 71, 141]
vaga7 = [445, 273, 36, 144]
vaga8 = [6, 30, 44, 85]
vaga9 = [67, 26, 48, 89]
vaga10 = [131, 30, 52, 85]
vaga11 = [192, 29, 56, 86]
vaga12 = [254, 27, 55, 87]
vaga13 = [320, 25, 50, 88]
vaga14 = [387, 22, 49, 88]

vagas = [vaga1, vaga2, vaga3, vaga4, vaga5, vaga6, vaga7, vaga8, vaga9, vaga10, vaga11, vaga12, vaga13, vaga14]
vagasLivres = []
vagasOcupadas = []
vagasAnterior = []

video = cv2.VideoCapture('tcc.mp4')

client = MongoClient("mongodb+srv://loran:estacionamento@cluster0.m9q8quv.mongodb.net/")
db = client["test"]
collection = db["vagamodels"]

results = collection.find()
for result in results:
    if result["status"] == True:
        vagasLivres.append(result["_id"])
    else:
        vagasOcupadas.append(result["_id"])

for vaga in vagasLivres:
    vagasAnterior.append(vaga)

while True:
    check,img = video.read()
    imgCinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    imgTh = cv2.adaptiveThreshold(imgCinza,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,25,16)
    imgBlur = cv2.medianBlur(imgTh, 5)
    kernel = np.ones((3,3),np.int8)
    imgDil = cv2.dilate(imgBlur,kernel)

    qtVagasAbertas = 0

    for x,y,w,h in vagas:
        recorte = imgDil[y:y+h, x:x+w]
        qtPxBranco = cv2.countNonZero(recorte)
        cv2.putText(img,str(qtPxBranco), (x,y+h-10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)

        if qtPxBranco > 900: 
            cv2.rectangle(img,(x,y),(x+w, y+h),(0,0,255),2)
            vaga = str(x) + str(y) + str(w) + str(h)
            if vaga in vagasLivres:
                vagasLivres.remove(vaga)
                vagasOcupadas.append(vaga)
        else:
            cv2.rectangle(img,(x,y),(x+w, y+h),(0,255,0),2)
            qtVagasAbertas +=1
            vaga = str(x) + str(y) + str(w) + str(h)
            if not vaga in vagasLivres:
                vagasLivres.append(vaga)
                vagasOcupadas.remove(vaga)
    
    cv2.rectangle(img,(20,0),(150,20),(255,0,0), -1)
    cv2.putText(img,f'LIVRE: {qtVagasAbertas}/15', (40,16),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),2)

    if vagasLivres != vagasAnterior:
        vagasAnterior.clear()

        for vaga in vagasLivres:
            vagasAnterior.append(vaga)
            buscarVaga = { "_id": vaga }
            atualizarVaga = { "$set": { "status": True } }
            collection.update_one(buscarVaga, atualizarVaga)
            
        for vaga in vagasOcupadas:
            buscarVaga = { "_id": vaga }
            atualizarVaga = { "$set": { "status": False } }
            collection.update_one(buscarVaga, atualizarVaga)


    key = cv2.waitKey(5)
    if key == 27:
        break
    
    cv2.imshow('video',img)
    #cv2.imshow('video TH',imgTh)
    cv2.waitKey(5)