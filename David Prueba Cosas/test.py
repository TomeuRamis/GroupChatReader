# import base64

# def main():
#     encoded = encodeimage("stickers/sticker (1).webp_thumb.jpg")

#     with open("iamgen.txt", "w", encoding="utf-8") as pagina:
#         #pagina.write("<img src=\"data:image/jpeg;base64,"+encoded+"\"/>")
#         pagina.write(encoded)

# def encodeimage(path):
#     with open(path,"rb") as imagen:
#         coded = str(base64.b64encode(imagen.read()))
#         coded = coded[2:len(coded)-1]
#     return coded

# main()

import json
a = {
    "carlos":[{"image":0,"cant":2},{"image":1,"cant":5}],
    "federico":[{"image":0,"cant":12},{"image":1,"cant":9}]}
ajson = json.dumps(a)
print(ajson)