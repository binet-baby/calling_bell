document.addEventListener('DOMContentLoaded', () => {
    console.log('Aarada Ne project loaded successfully!');
    
    let lastPlayedVisitor = null;
    let lastPlayedTime = 0;
    const COOLDOWN_MS = 10000; // 10 seconds cooldown between plays
    
    let autoplayBlocked = false;
    
    // Listen for user interaction to clear autoplay block warning
    document.body.addEventListener('click', () => {
        if (autoplayBlocked) {
            autoplayBlocked = false;
            const autoplayMsg = document.getElementById('autoplay-warning');
            if (autoplayMsg) autoplayMsg.remove();
            console.log("User interacted. Autoplay should be enabled now.");
        }
    });

    const video = document.getElementById('webcam');
    const canvas = document.getElementById('overlay');
    
    if (video && canvas) {
        const ctx = canvas.getContext('2d');

        // Request Webcam access
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(e => {
                showFriendlyError("Could not access webcam. Please grant permissions.");
                console.error(e);
            });

        // Wait until video metadata loads to match canvas size
        video.addEventListener('loadedmetadata', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            processFrameLoop();
        });

        async function processFrameLoop() {
            // Draw current video frame to a temporary canvas
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = video.videoWidth;
            tempCanvas.height = video.videoHeight;
            tempCanvas.getContext('2d').drawImage(video, 0, 0);
            
            // Convert to Base64
            const base64Image = tempCanvas.toDataURL('image/jpeg', 0.7);

            try {
                const response = await fetch('/process_frame', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: base64Image })
                });
                const data = await response.json();
                
                // Clear previous boxes
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (data.faces) {
                    data.faces.forEach(face => {
                        const [x1, y1, x2, y2] = face.bbox;
                        const width = x2 - x1;
                        const height = y2 - y1;
                        
                        ctx.strokeStyle = `rgb(${face.color[0]}, ${face.color[1]}, ${face.color[2]})`;
                        ctx.lineWidth = 3;
                        ctx.strokeRect(x1, y1, width, height);
                        
                        ctx.fillStyle = `rgb(${face.color[0]}, ${face.color[1]}, ${face.color[2]})`;
                        ctx.fillRect(x1, y1 - 30, width, 30);
                        ctx.fillStyle = "#000";
                        ctx.font = "20px Arial";
                        ctx.fillText(face.name, x1 + 5, y1 - 8);
                    });
                }

                if (data.visitor) {
                    const now = Date.now();
                    if (data.visitor !== lastPlayedVisitor || (now - lastPlayedTime) > COOLDOWN_MS) {
                        lastPlayedVisitor = data.visitor;
                        lastPlayedTime = now;
                        playRandomAudio(data.visitor);
                    }
                }
            } catch (e) {
                console.error("Error processing frame", e);
            }

            setTimeout(processFrameLoop, 500);
        }
    }

    async function playRandomAudio(visitorName) {
        try {
            // Determine if we need a "known" or "unknown" audio file
            const visitorType = (visitorName === 'stranger') ? 'unknown' : 'known';
            
            // Ask the server to randomly select an audio file from the correct folder
            const response = await fetch(`/random_audio?type=${visitorType}`);
            if (!response.ok) {
                const errData = await response.json();
                showFriendlyError(errData.error || "Audio file error");
                console.error("Backend error:", errData.error);
                return;
            }
            
            const data = await response.json();
            console.log(`Detected person: ${visitorName}`);
            console.log(`Selected random audio: ${data.filename}`);
            
            const audio = new Audio(data.audio_url);
            
            try {
                await audio.play();
                console.log("Audio playback successfully triggered.");
            } catch (e) {
                console.error("Playback error:", e);
                if (e.name === 'NotAllowedError') {
                    autoplayBlocked = true;
                    showFriendlyError("Audio autoplay blocked by browser. Click anywhere on the page to enable audio.", true);
                } else {
                    showFriendlyError("Failed to play audio. Check console for details.");
                }
            }
        } catch (e) {
            console.error("Error setting up audio:", e);
        }
    }

    function showFriendlyError(message, persistent=false) {
        // Create a temporary flash message in the UI
        let flashesContainer = document.querySelector('.flashes');
        
        // If the container doesn't exist yet, create it and insert it at the top
        if (!flashesContainer) {
            flashesContainer = document.createElement('ul');
            flashesContainer.className = 'flashes';
            const mainContainer = document.querySelector('.container');
            if (mainContainer) {
                mainContainer.insertBefore(flashesContainer, mainContainer.firstChild);
            } else {
                document.body.appendChild(flashesContainer);
            }
        }
        
        // Check if a persistent warning already exists to avoid spamming
        if (persistent && document.getElementById('autoplay-warning')) {
            return;
        }
        
        const li = document.createElement('li');
        li.className = 'error';
        li.innerText = message;
        if (persistent) {
            li.id = 'autoplay-warning';
            li.style.cursor = 'pointer';
        }
        flashesContainer.appendChild(li);
        
        // Remove it after 5 seconds if not persistent
        if (!persistent) {
            setTimeout(() => {
                li.remove();
                if (flashesContainer.children.length === 0) {
                    flashesContainer.remove();
                }
            }, 5000);
        }
    }
});
