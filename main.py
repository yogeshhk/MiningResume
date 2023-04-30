import os
from flask import Flask,render_template,request,flash,redirect
from src.parser import CONFIG_FILE, parse_document, read_config,read_document
from tempfile import TemporaryDirectory
import pathlib

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

TEMP_DIR =pathlib.Path(TemporaryDirectory().name)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/",methods=["GET","POST"])
def parse_file():
    if request.method == "POST":
        file = (request.files.get("file"))
        if file and allowed_file(file.filename):
            file_path = TEMP_DIR / file.filename
            file.save(file_path)
            config = read_config(CONFIG_FILE)
            document = read_document(file_path)
            
            result = parse_document(document, config)
            print(result)

    return render_template("main.html")



if __name__ == "__main__":
    app.run(debug=True)