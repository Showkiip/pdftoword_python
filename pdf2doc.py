from flask import Flask, request, jsonify
import base64
from pdf2docx import Converter
from io import BytesIO
from docx import Document
from reportlab.pdfgen import canvas

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
            docx_content = base64.b64encode(word_file.read())

        return docx_content
    except Exception as e:
        return jsonify({'error': "Something went wrong ! please try again"}), 500


def convert_docx_to_pdf(file_content):
    try:
        doc = Document(BytesIO(file_content))
        # Create in-memory PDF
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer)
        for element in doc.element.body:
            if element.tag.endswith('p'):
                text = element.text
                c.drawString(100, 800, text)  # Adjust coordinates as needed
        c.save()

        # Reset buffer position and return PDF content
        pdf_buffer.seek(0)
        return pdf_buffer.read()
    except Exception as e:
        return jsonify({'error': "Something went wrong ! please try again"}), 500


@app.route('/convert', methods=['POST'])
def index():
    try:
        content = request.json
        file_content = base64.b64decode(content['file'])

        if content['type'] == "pdftodocx":
            result_content = convert_pdf_to_docx(file_content)

        elif content['type'] == "docxtopdf":
            result_content = convert_docx_to_pdf(file_content)
        else:
            return jsonify({'error': 'Invalid conversion type'})

        return jsonify({'converted_file': base64.b64encode(result_content).decode('utf-8')})
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error during conversion: {str(e)}")
        return jsonify({'error': f'An error occurred during conversion : {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)
