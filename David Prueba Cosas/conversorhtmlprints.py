with open("pagina.html", "r", encoding="utf-8") as f:
    lineas = f.readlines()
    with open("output.txt", "w", encoding="utf-8") as out:
        for line in lineas:
            line = line.replace("\"","\\\"")
            line = line.replace("\n","")
            out.write("out.write(\""+line+"\\n\")\n")
