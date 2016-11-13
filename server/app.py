import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import requests, json, re

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        betterSplit(file)
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


def betterSplit(image):
    headers = {
        'Ocp-Apim-Subscription-Key': '20fb739c7d1a41cd9ec66b1ab9713600',
        'Content-Type': 'application/json',
    }

    r = requests.post('https://api.projectoxford.ai/vision/v1/ocr',
            json = {"Url": image}, headers = headers)

    result = r.json()
    
    def replace_all_bounding(obj):
        if isinstance(obj, dict):
            if "boundingBox" in obj:
                obj['boundingBox'] = obj['boundingBox'].split(',')
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
            
    for i in fixed_lines_as_array_with_string:
        r = requests.get("https://api.wit.ai/message?v=20161112&q="+i+"&access_token=ZIULONOT7SHPJ4AUAKPMK5FXGJSZ2Q3L")
        print(r.json())

    return fixed_lines_as_array_with_string



        