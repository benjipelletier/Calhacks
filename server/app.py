import os
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import requests, json, re
from flask_cors import CORS, cross_origin

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

    def bounding_box_to_arr(bounding):
        return bounding.split(',')

    def replace_all_bounding(obj):
        if isinstance(obj, dict):
            if "boundingBox" in obj:
                obj['boundingBox'] = bounding_box_to_arr(obj['boundingBox'])
            if 'lines' in obj:
                replace_all_bounding(obj['lines'])
            if 'words' in obj:
                replace_all_bounding(obj['words'])            
        elif isinstance(obj, list):
            for i in obj:
                replace_all_bounding(i)

    replace_all_bounding(result['regions'])

    lines = {}

    def pic_to_dic(obj):
        if isinstance(obj, dict):
            if 'text' in obj:
                if obj['boundingBox'][1] in lines:
                    lines[obj['boundingBox'][1]].append((obj['text'], obj['boundingBox'][0]))
                else:
                    lines[obj['boundingBox'][1]] = []
                    lines[obj['boundingBox'][1]].append((obj['text'], obj['boundingBox'][0]))
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
        lower = dict_range(int(l)-2,2,fixed_lines)
        higher = dict_range(int(l)+1,2, fixed_lines)
        if lower:
            fixed_lines[lower].extend(lines[l])
        elif higher:
            fixed_lines[higher].extend(lines[l])
        elif str(l) in fixed_lines:
            fixed_lines[str(l)]
        else:
            fixed_lines[l] = lines[l]

    important_lines = {}
    
    fixed_lines_as_array = []
    for i in fixed_lines:
        fixed_lines_as_array.append((fixed_lines[i],i))
    fixed_lines_as_array = sorted(fixed_lines_as_array, key=lambda x: int(x[1]))
    
    fixed_lines_as_array_with_string = []

    for i in fixed_lines_as_array:
        i = sorted(i[0], key=lambda x: int(x[1]))
        j = [x[0] for x in i]
        fixed_lines_as_array_with_string.append(" ".join(j))

    print(fixed_lines_as_array_with_string)

    for i in fixed_lines:
        number = False
        text = False
        for j in fixed_lines[i]:
            if re.match("^\d+?\.\d+?$", j[0]):
                number = True
            elif '$' in j[0]:
                print("HI")
                number = True
            else:
                text = True
        if number and text:
            important_lines[i] = fixed_lines[i]

    return fixed_lines_as_array_with_string

app.run(host="0.0.0.0")
