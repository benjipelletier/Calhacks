import os
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import requests, json, re
from flask_cors import CORS, cross_origin
import img2

app = Flask(__name__)
CORS(app)
@app.route('/', methods=['GET'])
def index():
    print(request.args.get('data'))
    if request.method == 'GET':
        img_url = request.args.get('data')
        result = betterSplit(img_url)
        print(result)
        return jsonify(result)
    else:
        return "hello"

def betterSplit(image):
    headers = {
        'Ocp-Apim-Subscription-Key': '20fb739c7d1a41cd9ec66b1ab9713600',
        'Content-Type': 'application/json',
    }

    r = requests.post('https://api.projectoxford.ai/vision/v1/ocr',
            json = {"Url": image}, headers = headers)

    result = r.json()

    print("hello",result)
    
    text_bounding = []

    def replace_all_bounding(obj):
        if isinstance(obj, dict):
            if "boundingBox" in obj:
                obj['boundingBox'] = obj['boundingBox'].split(',')
            if 'lines' in obj:
                replace_all_bounding(obj['lines'])
            if 'words' in obj:
                for i in obj['words']:
                    bb = i['boundingBox'].split(',')
                    text_bounding.append(bb)
                replace_all_bounding(obj['words'])         
        elif isinstance(obj, list):
            for i in obj:
                replace_all_bounding(i)

    replace_all_bounding(result['regions'])

    circles, squares, diamonds, triangles = img2.clearImg(text_bounding,image)

    lines = {}

    def pic_to_dic(obj):
        if isinstance(obj, dict):
            if 'text' in obj:
                if obj['boundingBox'][1] in lines:
                    lines[obj['boundingBox'][1]].append([obj['text'], obj['boundingBox'][0]])
                else:
                    lines[obj['boundingBox'][1]] = []
                    lines[obj['boundingBox'][1]].append([obj['text'], obj['boundingBox'][0]])
            if 'lines' in obj:
                pic_to_dic(obj['lines'])
            if 'words' in obj:
                pic_to_dic(obj['words'])            
        elif isinstance(obj, list):
            for i in obj:
                pic_to_dic(i)

    pic_to_dic(result['regions'])

    fixed_lines = {}

    def dict_range(start, ra, dictionary):
        for i in range(start, start+ra):
            if str(i) in dictionary:
                return str(i)
        return False

    for l in lines:
        lower = dict_range(int(l)-5,5,fixed_lines)
        higher = dict_range(int(l)+1,5, fixed_lines)
        if lower:
            fixed_lines[lower].extend(lines[l])
        elif higher:
            fixed_lines[higher].extend(lines[l])
        elif str(l) in fixed_lines:
            fixed_lines[str(l)]
        else:
            fixed_lines[l] = lines[l]
    
    fixed_lines_as_array = []
    for i in fixed_lines:
        fixed_lines_as_array.append([fixed_lines[i],i])
    fixed_lines_as_array = sorted(fixed_lines_as_array, key=lambda x: int(x[1]))

    fixed_lines_as_array_with_string = []

    for i in fixed_lines_as_array:
        v = [sorted(i[0], key=lambda x: int(x[1])),i[1]]
        j = [x[0] for x in v[0]]
        fixed_lines_as_array_with_string.append([" ".join(j),i[1]])

    reciept = {'items':[],'total':None}
    
    for i in fixed_lines_as_array_with_string:
        r = requests.get("https://api.wit.ai/message?v=20161112&q="+i[0]+"&access_token=ZIULONOT7SHPJ4AUAKPMK5FXGJSZ2Q3L")
        r = r.json()
        if r['outcomes'][0]['confidence'] > .5:
            if r['outcomes'][0]['intent'] == "Item":
                try:
                    float(r['outcomes'][0]['entities']['price'][0]['value'])
                    reciept['items'].append([r['outcomes'][0]['entities']['item'][0]['value'],r['outcomes'][0]['entities']['price'][0]['value'],i[1]])
                except:
                    print("NOOO")
            elif r['outcomes'][0]['intent'] == "Total":
                try:
                    reciept['total'] = r['outcomes'][0]['entities']['price'][0]['value']
                except:
                    pass

    print("c",len(circles),"t",len(triangles),"s",len(squares),"d",len(diamonds))
    print(squares)

    for i in circles:
        for j in reciept['items']:
            if abs(int(j[2])-i) < 8:
                j.append("circle")

    for i in squares:
        for j in reciept['items']:
            if abs(int(j[2])-i) < 8:
                j.append("square")

    for i in triangles:
        for j in reciept['items']:
            if abs(int(j[2])-i) < 8:
                j.append("triangle")

    for i in diamonds:
        for j in reciept['items']:
            if abs(int(j[2])-i) < 8:
                j.append("diamond")

    for i in reciept['items']:
        print(i)
        i.pop(2)
        print(i)


    return reciept
betterSplit("https://lh3.googleusercontent.com/z9DvcxTAY3zFXhlJqcKb6ma0f6Xu9hLNloHAI_iIzvhkAHY6ktJFN99tuu3-25lNacE_cphmRWP2kVAfBVcoH1ZQqAPhx0Z-QF5OwQIi29MteoAJ6P2sxXqrxigtbNr9nsy9oX9jaP0Mg_6JpQtdmDg1Un_UWtPf3Th_dgcPIlPAeAQWoYX6gbcqWXr1Y0JVzlekUGISPrrM1CbGWGW0lgQ9gdMQ1kZmWPd8PVE-yQZ4cwMrXOuyf31npAnB7sHAOVoPnSrrav3H0xMcKz94n3VqUmqr77V1CO2LoJ5nQZZ9Oa5yCye63zY6op1yTpQUh760m8ng60aV3lRGtlrRHy52IAaU7H8s4uEynrT7rBGCu8CuD6xJnFW8iIWGg8Ne-xgkqNF1NRIxwouFEL2TYCZa00IJ1sh6VuEiTjwx24G8jkBF8-q4jDrwUZPYqaf6j8XVsNxnqB3HAOREdpvBfsemTrfKUwgmeQpNhSd66-fSY1swCCz24_io-CwkD0J6JjeWlJk1OpPJ6_VC89zfmxYuSPxeh_HzbUV__r0ylFXC2uapi_vpSX5Y79uj7NuZQyMni40=s950-w713-h950-no")
#app.run(host="0.0.0.0")
