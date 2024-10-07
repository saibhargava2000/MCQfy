from flask import Flask, redirect, request, render_template, jsonify, session, url_for
import json
from Models.audio_to_MCQS import mcqs_from_audio
from Models.text_to_MCQS import mcqs_from_text
from Models.url_to_MCQS import mcqs_from_URL
from Models.data_loaders import *
from werkzeug.utils import secure_filename
from Models.image_2_MCQS import mcqs_from_image
import os
import traceback

app = Flask(__name__)
app.secret_key = 'hjxghkjsuishgkjsfhkjdhkjdhgkjsdhgkjsfhgjk' 
app.config['UPLOAD_FOLDER'] = 'uploads'
FILE_TYPE_EXTENSIONS_ALLOWED = {
    'image': {'jpeg'},
    'document': {'txt', 'pdf', 'docx','csv','html','mp3'}
}

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()

    return jsonify({'error': 'Something went wrong, please try again'}), 500


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/generate_mcqs', methods=['POST'])
def generate_mcqs():
    saved_path = ''
    try:
        input_type = request.form['input_type']
        num_mcqs = request.form['num_mcqs']

        if input_type == 'file':
            file = request.files['file']
            file_type = file.filename.split('.')[-1].lower()

            # Validate file extension
            if file_type not in {'jpeg', 'txt', 'pdf', 'docx', 'csv', 'html', 'mp3'}:
                return jsonify({'error': 'File type not supported'}), 400
            
            if not any(file_type in FILE_TYPE_EXTENSIONS_ALLOWED[ftype] for ftype in FILE_TYPE_EXTENSIONS_ALLOWED):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Save file
            filename = secure_filename(file.filename)
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_path)
            if file_type in FILE_TYPE_EXTENSIONS_ALLOWED['image']:
                mcqs = mcqs_from_image(saved_path,num_mcqs)
            elif file_type in FILE_TYPE_EXTENSIONS_ALLOWED['document']:
                if file_type == 'docx':
                    text = load_doc(saved_path)
                    mcqs = mcqs_from_text(text, num_mcqs)
                elif file_type == 'pdf':
                    text = load_pdf(saved_path)
                    mcqs = mcqs_from_text(text, num_mcqs)
                elif file_type == 'csv':
                    text = load_csv(saved_path)
                    mcqs = mcqs_from_text(text, num_mcqs)
                elif file_type == 'html':
                    text = load_html(saved_path)
                    mcqs = mcqs_from_text(text, num_mcqs)
                elif file_type == 'mp3':
                    print("called audio function")
                    text = mcqs_from_audio(saved_path)
                    mcqs = mcqs_from_text(text,num_mcqs)

        elif input_type == 'text':
            text = request.form['text']
            mcqs = mcqs_from_text(text, num_mcqs)
            session['mcqs'] = mcqs  # Store MCQs in session

        elif input_type == 'url':
            url = request.form['url']
            text = mcqs_from_URL(url)
            mcqs = mcqs_from_text(text,num_mcqs)
            session['mcqs'] = mcqs 

        elif input_type == 'youtube':
            url = request.form['youtube']
            text = load_youtubeurl(url)
            print(text)
            mcqs = mcqs_from_text(text,num_mcqs)
            session['mcqs'] = mcqs

        
    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'error': 'Something went wrong, please try again'}), 500

    return jsonify(mcqs)




if __name__ == '__main__':
    app.run(debug=True)