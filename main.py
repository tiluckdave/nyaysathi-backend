from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pdf2image import convert_from_bytes
from lib.kanoon import searchKanoon, getDocument
from lib.llm import generateResponse, getAct, generateChatResponse, visionOCR, SummarizeLegalText
from lib.firebase import uploadFile, fileExists, getFileContent, uploadOtherFile
from lib.utils import htmlToText, createFileWithContent, deleteFile, encodeImage

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/ask', methods=['POST'])
@cross_origin()
def ask():
    question = request.json['question']
    act = getAct(question)
    print(act)
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
    response = generateResponse(text, question)
    return jsonify({'act': act, 'answer': response})

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
    summary = SummarizeLegalText(text)
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
    print(publicUrl)
    if publicUrl != False:
        deleteFile(fileurl)
    return jsonify({'url': publicUrl})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)