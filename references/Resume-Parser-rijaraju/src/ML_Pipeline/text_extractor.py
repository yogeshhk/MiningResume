from tika import parser
import os


def convert_pdf_to_text(dir):
    output = []
    for root, dirs, files in os.walk(dir):
        print(files)
        for file in files:
            path_to_pdf = os.path.join(root, file)
            [stem, ext] = os.path.splitext(path_to_pdf)
            if ext == ".pdf":
                print("Processing " + path_to_pdf)
                pdf_contents = parser.from_file(path_to_pdf, service="text")
                path_to_txt = stem + ".txt"
                output.append(pdf_contents["content"])
    return output

