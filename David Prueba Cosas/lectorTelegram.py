import json
import unicodedata
import datetime
import base64
from collections import OrderedDict 
from operator import itemgetter 

chatname = "undefined chat"
members = {}
stickerfiles = []
letras = {}
horas = {}

def main():
    global chatname
    global members
    global stickerfiles
    global letras
    global horas
    badchars = ",.-_´`¨:[]{}^*()+¿?¡!\"'=\\&%$#@|ºª>"


    with open("result.json", "r", encoding="utf-8") as f:
        print("Leamos el fichero!")

        data = json.load(f)
        if "name" in data: chatname = data["name"]

        #iteramos sobre los mensajes
        for msg in data["messages"]:
            #diferente codigo seguin el tipo (message, service, etc)
            if(msg["type"] == "message"):
                #control de los participantes del grupo
                autor = msg["from"]
                if(autor in members):
                    members[autor].addmsg()
                else:
                    members[autor] = Member(autor)

                
                line = msg["text"]
                #comprobamos si es un sticker y si lo es, lo contamos
                if("media_type" in msg and msg["media_type"] == "sticker"):
                    if msg["thumbnail"] not in stickerfiles: stickerfiles.append(msg["thumbnail"])
                    members[autor].addsticker(msg["thumbnail"])
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
                    if wrd == "": continue      
                    members[autor].addword(wrd)
                for ltr in line:
                    if ltr == " ": continue
                    aux = letras.get(ltr)
                    if(aux == None):
                        letras.update({ltr: 1})
                    else:
                        letras.update({ltr: aux+1})
                
                #hora
                dt = datetime.datetime.strptime(msg["date"], '%Y-%m-%dT%H:%M:%S')
                aux = horas.get(dt.hour)
                if(aux == None):
                    horas.update({dt.hour: 1})
                else:
                    horas.update({dt.hour: aux+1})   
            
        letras = OrderedDict(sorted(letras.items(), key = itemgetter(1), reverse = True))
        horas = OrderedDict(sorted(horas.items()))
        members = OrderedDict(sorted(members.items(), key = itemgetter(1), reverse = True))
        for member in members:
            members[member].words = OrderedDict(sorted(members[member].words.items(), key = itemgetter(1), reverse = True))
            members[member].stickers = OrderedDict(sorted(members[member].stickers.items(), key = itemgetter(1), reverse = True))

        printResults()

