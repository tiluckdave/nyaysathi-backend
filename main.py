import requests
import string
import random
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pdf2image import convert_from_bytes
from lib.kanoon import searchKanoon, getDocument
from lib.llm import generateResponse, getAct, generateChatResponse, visionOCR, SummarizeLegalText, getKYR, getSpecs, regenerateResponse
# from google.cloud import texttospeech
from lib.firebase import uploadFile, fileExists, getFileContent, uploadOtherFile
from lib.utils import htmlToText, createFileWithContent, deleteFile, encodeImage, banglaSpeechTOText
import datetime

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/test', methods=['GET'])
@cross_origin()
def test():
    return jsonify({'message': 'Hello World'})

@app.route('/ask', methods=['POST'])
@cross_origin()
def ask():
    question = request.json['question']
    act = getAct(question)
    specs = getSpecs(question)
    print(act)
    print(specs)
    docs = searchKanoon(act)
    text = ""
    sdocs = []
    for doc in docs[:5]:
        docid = doc['tid']
        sdocs.append(docid)
        print(docid)
        if not fileExists(f"{docid}.txt"):
            content = getDocument(docid)
            print(content)
            parsedContent = htmlToText(content)
            path = createFileWithContent(docid, parsedContent)
            status = uploadFile(docid, path)
            if status:
                deleteFile(path)
        text += getFileContent(f"{docid}.txt") + "\n\n\n\n"
    response = generateResponse(text, question)
    apikey = 'dNfhDO4BhWNrZ6CbAXBkaCIubUV5m9P6bA1SgF8b'
    voice = 'salman'
    url = f'https://api.narakeet.com/text-to-speech/m4a?voice={voice}'

    options = {
        'headers': {
            'Accept': 'application/octet-stream',
            'Content-Type': 'text/plain',
            'x-api-key': apikey,
        },
        'data': response.encode('utf8')
    }
    with open('./files/output.m4a', 'wb') as f:
        f.write(requests.post(url, **options).content)
    status = uploadOtherFile(f"{current_time}_hello.m4a", "./files/output.m4a")
    if status:
        deleteFile("./files/output.m4a")
    return jsonify({'act': act, 'voice':status, 'answer': response, 'specs': specs, 'docs': sdocs})


@app.route('/ask-voice', methods=['POST'])
@cross_origin()
def askVoice():
    current_time = datetime.datetime.now().strftime("%H%M%S")
    print(request.files['file'])
    file = request.files['file']
    # lang = request.form.get('lang')
    file.save(f"files/{current_time}_hello.wav")
    fileurl = f"./files/{current_time}_hello.wav"
    banglaText = banglaSpeechTOText(fileurl)
    act = getAct(banglaText)
    specs = getSpecs(banglaText)
    docs = searchKanoon(act)
    text = ""
    sdocs = []
    for doc in docs[:5]:
        docid = doc['tid']
        sdocs.append(docid)
        print(docid)
        if not fileExists(f"{docid}.txt"):
            content = getDocument(docid)
            print(content)
            parsedContent = htmlToText(content)
            path = createFileWithContent(docid, parsedContent)
            status = uploadFile(docid, path)
            if status:
                deleteFile(path)
        text += getFileContent(f"{docid}.txt") + "\n\n\n\n"
    response = generateResponse(text, banglaText)
    apikey = 'dNfhDO4BhWNrZ6CbAXBkaCIubUV5m9P6bA1SgF8b'
    voice = 'salman'
    url = f'https://api.narakeet.com/text-to-speech/m4a?voice={voice}'

    options = {
        'headers': {
            'Accept': 'application/octet-stream',
            'Content-Type': 'text/plain',
            'x-api-key': apikey,
        },
        'data': response.encode('utf8')
    }
    with open('./files/output.m4a', 'wb') as f:
        f.write(requests.post(url, **options).content)
    status = uploadOtherFile(f"{current_time}_hello.m4a", "./files/output.m4a")
    if status:
        deleteFile("./files/output.m4a")
    return jsonify({'act': act,'question':banglaText, 'voice':status, 'answer': response, 'specs': specs, 'docs': sdocs})

@app.route('/reask', methods=['POST'])
@cross_origin()
def reask():
    response = request.json['response']
    question = request.json['question']
    docs = request.json['docs']
    text = ""
    for doc in docs:
        text += getFileContent(f"{doc}.txt") + "\n\n\n\n"
    response = regenerateResponse(text, question, response)
    apikey = 'dNfhDO4BhWNrZ6CbAXBkaCIubUV5m9P6bA1SgF8b'
    voice = 'salman'
    url = f'https://api.narakeet.com/text-to-speech/m4a?voice={voice}'

    options = {
        'headers': {
            'Accept': 'application/octet-stream',
            'Content-Type': 'text/plain',
            'x-api-key': apikey,
        },
        'data': response.encode('utf8')
    }
    with open('./files/output.m4a', 'wb') as f:
        f.write(requests.post(url, **options).content)
    status = uploadOtherFile(f"{current_time}_hello.m4a", "./files/output.m4a")
    if status:
        deleteFile("./files/output.m4a")
    return jsonify({'answer': response, 'voice': status})
    
@app.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    act = request.json['act']
    previousContext = request.json['context']
    followUpQuestion = request.json['question']
    docs = searchKanoon(act)
    text = ""
    for doc in docs[:5]:
        docid = doc['tid']
        print(docid)
        if not fileExists(f"{docid}.txt"):
            content = getDocument(docid)
            print(content)
            parsedContent = htmlToText(content)
            path = createFileWithContent(docid, parsedContent)
            status = uploadFile(docid, path)
            if status:
                deleteFile(path)
        text += getFileContent(f"{docid}.txt") + "\n\n\n\n"
    response = generateChatResponse(text, previousContext, followUpQuestion)
    return jsonify({'answer': response})

@app.route('/summarize', methods=['POST'])
@cross_origin()
def summarize():
    file = request.files['file']
    lang = request.form.get('lang')
    filename = file.filename
    print(filename)
    file.save(f"files/{filename}")
    fileurl = "./files/" + filename
    print(fileurl)
    fileExt = fileurl.split(".")[-1]
    text = ""
    imgs = []
    if fileExt != "pdf":
        imgs.append(encodeImage(fileurl))
        text = visionOCR(imgs)
    else:
        images = convert_from_bytes(open(fileurl, 'rb').read())
        for i in range(len(images)):
            images[i].save(f"images/{i}.png", 'PNG')
            imgs.append(encodeImage(f"images/{i}.png"))
        text = visionOCR(imgs)
    summary = SummarizeLegalText(text, lang)
    return jsonify({'summary': summary})

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload():
    file = request.files['file']
    filename = file.filename
    print(filename)
    file.save(f"files/{filename}")
    fileurl = "./files/" + filename
    publicUrl = uploadOtherFile(filename, fileurl)
    if publicUrl != False:
        deleteFile(fileurl)
    return jsonify({'url': publicUrl})


@app.route('/kyr', methods=['POST'])
@cross_origin()
def kyr():
    age = request.json['age']
    gender = request.json['gender']
    city = request.json['city']
    state = request.json['state']
    profession = request.json['profession']
    
    data = f"Tell me my rights as {gender}, {age} years old. Living in ${city}, ${state}. I am ${profession} by profession."
    rights = getKYR(data)
    rights = rights.split("\n")
    rights = list(filter(None, rights))
    rights = [right[2:] for right in rights]
    rights = [right.strip() for right in rights]
    print(rights)
    return jsonify({'rights': rights})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)