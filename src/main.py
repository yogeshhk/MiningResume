import os
from flask import Flask, render_template, request, flash, redirect
from parser import CONFIG_FILE, parse_document, read_config, read_document
from tempfile import TemporaryDirectory
import pathlib

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

TEMP_DIR = pathlib.Path(TemporaryDirectory().name)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def parse_file():
    if request.method == "POST":
        directory = (request.files.getlist("file"))
        results = {}
        try:
            if directory[0].filename:
                for file in directory:
                    if file and allowed_file(file.filename):
                        file_path = TEMP_DIR / pathlib.Path(file.filename)
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file.save(file_path)
                        config = read_config(CONFIG_FILE)
                        document = read_document(file_path)

                        result = parse_document(document, config)
                        results[file_path.name] = {}
                        for key, value in result.items():
                            results[file_path.name].update(value)
                return render_template("result.html", result=results)
            return render_template("main.html", error="Please select a valid Directory")
        except:
            return render_template("main.html", error="Something Went Wrong. Please try again.")

    return render_template("main.html")


if __name__ == "__main__":
    app.run(debug=True)
