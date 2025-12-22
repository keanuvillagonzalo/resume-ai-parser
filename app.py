from flask import Flask, render_template, request, jsonify
import os
import sqlite3
import database
from gemini_service import GeminiService
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("API_KEY")
DATABASE_URL=os.getenv("DATABASE_URL")



# Initialize your service


AI_SERVICE = GeminiService(api_key=API_KEY)




app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'uploads'


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)




# Helper function to save to DB


def save_to_db(filename, experience_json):


    conn = sqlite3.connect(DATABASE_URL)


    c = conn.cursor()


    c.execute("CREATE TABLE IF NOT EXISTS parsed_resumes (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, experience_json TEXT)")


    c.execute("INSERT INTO parsed_resumes (filename, experience_json) VALUES (?, ?)", (filename, experience_json))


    conn.commit()


    conn.close()





@app.route('/')


def index():
    return render_template('index.html')



@app.route('/upload_resume')


def upload_resume():


    return render_template('resume-parser.html')    



@app.route('/upload', methods=['POST'])


def upload_file():


    if 'resume' not in request.files:


        return jsonify({"error": "No file uploaded"}), 400


    


    file = request.files['resume']


    if file.filename == '':


        return jsonify({"error": "No selected file"}), 400



    # Save file


    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)


    file.save(file_path)


    print(f"File saved to {file_path}")



    try:


        # Step 1: Extract


        print("Extracting text...")


        raw_text = AI_SERVICE.extract_text(file_path)


        


        # Step 2: Gemini Parsing


        print("Calling Gemini 2.5 Flash-Lite...")


        structured_data = AI_SERVICE.parse_resume(raw_text)


        save_to_db(file.filename, structured_data)


        


        return jsonify({"success": True, "data": structured_data})


    


    except Exception as e:


        print(f"Error: {str(e)}")


        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/match', methods=['POST'])


def match():


    jd = request.json.get('job_description')


    


    # 1. Grab the latest parsed resume from DB


    conn = sqlite3.connect(DATABASE_URL)


    c = conn.cursor()


    c.execute("SELECT experience_json FROM parsed_resumes ORDER BY id DESC LIMIT 1")


    row = c.fetchone()


    conn.close()



    if not row:


        return jsonify({"error": "No resumes found in database"}), 404



    # 2. Let Gemini reason through the match


    analysis = AI_SERVICE.match_experience_to_jd(row[0], jd)


    


    return jsonify({"analysis": analysis})




@app.route('/resumes', methods=['GET'])


def get_resumes():


    conn = sqlite3.connect(DATABASE_URL)


    c = conn.cursor()


    # Fetch all resumes (ID and Filename)


    c.execute("SELECT id, filename FROM parsed_resumes")


    resumes = [{"id": row[0], "filename": row[1]} for row in c.fetchall()]


    conn.close()


    return jsonify(resumes)



@app.route('/delete/<int:resume_id>', methods=['DELETE'])


def delete_resume(resume_id):


    try:


        conn = sqlite3.connect(DATABASE_URL)


        c = conn.cursor()


        


        # Optional: Delete the physical file too


        c.execute("SELECT filename FROM parsed_resumes WHERE id=?", (resume_id,))


        row = c.fetchone()


        if row:


            file_path = os.path.join('uploads', row[0])


            if os.path.exists(file_path):


                os.remove(file_path)


        


        # Delete from DB


        c.execute("DELETE FROM parsed_resumes WHERE id=?", (resume_id,))


        conn.commit()


        conn.close()


        return jsonify({"success": True})


    except Exception as e:


        return jsonify({"success": False, "error": str(e)}), 500





if __name__ == '__main__':
    database.test_db_connection()

    app.run(debug=True)