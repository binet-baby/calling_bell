<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />

# Aarada Nee 🎯

## Basic Details
### Team Name: lowkey tech

### Team Members
- Team Lead: Jyothika K S - Viswajyothi College Of Engineering And Technology
- Member 2: Binet Baby - Viswajyothi College Of Engineering And Technology

### Project Description
Aarada Nee is a ridiculously over-engineered smart doorbell system. It uses advanced AI facial recognition through a web browser to detect who is at your door and automatically blasts customized, random audio clips depending on whether the visitor is a known friend or a complete stranger. 

### The Problem (that doesn't exist)
Standard calling bells are boring. "Ding-dong" is so last century, and physically walking to the door to see who is there is exhausting. Furthermore, when your friends visit, they aren't properly announced with the dramatic background music they deserve. 

### The Solution (that nobody asked for)
We built an AI-powered doorbell that uses heavy machine learning models (InsightFace) just to play a sound! When someone stands in front of the camera, the app scans their face in real-time. If it's a known person (registered in the settings), it plays a random audio clip from the "known" folder (like a royal entrance). If it's a stranger, it plays a sound from the "unknown" folder (like a dramatic boss-fight theme). It's essentially a theme-music generator for your front door.

## Technical Details
### Technologies/Components Used
For Software:
- **Languages used:** Python, JavaScript, HTML, CSS
- **Frameworks used:** Flask (Python Web Framework)
- **Libraries used:** 
  - `insightface` & `onnxruntime` (For AI facial recognition)
  - `opencv-python-headless` (For image processing)
  - `numpy` (For mathematical embeddings)
- **Tools used:** HTML5 WebRTC (for client-side camera capture), Fetch API

For Hardware:
- *(Optional: List if you are actually mounting a screen/camera to a door, e.g., Raspberry Pi, USB Webcam)*
- N/A (Runs completely in a web browser and cloud backend)

### Implementation
For Software:
# Installation
```bash
# Clone the repository
git clone <repo-url>
cd calling_bell

# Install required Python packages
pip install -r requirements.txt
```

# Run
```bash
# Run locally
python app.py

# Or run using Gunicorn (for production/Render deployment)
gunicorn app:app
```

### Project Documentation
For Software:

# Screenshots (Add at least 3)
![Screenshot1](dummy.png)
*Home screen showing the live camera feed and facial recognition bounding boxes.*

![Screenshot2](dummy.png)
*Settings page where new faces can be registered and saved to the JSON database.*

![Screenshot3](dummy.png)
*Audio triggered in the browser when a known face is successfully matched.*

# Diagrams
![Workflow](dummy.png)
*Workflow: The client browser captures a webcam frame via WebRTC, sends it as Base64 JSON via POST to the Flask backend. Flask decodes it, runs it through InsightFace to generate embeddings, compares it against known faces using Euclidean distance, and returns the bounding boxes and match status back to the client to draw on the HTML5 Canvas.*

For Hardware:
*(N/A - This is a software-based web app)*

### Project Demo
# Video
[Add your demo video link here]
*A quick demonstration of registering a face, stepping in front of the camera, and hearing the custom doorbell sound trigger.*

# Additional Demos
[Add any extra demo materials/links]

## Team Contributions
- Jyothika K S: [Specific contributions - e.g., Frontend UI, Audio triggering logic]
- Binet Baby: [Specific contributions - e.g., Backend architecture, InsightFace integration]

---
Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)
