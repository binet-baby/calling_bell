import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, Response
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import time

visitor_state = {"name": None, "time": 0}

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Configurations
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'known_faces')
DATA_FILE = os.path.join(BASE_DIR, 'people.json')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder and data file exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_people():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_people(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Global variables for face recognition
try:
    import insightface
    from insightface.app import FaceAnalysis
    # Initialize InsightFace (using the lightweight buffalo_sc model)
    face_app = FaceAnalysis(name='buffalo_sc', allowed_modules=['detection', 'recognition'])
    face_app.prepare(ctx_id=0, det_size=(640, 640))
except ImportError:
    face_app = None
    print("InsightFace not installed. Face recognition will not work.")

# The tolerance threshold for matching faces (Euclidean distance).
# Lower distance means a closer match. For ArcFace, < 1.0 to 1.2 is typically a good match.
FACE_MATCH_THRESHOLD = 1.0

known_face_encodings = []
known_face_names = []

def reload_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    
    if face_app is None:
        return
        
    people = load_people()
    for person in people:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], person['image'])
        if os.path.exists(file_path):
            img = cv2.imread(file_path)
            if img is not None:
                # Detect faces and extract embeddings
                faces = face_app.get(img)
                if len(faces) > 0:
                    # Save the numerical embedding (a vector representing the face)
                    raw_embedding = faces[0].embedding
                    # Normalize the embedding to a unit vector so distances are bounded (0 to 2)
                    embedding = raw_embedding / np.linalg.norm(raw_embedding)
                    
                    known_face_encodings.append(embedding)
                    known_face_names.append(person['name'])
                    print(f"DEBUG: Successfully encoded face for {person['name']}")
                else:
                    print(f"DEBUG: No face detected in {person['image']}. This identity was NOT encoded.")
            else:
                print(f"DEBUG: Failed to read image for {person['name']}")
        else:
            print(f"DEBUG: Image file missing for {person['name']}")
            
    print(f"DEBUG: Loaded {len(known_face_names)} registered faces into memory.")

# Load faces when the app starts
reload_known_faces()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings():
    people = load_people()
    return render_template('settings.html', people=people)

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    if not name:
        flash('Name is required!', 'error')
        return redirect(url_for('settings'))

    if 'photo' not in request.files:
        flash('No photo selected!', 'error')
        return redirect(url_for('settings'))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No photo selected!', 'error')
        return redirect(url_for('settings'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not filename:
            flash('Invalid filename!', 'error')
            return redirect(url_for('settings'))
            
        # Create a unique filename if necessary, but for simplicity we'll just save it
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Update JSON data
        people = load_people()
        people.append({
            'name': name,
            'image': filename
        })
        save_people(people)
        
        # Reload known faces in memory
        reload_known_faces()
        
        flash('Person registered successfully!', 'success')
        return redirect(url_for('settings'))
    else:
        flash('Invalid file type! Please upload an image.', 'error')
        return redirect(url_for('settings'))

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    # 1. Update JSON data by filtering out the deleted person
    people = load_people()
    people = [p for p in people if p['image'] != filename]
    save_people(people)
    
    # Reload known faces in memory
    reload_known_faces()

    # 2. Delete the face image file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Ignore errors if the file is already missing or locked
        pass

    flash('Person deleted successfully!', 'success')
    return redirect(url_for('settings'))

@app.route('/known_faces/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def generate_frames():
    # Attempt to open the webcam
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break
            
        if face_app is not None:
            # Detect and extract embeddings for live face
            faces = face_app.get(frame)
            
            for face in faces:
                bbox = face.bbox.astype(int)
                x, y, x2, y2 = bbox
                
                raw_embedding = face.embedding
                # Normalize the live embedding to match the stored normalized encodings
                embedding = raw_embedding / np.linalg.norm(raw_embedding)
                
                name = "Unknown Visitor"
                color = (0, 0, 255) # Red for unknown
                best_distance = 999.0
                
                if len(known_face_encodings) > 0:
                    # Compare live embedding with ALL known encodings
                    distances = [np.linalg.norm(embedding - known_emb) for known_emb in known_face_encodings]
                    min_idx = np.argmin(distances)
                    best_distance = distances[min_idx]
                    
                    print(f"DEBUG: Closest match -> {known_face_names[min_idx]} (Distance: {best_distance:.2f}, Threshold: {FACE_MATCH_THRESHOLD})")
                    
                    if best_distance < FACE_MATCH_THRESHOLD:
                        name = f"Known: {known_face_names[min_idx]}"
                        color = (0, 255, 0) # Green for known
                        visitor_state['name'] = known_face_names[min_idx]
                        visitor_state['time'] = time.time()
                        print("DEBUG: Result -> KNOWN")
                    else:
                        print("DEBUG: Result -> UNKNOWN (Distance too high)")
                        visitor_state['name'] = "stranger"
                        visitor_state['time'] = time.time()
                else:
                    print("DEBUG: Result -> UNKNOWN (No registered faces)")
                    visitor_state['name'] = "stranger"
                    visitor_state['time'] = time.time()

                # Draw a box around the face
                cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
                
                # Draw a label with a name above the face
                cv2.rectangle(frame, (x, y-35), (x2, y), color, cv2.FILLED)
                cv2.putText(frame, name, (x + 6, y - 6), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

        # Encode the frame into JPEG to stream to the browser
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    camera.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_visitor')
def get_visitor():
    from flask import jsonify
    # Only return the visitor if they were seen in the last 2 seconds
    if time.time() - visitor_state['time'] < 2.0:
        return jsonify({"visitor": visitor_state['name']})
    else:
        return jsonify({"visitor": None})

@app.route('/random_audio')
def random_audio():
    from flask import jsonify, request, url_for
    import random
    
    visitor_type = request.args.get('type', 'known')
    if visitor_type not in ['known', 'unknown']:
        visitor_type = 'known'
        
    audio_dir = os.path.join(app.root_path, 'static', 'audio', visitor_type)
    if not os.path.exists(audio_dir):
        return jsonify({"error": f"Directory missing. Please create static/audio/{visitor_type}/."}), 404
        
    files = [f for f in os.listdir(audio_dir) if f.lower().endswith(('.mp3', '.wav'))]
    if not files:
        return jsonify({"error": f"No audio files found in static/audio/{visitor_type}/."}), 404
        
    selected = random.choice(files)
    return jsonify({
        "audio_url": url_for('static', filename=f'audio/{visitor_type}/{selected}'),
        "filename": selected
    })

if __name__ == '__main__':
    app.run(debug=True)
