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

    // Poll the server for the current visitor every 1 second
    setInterval(async () => {
        try {
            const response = await fetch('/get_visitor');
            const data = await response.json();
            const visitor = data.visitor;
            
            if (visitor) {
                const now = Date.now();
                // Play audio if it's a new visitor, or if the cooldown has expired
                if (visitor !== lastPlayedVisitor || (now - lastPlayedTime) > COOLDOWN_MS) {
                    lastPlayedVisitor = visitor;
                    lastPlayedTime = now;
                    playRandomAudio(visitor);
                }
            }
        } catch (e) {
            console.error("Error fetching visitor status:", e);
        }
    }, 1000);

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
