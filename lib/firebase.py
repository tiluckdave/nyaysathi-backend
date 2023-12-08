import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate('lib/key.json')

app = firebase_admin.initialize_app(cred, {'storageBucket': 'nyaysathi.appspot.com'})

bucket = storage.bucket()

def uploadFile(filename, path):
    try:
        blob = bucket.blob(f"{filename}.txt")
        blob.upload_from_filename(path)
        blob.make_public()
    except Exception as e:
        print(e)
        return False
    return True

def fileExists(filename):
    try:
        blob = bucket.blob(filename)
        return blob.exists()
    except Exception as e:
        print(e)
        return False
    return True

def getFileContent(filename):
    try:
        blob = bucket.blob(filename)
        return blob.download_as_string().decode("utf-8")
    except Exception as e:
        print(e)
        return False
    return True