def printResults():
    print("Generando output...")
    filename = chatname.replace(" ","_") + ".html"
    datamensajes = "["
    for name in members:
        member = members[name]
        datamensajes += "{ name: '" + member.name + "', y: " + str(member.messagecount) + " },"
    datamensajes = datamensajes[0:len(datamensajes)-1] + "]"

    # Procesamiento horas
    datahoras = "["
    for i in range(24):
        datahoras += "[ '" + str(i) + "', " + str(horas.get(i,0)) + " ],"
    datahoras = datahoras[0:len(datahoras)-1] + "]"

    # Procesamiento stickers
    lstickers = {}
    lstickers[1] = [] #Animated
    lstickers[0] = [] #Normal
    # leemos la lista de stickers de cada usuario
    # rellenamos las listas de traducción (1 y 0)
    # creamos las listas de cada usuario con el indice a la lista de traducción
    for name in members:
        member = members[name]
        lstickers[name] = []
        for sticker in member.stickers:
            idx, isAnim = getIndex(sticker)
            addAt(lstickers[isAnim],sticker,idx)
            lstickers[name].append({"image":idx, "animated":isAnim, "cant":member.stickers[sticker]})
    # combinamos las listas de traducción de stickers normales y animados
    numnormal = len(lstickers[0])
    lstickers[0].extend(lstickers[1])
    lstickers.pop(1)
    # ajustamos los indices de los stickers animados y eliminamos el campo animated
    for name in members:
        for s in lstickers[name]:
            if s["animated"] == 1:
                s["image"] += numnormal
            s.pop("animated")
    # codificamos los stickers en base64
    codedstickers = []
    for s in lstickers[0]:
        codedstickers.append(encodeimage(s))
    lstickers.pop(0)
            
    # procesamiento de palabras
    lwords = {}
    for name in members:
        member = members[name]
        lwords[name] = []
        for wrd in member.words:
            lwords[name].append({"name":wrd, "cant":member.words[wrd]})

    # procesamiento letras
    dataletras = "["
    for letra in letras:
        if not letra == "\n":
            dataletras += "[ '"+letra+"', "+str(letras[letra])+" ],"
    dataletras = dataletras[0:len(dataletras)-1] + "]"

    # ----------------------------------------- ESCRIBIMOS LA PÁGINA -------------------------------------------
    with open(filename,"w",encoding="utf-8") as out:
        out.write("<!DOCTYPE html>\n")
        out.write("<html lang=\"en\">\n")
        out.write("\n")
        out.write("<head>\n")
        out.write("  <meta charset=\"UTF-8\">\n")
        out.write("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
        out.write("  <title>GroupChatReader - (group-name)</title>\n")
        out.write("  <link rel=\"stylesheet\" href=\"https://cdn.datatables.net/1.10.23/css/jquery.dataTables.min.css\">\n")
        out.write("  <link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\">\n")
        out.write("  <script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js\"></script>\n")
        out.write("  <script src=\"https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js\"></script>\n")
        out.write("  <script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js\"></script>\n")
        out.write("  <script src=\"https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js\"></script>\n")
        out.write("  <script src=\"https://code.highcharts.com/highcharts.js\"></script>\n")
        out.write("  <script src=\"https://code.highcharts.com/modules/exporting.js\"></script>\n")
        out.write("  <script src=\"https://code.highcharts.com/modules/export-data.js\"></script>\n")
        out.write("  <script src=\"https://code.highcharts.com/modules/accessibility.js\"></script>\n")
        out.write("</head>\n")
        out.write("\n")
        out.write("<body>\n")
        out.write("  <ul class=\"nav nav-tabs\">\n")
        out.write("    <li class=\"nav-item\">\n")
        out.write("      <a class=\"nav-link active\" data-toggle=\"tab\" href=\"#home\">Home</a>\n")
        out.write("    </li>\n")
        out.write("    <li class=\"nav-item\">\n")
        out.write("      <a class=\"nav-link\" data-toggle=\"tab\" href=\"#menustickers\">Stickers</a>\n")
        out.write("    </li>\n")
        out.write("    <li class=\"nav-item\">\n")
        out.write("      <a class=\"nav-link\" data-toggle=\"tab\" href=\"#menupalabras\">Palabras</a>\n")
        out.write("    </li>\n")
        out.write("    <li class=\"nav-item\">\n")
        out.write("      <a class=\"nav-link\" data-toggle=\"tab\" href=\"#menuletras\">Letras</a>\n")
        out.write("    </li>\n")
        out.write("  </ul>\n")
        out.write("  <!-- Tab panes -->\n")
        out.write("  <div class=\"tab-content\">\n")
        out.write("    <!------------------------------ Resumen ------------------------------->\n")
        out.write("    <div class=\"tab-pane container active\" id=\"home\">\n")
        out.write("      <h1 class=\"mt-2\">Analisis de datos para <span id=\"nombrechat\"></span></h1>\n")
        out.write("\n")
        out.write("      <h2 class=\"mt-2\">Total de mensajes: <span id=\"totalmensajes\">XXXXXX</span></h2>\n")
        out.write("      <div class=\"container-fluid border row rounded ml-0 px-4 my-4\">\n")
        out.write("        <div id=\"miembroshome\" class=\"col-sm-4 py-3 border-right\">\n")
        out.write("          <h3 class=\"h5\">Mensajes por miembro</h3>\n")
        out.write("        </div>\n")
        out.write("        <div class=\"col-sm-8\">\n")
        out.write("          <div id=\"container-mensajes\"></div>\n")
        out.write("        </div>\n")
        out.write("      </div>\n")
        out.write("\n")
        out.write("      <h2 class=\"mt-2\">Actividad</h2>\n")
        out.write("      <div class=\"container border row rounded ml-0 px-4\">\n")
        out.write("        <div id=\"container-actividad\" class=\"col-sm-12\"></div>\n")
        out.write("      </div>\n")
        out.write("    </div>\n")
        out.write("    <!------------------------------ Stickers ------------------------------->\n")
        out.write("    <div class=\"tab-pane container fade\" id=\"menustickers\">\n")
        out.write("      <h1 class=\"mt-2\">Stickers</h1>\n")
        out.write("      <!-- SELECCIÓN DE PARÁMETROS-->\n")
        out.write("      <div id=\"checkstickers\" class=\"container-fluid border rounded px-4 py-2 my-4\"></div>\n")
        out.write("      <!-- TABLA -->\n")
        out.write("      <table id=\"tablaStickers\" class=\"display\">\n")
        out.write("        <thead>\n")
        out.write("          <tr>\n")
        out.write("            <th>Sticker</th>\n")
        out.write("            <th>Apariciones</th>\n")
        out.write("          </tr>\n")
        out.write("        </thead>\n")
        out.write("        <tbody id=\"bodytstickers\"></tbody>\n")
        out.write("      </table>\n")
        out.write("    </div>\n")
        out.write("    <!------------------------------ Palabras ------------------------------->\n")
        out.write("    <div class=\"tab-pane container fade\" id=\"menupalabras\">\n")
        out.write("      <h1 class=\"mt-2\">Palabras</h1>\n")
        out.write("      <!-- SELECCIÓN DE PARÁMETROS-->\n")
        out.write("      <div class=\"container-fluid row border rounded my-4\">\n")
        out.write("        <div class=\"container border-right col-sm-5 px-4 py-2\">\n")
        out.write("          <div class=\"container-fluid px-0\">\n")
        out.write("            <label for=\"minletras\" class=\"mb-1\"><b>Número mínimo de caracteres: <span\n")
        out.write("                  id=\"pminletras\">1</span></b></label>\n")
        out.write("            <input type=\"range\" id=\"minletras\" min=1 max=20 step=1 value=1 class=\"form-control-range\"><br>\n")
        out.write("          </div>\n")
        out.write("          <div id=\"checkpalabras\" class=\"container px-0 mx-0\">\n")
        out.write("            <p class=\"mb-3\"><b>Participantes del chat</b></p>\n")
        out.write("          </div>\n")
        out.write("        </div>\n")
        out.write("        <!-- GRÁFICA -->\n")
        out.write("        <div class=\"container col-sm-7\">\n")
        out.write("          <div id=\"container-palabras\"></div>\n")
        out.write("        </div>\n")
        out.write("      </div>\n")
        out.write("      <!-- TABLA -->\n")
        out.write("      <table id=\"tablaPalabras\" class=\"display\" width=\"100%\">\n")
        out.write("        <thead>\n")
        out.write("          <tr>\n")
        out.write("            <th>Palabra</th>\n")
        out.write("            <th>Apariciones</th>\n")
        out.write("          </tr>\n")
        out.write("        </thead>\n")
        out.write("        <tbody id=\"bodytpalabras\"></tbody>\n")
        out.write("      </table>\n")
        out.write("    </div>\n")
        out.write("    <!------------------------------ Letras ------------------------------->\n")
        out.write("    <div class=\"tab-pane container fade\" id=\"menuletras\">\n")
        out.write("      <h1 class=\"mt-2\">Letras</h1>\n")
        out.write("      <!-- TABLA -->\n")
        out.write("      <table id=\"tablaLetras\" class=\"display\" width=\"100%\"></table>\n")
        out.write("    </div>\n")
        out.write("  </div>\n")
        out.write("  <!--------------------------------------------------------------------------------------------\\n")
        out.write("  |                                    CÓDIGO JAVASCRIPT                                        |\n")
        out.write("  \--------------------------------------------------------------------------------------------->\n")
        out.write("  <script>\n")
        out.write("    var pieColors = (function () {\n")
        out.write("      var colors = [],\n")
        out.write("        base = Highcharts.getOptions().colors[0],\n")
        out.write("        i;\n")
        out.write("\n")
        out.write("      for (i = 0; i < 10; i += 1) {\n")
        out.write("        colors.push(Highcharts.color(base).brighten((i - 3) / 7).get());\n")
        out.write("      }\n")
        out.write("      return colors;\n")
        out.write("    }());\n")
        out.write("    // ------------- DEFINICIÓN DE VARIABLES --------------\n")
        out.write("    nombrechat = \""+chatname+"\";\n")
        out.write("    datamiembros = "+datamensajes+";\n")
        out.write("    datahoras = "+datahoras+";\n")
        out.write("    traduccionstickers = "+json.dumps(codedstickers)+";\n")
        out.write("    datastickers = "+json.dumps(lstickers)+";\n")
        out.write("    datapalabras = "+json.dumps(lwords)+";\n")
        out.write("    dataletras = "+dataletras+";\n")
        out.write("    // --------------------- SCRIPTS ----------------------\n")
        out.write("    $(document).ready(() => {\n")
        out.write("\n")
        out.write("      // ---------------- SCRIPT HOME ---------------------\n")
        out.write("      $(\"#nombrechat\").html(nombrechat);\n")
        out.write("      total = 0;\n")
        out.write("      for (i = 0; i < datamiembros.length; i++) {\n")
        out.write("        miembro = datamiembros[i];\n")
        out.write("        total += miembro.y\n")
        out.write("        $(\"#miembroshome\").append('<p class=\"my-0\">' + miembro.name + ': ' + miembro.y + '</p>')\n")
        out.write("      }\n")
        out.write("      $(\"#totalmensajes\").html(total);\n")
        out.write("      // Chart porcentaje mensajes\n")
        out.write("      Highcharts.chart('container-mensajes', {\n")
        out.write("        chart: {\n")
        out.write("          plotBackgroundColor: null,\n")
        out.write("          plotBorderWidth: null,\n")
        out.write("          plotShadow: false,\n")
        out.write("          type: 'pie'\n")
        out.write("        },\n")
        out.write("        title: {\n")
        out.write("          text: 'Porcentaje de mensajes por miembro del chat'\n")
        out.write("        },\n")
        out.write("        tooltip: {\n")
        out.write("          pointFormat: '{series.name}: <b>{point.y}</b>'\n")
        out.write("        },\n")
        out.write("        accessibility: {\n")
        out.write("          point: {\n")
        out.write("            valueSuffix: '%'\n")
        out.write("          }\n")
        out.write("        },\n")
        out.write("        plotOptions: {\n")
        out.write("          pie: {\n")
        out.write("            allowPointSelect: true,\n")
        out.write("            cursor: 'pointer',\n")
        out.write("            colors: pieColors,\n")
        out.write("            dataLabels: {\n")
        out.write("              enabled: true,\n")
        out.write("              format: '<b>{point.name}</b><br>{point.percentage:.1f} %',\n")
        out.write("              distance: -25,\n")
        out.write("              filter: {\n")
        out.write("                property: 'percentage',\n")
        out.write("                operator: '>',\n")
        out.write("                value: 4\n")
        out.write("              }\n")
        out.write("            }\n")
        out.write("          }\n")
        out.write("        },\n")
        out.write("        series: [{\n")
        out.write("          name: 'Share',\n")
        out.write("          data: datamiembros\n")
        out.write("        }]\n")
        out.write("      });\n")
        out.write("      //Chart actividad por horas\n")
        out.write("      Highcharts.chart('container-actividad', {\n")
        out.write("        chart: {\n")
        out.write("          type: 'column'\n")
        out.write("        },\n")
        out.write("        title: {\n")
        out.write("          text: 'Total de mensajes por hora del día'\n")
        out.write("        },\n")
        out.write("        xAxis: {\n")
        out.write("          type: 'category',\n")
        out.write("          labels: {\n")
        out.write("            style: {\n")
        out.write("              fontSize: '13px',\n")
        out.write("              fontFamily: 'Verdana, sans-serif'\n")
        out.write("            }\n")
        out.write("          }\n")
        out.write("        },\n")
        out.write("        yAxis: {\n")
        out.write("          min: 0,\n")
        out.write("          title: {\n")
        out.write("            text: 'Número de mensajes'\n")
        out.write("          }\n")
        out.write("        },\n")
        out.write("        legend: {\n")
        out.write("          enabled: false\n")
        out.write("        },\n")
        out.write("        tooltip: {\n")
        out.write("          pointFormat: 'Mensajes: <b>{point.y}</b>'\n")
        out.write("        },\n")
        out.write("        series: [{\n")
        out.write("          name: 'Population',\n")
        out.write("          data: datahoras\n")
        out.write("        }]\n")
        out.write("      });\n")
        out.write("      // ---------------- SCRIPT STICKERS ---------------------\n")
        out.write("      for (let i = 0; i < datamiembros.length; i++) {\n")
        out.write("        miembro = datamiembros[i].name;\n")
        out.write("        $(\"#checkstickers\").append('<label class=\"form-check-label mx-3\">' +\n")
        out.write("          '<input type=\"checkbox\" class=\"form-check-input csticker\" checked value=\"' + miembro + '\">' + miembro + '</label>');\n")
        out.write("      }\n")
        out.write("      let cstickerhandler = () => {\n")
        out.write("        //vaciar la tabla\n")
        out.write("        $(\"#bodytstickers\").empty();\n")
        out.write("        checkboxes = $('.csticker');\n")
        out.write("        dataframe = [];\n")
        out.write("        datatable = [];\n")
        out.write("        for (let i = 0; i < checkboxes.length; i++) {\n")
        out.write("          if (checkboxes[i].checked) {\n")
        out.write("            miembro = checkboxes[i].value;\n")
        out.write("            dataframe = combinarstickers(dataframe, datastickers[miembro]);\n")
        out.write("          }\n")
        out.write("        }\n")
        out.write("        dataframe.sort((a,b)=>{return b.cant - a.cant})\n")
        out.write("        for (let i = 0; i < dataframe.length; i++) {\n")
        out.write("          let img = dataframe[i].image;\n")
        out.write("          let cant = dataframe[i].cant;\n")
        out.write("          datatable.push(['<img width=100 src=\"data:image/jpeg;base64,' + traduccionstickers[img] + '\"/>',cant])\n")
        out.write("          //$(\"#bodytstickers\").append('<tr><td><img src=\"data:image/jpeg;base64,' + traduccionstickers[img] + '\"/></td><td>' + cant + '</td></tr>');\n")
        out.write("        }\n")
        out.write("        $('#tablaStickers').DataTable().clear().rows.add(datatable).draw();\n")
        out.write("      }\n")
        out.write("      $('.csticker').change(cstickerhandler);\n")
        out.write("      cstickerhandler();\n")
        out.write("      // ---------------- SCRIPT PALABRAS ---------------------\n")
        out.write("      for (let i = 0; i < datamiembros.length; i++) {\n")
        out.write("        miembro = datamiembros[i].name;\n")
        out.write("        $(\"#checkpalabras\").append('<label class=\"form-check-label mx-3\">' +\n")
        out.write("          '<input type=\"checkbox\" class=\"form-check-input cpalabra\" checked value=\"' + miembro + '\">' + miembro + '</label>');\n")
        out.write("      }\n")
        out.write("      let cpalabrahandler = () => {\n")
        out.write("        //vaciar la tabla\n")
        out.write("        //$(\"#bodytpalabras\").empty();\n")
        out.write("        checkboxes = $('.cpalabra');\n")
        out.write("        dataframe = [];\n")
        out.write("        datatable = [];\n")
        out.write("        datachart = [];\n")
        out.write("        for (let i = 0; i < checkboxes.length; i++) {\n")
        out.write("          if (checkboxes[i].checked) {\n")
        out.write("            miembro = checkboxes[i].value;\n")
        out.write("            dataframe = combinarpalabras(dataframe, datapalabras[miembro]);\n")
        out.write("          }\n")
        out.write("        }\n")
        out.write("        dataframe.sort((a,b)=>{return b.cant - a.cant})\n")
        out.write("        for (let i = 0; i < dataframe.length; i++) {\n")
        out.write("          let pal = dataframe[i].name;\n")
        out.write("          let cant = dataframe[i].cant;\n")
        out.write("          if(pal.length >= $(\"#minletras\").val()){\n")
        out.write("            if (datachart.length < 10) datachart.push([trimstring(pal,20),cant]);\n")
        out.write("            datatable.push([trimstring(pal,60),cant]);\n")
        out.write("          }\n")
        out.write("        }\n")
        out.write("        $('#tablaPalabras').DataTable().clear().rows.add(datatable).draw();\n")
        out.write("        let drawchart = (data) => {\n")
        out.write("          Highcharts.chart('container-palabras', {\n")
        out.write("            chart: {\n")
        out.write("              type: 'column'\n")
        out.write("            },\n")
        out.write("            title: {\n")
        out.write("              text: 'Las 10 palabras más comunes'\n")
        out.write("            },\n")
        out.write("            xAxis: {\n")
        out.write("              type: 'category',\n")
        out.write("              labels: {\n")
        out.write("                rotation: -45,\n")
        out.write("                style: {\n")
        out.write("                  fontSize: '13px',\n")
        out.write("                  fontFamily: 'Verdana, sans-serif'\n")
        out.write("                }\n")
        out.write("              }\n")
        out.write("            },\n")
        out.write("            yAxis: {\n")
        out.write("              min: 0,\n")
        out.write("              title: {\n")
        out.write("                text: 'Apariciones'\n")
        out.write("              }\n")
        out.write("            },\n")
        out.write("            legend: {\n")
        out.write("              enabled: false\n")
        out.write("            },\n")
        out.write("            tooltip: {\n")
        out.write("              pointFormat: 'Apariciones: <b>{point.y}</b>'\n")
        out.write("            },\n")
        out.write("            series: [{\n")
        out.write("              name: 'Population',\n")
        out.write("              data: data\n")
        out.write("            }]\n")
        out.write("          });\n")
        out.write("        }\n")
        out.write("        drawchart(datachart);\n")
        out.write("      }\n")
        out.write("      $('.cpalabra').change(cpalabrahandler);\n")
        out.write("      cpalabrahandler();\n")
        out.write("      $('#minletras').on(\"input\", () => {\n")
        out.write("        $(\"#pminletras\").html($(\"#minletras\").val());\n")
        out.write("      });\n")
        out.write("      $('#minletras').on(\"change\", cpalabrahandler);\n")
        out.write("      $('#tablaPalabras').DataTable();\n")
        out.write("\n")
        out.write("      // ---------------- SCRIPT LETRAS ---------------------\n")
        out.write("      $('#tablaLetras').DataTable({\n")
        out.write("        data: dataletras,\n")
        out.write("        columns: [\n")
        out.write("          { title: \"Letra\" },\n")
        out.write("          { title: \"Apariciones\" }\n")
        out.write("        ]\n")
        out.write("      });\n")
        out.write("    });\n")
        out.write("    function combinarstickers(array1, array2) {\n")
        out.write("      let nuevoarray = [];\n")
        out.write("      for (let i = 0; i < array1.length; i++)\n")
        out.write("        nuevoarray.push(Object.assign({}, array1[i]));\n")
        out.write("      for (let i = 0; i < array2.length; i++) {\n")
        out.write("        found = false;\n")
        out.write("        nuevoelem = array2[i];\n")
        out.write("        for (let j = 0; j < nuevoarray.length; j++) {\n")
        out.write("          elemcomp = nuevoarray[j];\n")
        out.write("          if (elemcomp.image == nuevoelem.image) {\n")
        out.write("            elemcomp.cant += nuevoelem.cant;\n")
        out.write("            found = true;\n")
        out.write("            break;\n")
        out.write("          }\n")
        out.write("        }\n")
        out.write("        if (!found) nuevoarray.push(Object.assign({}, nuevoelem));\n")
        out.write("      }\n")
        out.write("      return nuevoarray;\n")
        out.write("    }\n")
        out.write("    function combinarpalabras(array1, array2) {\n")
        out.write("      let nuevoarray = [];\n")
        out.write("      for (let i = 0; i < array1.length; i++)\n")
        out.write("        nuevoarray.push(Object.assign({}, array1[i]));\n")
        out.write("      for (let i = 0; i < array2.length; i++) {\n")
        out.write("        found = false;\n")
        out.write("        nuevoelem = array2[i];\n")
        out.write("        for (let j = 0; j < nuevoarray.length; j++) {\n")
        out.write("          elemcomp = nuevoarray[j];\n")
        out.write("          if (elemcomp.name == nuevoelem.name) {\n")
        out.write("            elemcomp.cant += nuevoelem.cant;\n")
        out.write("            found = true;\n")
        out.write("            break;\n")
        out.write("          }\n")
        out.write("        }\n")
        out.write("        if (!found) nuevoarray.push(Object.assign({}, nuevoelem));\n")
        out.write("      }\n")
        out.write("      return nuevoarray;\n")
        out.write("    }\n")
        out.write("    function trimstring(str,length){\n")
        out.write("      nstr = str;\n")
        out.write("      if(str.length > length){\n")
        out.write("        nstr = str.substr(0,60) + \"...\";\n")
        out.write("      }\n")
        out.write("      return nstr;\n")
        out.write("    }\n")
        out.write("  </script>\n")
        out.write("</body>\n")
        out.write("\n")
        out.write("</html>\n")

    print("Análisis finalizado. Resultados en: " + filename)

def getIndex(stickerfile):
    idx1 = stickerfile.find("(")+1
    idx2 = stickerfile.find(")")
    idx3 = stickerfile.find("/")+1
    animated = 1 if stickerfile[idx3] == "A" else 0
    if idx1 == 0: 
        return 0, animated
    else: 
        return int(stickerfile[idx1:idx2]), animated

def addAt(list,item,index):
    if index >= len(list):
        for i in range(len(list), index):
            list.append(None)
        list.append(item)
    else:
        list[index] = item
    

class Member:
    def __init__(self, name):
        self.name = name
        self.messagecount = 1
        self.words = {}
        self.stickers = {}
    
    def addmsg(self):
        self.messagecount += 1
    
    def addword(self,word):
        if word in self.words:
            self.words[word] += 1
        else:
            self.words[word] = 1

    def addsticker(self,sticker):
        if sticker in self.stickers:
            self.stickers[sticker] += 1
        else:
            self.stickers[sticker] = 1
    
    def __lt__(self, other):
        return self.messagecount < other.messagecount

def encodeimage(path):
    with open(path,"rb") as imagen:
        coded = str(base64.b64encode(imagen.read()))
        coded = coded[2:len(coded)-1]
    return coded

main()