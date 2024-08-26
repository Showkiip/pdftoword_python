from flask import Flask, request, jsonify
import base64
from pdf2docx import Converter
from io import BytesIO
from docx import Document
from fpdf import FPDF
import os

app = Flask(__name__)


def convert_pdf_to_docx(file_content):
    try:
        pdf_path = 'temp_input.pdf'
        word_path = 'temp_output.docx'

        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(file_content)

        cv = Converter(pdf_path)
        cv.convert(word_path, start=0, end=None)
        cv.close()

        # Read the converted Word file and encode it to base64
        with open(word_path, 'rb') as word_file:
            docx_content = base64.b64encode(word_file.read()).decode('utf-8')

        # Clean up temp files
        os.remove(pdf_path)
        os.remove(word_path)

        return jsonify({'converted_file': docx_content})
    except Exception as e:
        return jsonify({'error': f"Something went wrong: {str(e)}"}), 500


def convert_docx_to_pdf(file_content):
    try:
        doc = Document(BytesIO(file_content))
        pdf_buffer = BytesIO()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for para in doc.paragraphs:
            pdf.multi_cell(0, 10, para.text)

        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        # Encode to base64
        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')

        return jsonify({'converted_file': pdf_base64})
    except Exception as e:
        return jsonify({'error': f"Something went wrong: {str(e)}"}), 500


@app.route('/convert', methods=['POST'])
def index():
    try:
        content = request.json
        file_content = base64.b64decode(content['file'])

        if content['type'] == "pdftodocx":
            result = convert_pdf_to_docx(file_content)

        elif content['type'] == "docxtopdf":
            result = convert_docx_to_pdf(file_content)
        else:
            return jsonify({'error': 'Invalid conversion type'}), 400

        return result
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return jsonify({'error': f'An error occurred during conversion: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
