import json
import unicodedata
import datetime
from collections import OrderedDict 
from operator import itemgetter 
   
members = {}
avglen = 0
words = {}
letras = {}
stickers = {}
horas = {}
i = 0
badchars = ",.-_´`¨:[]{}^*()+¿?¡!\"'=\\&%$#@|ºª>"

with open("result.json", "r", encoding="utf-8") as f:
    print("Leeamos el fichero!")

    data = json.load(f)

    mensajes = data["messages"]
    #iteramos sobre mensajes
    for msg in mensajes:
        #diferente codigo seguin el tipo (message, service, etc)
        if(msg["type"] == "message"):
            #control de los participantes del grupo
            autor = msg["from"]
            aux = members.get(autor)
            if(aux == None):
                members.update({autor: 1})
            else:
                members.update({autor: aux+1})    

            
            line = msg["text"]
            #Si el texto está vacio
            if(line == ""):
                #comprovamos si es un sticker y si lo es, lo contamos
                if("media_type" in msg and msg["media_type"] == "sticker"):
                    aux = stickers.get(msg["file"])
                    if(aux == None):
                        stickers.update({msg["file"]: 1})
                    else:
                        stickers.update({msg["file"]: aux+1})    
            #miramos si es un comando y los adaptamos
            if(type(line) is not str):
                aux = ""
                for elem in line:
                    if(type(elem) is str):
                        aux += elem
                    elif (elem["type"] == "bot_command"):
                        aux += elem["text"] + " "
                line = aux

            #eliminacion de caracteres extraños y normalización
            line = unicodedata.normalize('NFKD',line.lower()).encode('ASCII', 'ignore').decode("utf-8")
            for char in badchars:
                line = line.replace(char, " ")

            #Contamos las palabras y letras
            aux = line.split(" ")
            for wrd in aux:           
                aux = words.get(wrd)
                if(aux == None):
                    words.update({wrd : 1})
                else:
                    words.update({wrd: aux+1})
            for ltr in line:
                aux = letras.get(ltr)
                if(aux == None):
                    letras.update({ltr : 1})
                else:
                    letras.update({ltr: aux+1})
            
            avglen += len(line)

            #hora
            h = datetime.datetime.strptime(msg["date"], '%Y-%m-%dT%H:%M:%S')
            aux = horas.get(h.hour)
            if(aux == None):
                horas.update({h.hour: 1})
            else:
                horas.update({h.hour: aux+1})   

            i += 1 
        
    avglen = avglen/i
    del words[""]
    words = OrderedDict(sorted(words.items(), key = itemgetter(1), reverse = True))
    letras = OrderedDict(sorted(letras.items(), key = itemgetter(1), reverse = True))
    stickers = OrderedDict(sorted(stickers.items(), key = itemgetter(1), reverse = True))
    horas = OrderedDict(sorted(horas.items()))
    members = OrderedDict(sorted(members.items(), key = itemgetter(1), reverse = True))

    with open('ordenacion.txt', 'w', encoding="utf-8") as fi:
        for k, v in words.items():
            fi.write(str(k) + ' >>> '+ str(v) + '\n') 
    with open('stickers.html', 'w', encoding="utf-8") as fi:
        fi.write("<table>")
        for k, v in stickers.items():
            fi.write("<tr>")
            fi.write("<td><img src='"+k+"' width=200 height=200></td><td>"+str(v)+"</td>") 
            fi.write("</tr>")
        fi.write("</table>")
    print("--- RESULTADOS ---")
    print("Total de mensajes: "+ str(i)) 
    #Mensajes por persona
    print()
    for u in members:
        print("Total de mensajes de "+ str(u)+" : "+ str(members[u]))
    #Estadísiticas
    print()
    print("Las 5 palabras más usadas: "+ str(list(words.items())[:5] ))
    print("Letra más usada: "+str(letras))
    print("Longitud media de mensaje: "+ str(avglen))
    print("Distribución de mensajes por hora: "+ str(horas))

        

