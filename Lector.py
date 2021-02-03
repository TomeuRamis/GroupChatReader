import json
import sys
from collections import OrderedDict 
from operator import itemgetter 

mode = "T"
file = "a.txt"

if(mode == "WP"):
    fecha = []
    hora = []
    usuario = []
    mensaje = []

    Nmsg = 0

    kicks = []

    with open("a.txt", "r", encoding="utf-8") as f:
        print("Leeamos el fichero!")

        line = f.readline()
        while line:
            msg = []
            j = 0
            try:
            #mensajes de otro chat pegados
                if(line[0]!="["):
                    aux = line.split(",", 1)            
                    fecha.append(aux[0])
                    j += 1
                    aux = aux[1].split("-", 1)
                    hora.append(aux[0])
                    j += 1
                    aux = aux[1].split(":", 1)
                    usuario.append(aux[0])
                    j += 1
                    #elimiación de miembro del grupo
                    if(len(aux) > 1):
                        mensaje.append(aux[1][:-1])
                        Nmsg += 1
                    else:
                        kicks=[fecha[Nmsg], hora[Nmsg], usuario[Nmsg]]
                        fecha = fecha[:-1]
                        hora = hora[:-1]
                        usuario = usuario[:-1]
            except:
                #Error en el formato de la linea (pasamos de ella)   
                if j >= 1:
                    fecha = fecha[:-1]
                if j >= 2:
                    hora = hora[:-1]
                if j >= 3:
                    usuario = usuario[:-1]

            line = f.readline() 

    print("Lectura terminada.")
    print("Inicio del análisis de la conversación")

    #variables
    multimedia = 0
    enlaces = 0
    avglen = 0

    usrs = {}

    words = {}
    letras = {}

    years = {}
    months = [0,0,0,0,0,0,0,0,0,0,0,0]
    hours = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    char = "ABCÇDEFGHIJKLMNÑOPQRSTXYZ1234567890"
    i = 0
    while(i<Nmsg):

        line = mensaje[i].upper()
        avglen += len(line)
        for ltr in line: 
            
            if(ltr in char):
                aux = letras.get(ltr)
                if(aux == None):
                    letras.update({ltr : 1})
                else:
                    letras.update({ltr: aux+1})

        if("<FITXERS" in line or "HTTP" in line):
            if("<FITXERS" in line):
                multimedia += 1
            if("HTTP" in line):
                enlaces += 1
        else:
            aux = line.split(" ")
            for wrd in aux:           
                aux = words.get(wrd)
                if(aux == None):
                    words.update({wrd : 1})
                else:
                    words.update({wrd: aux+1})
                

        aux = usrs.get(usuario[i])
        if(aux == None):
            usrs.update({usuario[i] : 1})
        else:
            usrs.update({usuario[i]: aux+1})

        line = fecha[i].split("/")
        #años
        aux = years.get(line[2])
        if(aux == None):
            years.update({line[2] : 0})
        else:
            years.update({line[2]: aux+1})
        #meses
        months[int(line[1])-1] += 1
        #horas
        line = hora[i].split(":")
        hours[int(line[0])] += 1

        i += 1


    avglen = avglen/Nmsg
    puretxt = Nmsg - multimedia - enlaces  

    sorted_words = OrderedDict(sorted(words.items(), key = itemgetter(1), reverse = True))
    with open('ordenacion.txt', 'w', encoding="utf-8") as fi:
        for k, v in sorted_words.items():
            fi.write(str(k) + ' >>> '+ str(v) + '\n') 

    letras = sorted(letras.items(), key = itemgetter(1), reverse = True)

    print("--- RESULTADOS ---")
    print("Total de mensajes: "+ str(Nmsg))
    print("Total de mensajes sin multimedia ni enlaces: "+str(puretxt))
    print("Total de mensajes multimedia (foto/video/audio): "+ str(multimedia))
    print("Total de mensajes con enlaces web: "+ str(enlaces))
    #Mensajes por persona
    print()
    for u in usrs:
        print("Total de mensajes de "+u+" : "+ str(usrs[u]))
    #Estadísiticas
    print()
    print("Las 5 palabras más usadas: "+ str(list(sorted_words.items())[:5] ))
    print("Letra más usada: "+str(letras))
    print("Longitud media de mensaje: "+ str(avglen))
    print("Distribución de mensajes por año: "+ str(years))
    print("Distribución de mensajes por mes: "+ str(months))
    print("Distribución de mensajes por hora: "+ str(hours))
    #Media de mensajes seguidos enviados (siempre >=1)
    print("Mensajes en cadena: ")

    print("Fin.")

else: