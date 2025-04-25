document.addEventListener('DOMContentLoaded', function() {
    const wordLookupForm = document.getElementById('wordLookupForm');
    const wordInput = document.querySelector('[name="word"]');
    const wordResult = document.getElementById('wordResult');
    const resultWord = document.getElementById('resultWord');
    const resultPartOfSpeech = document.getElementById('resultPartOfSpeech');
    const resultDefinition = document.getElementById('resultDefinition');
    const resultExamples = document.getElementById('resultExamples');
    const saveWordBtn = document.getElementById('saveWordBtn');
    const heartIcon = saveWordBtn.querySelector('.heart-icon');
    const playAudioBtn = document.getElementById('playAudioBtn');
    const volumeIcon = playAudioBtn.querySelector(".bi-volume-up");
    const wordAudio = document.getElementById('wordAudio');
    const lookupSpinner = document.getElementById('lookupSpinner');
    
    let currentWordId = null;
    let isWordSaved = false;
    
    // Initialize the heart icon with outlined class
    heartIcon.classList.add('outlined');
    volumeIcon.classList.remove('outlined');
    volumeIcon.classList.add('filled');
    
    let isPlaying = false;

    function showVolumeIcon() {
        volumeIcon.innerHTML = `
            <path transform="translate(2,0)" d="M11.536 14.01A8.47 8.47 0 0 0 14.026 8a8.47 8.47 0 0 0-2.49-6.01l-.708.707A7.48 7.48 0 0 1 13.025 8c0 2.071-.84 3.946-2.197 5.303z"/>
            <path transform="translate(1,0)" d="M10.121 12.596A6.48 6.48 0 0 0 12.025 8a6.48 6.48 0 0 0-1.904-4.596l-.707.707A5.48 5.48 0 0 1 11.025 8a5.48 5.48 0 0 1-1.61 3.89z"/>
            <path d="M10.025 8a4.5 4.5 0 0 1-1.318 3.182L8 10.475A3.5 3.5 0 0 0 9.025 8c0-.966-.392-1.841-1.025-2.475l.707-.707A4.5 4.5 0 0 1 10.025 8"/>
            <path d="M7 4a.5.5 0 0 0-.812-.39L3.825 5.5H1.5A.5.5 0 0 0 1 6v4a.5.5 0 0 0 .5.5h2.325l2.363 1.89A.5.5 0 0 0 7 12z"/>
            <path d="M4.312 6.39 6 5.04v5.92L4.312 9.61A.5.5 0 0 0 4 9.5H2v-3h2a.5.5 0 0 0 .312-.11"/>
        `;
        volumeIcon.classList.remove('filled');
        volumeIcon.classList.add('outlined');
    }
    
    function showSquareIcon() {
        volumeIcon.innerHTML = `
            <rect x="4" y="4" width="9" height="9" rx="2" ry="2"></rect>
        `;
        volumeIcon.classList.remove('outlined');
        volumeIcon.classList.add('filled');
    }
    
    playAudioBtn.addEventListener('click', () => {
        if (!wordAudio.src) return;
    
        if (isPlaying) {
            wordAudio.pause();
            wordAudio.currentTime = 0;
            isPlaying = false;
            showVolumeIcon();
        } else {
            wordAudio.play().catch(err => {
                console.error('Audio playback failed:', err);
            });
        }
    });
    
    // Audio state listeners
    wordAudio.addEventListener('play', () => {
        isPlaying = true;
        showSquareIcon();
    });
    
    wordAudio.addEventListener('ended', () => {
        isPlaying = false;
        showVolumeIcon();
    });
    
    wordAudio.addEventListener('pause', () => {
        if (!wordAudio.ended) {
            isPlaying = false;
            showVolumeIcon();
        }
    });

    // Set the button state based on whether the word is saved
    function updateSaveButtonState(isSaved) {
        isWordSaved = isSaved;
        
        if (isSaved) {
            saveWordBtn.classList.remove('btn-outline-danger');
            saveWordBtn.classList.add('btn-danger');
            saveWordBtn.title = 'Удалить из коллекции';
        } else {
            saveWordBtn.classList.remove('btn-danger');
            saveWordBtn.classList.add('btn-outline-danger');
            saveWordBtn.title = 'Сохранить в мою коллекцию';
        }
        
        saveWordBtn.disabled = false;
    }
    
    wordLookupForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Show spinner, hide result
        if (lookupSpinner) lookupSpinner.style.display = 'flex';
        if (wordResult) wordResult.style.display = 'none';

        const formData = new FormData(wordLookupForm);
        const lookupUrl = wordLookupForm.dataset.lookupUrl;

        fetch(lookupUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
            const contentType = response.headers.get('content-type');
            if (response.ok && contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                return response.text().then(text => {
                    throw new Error('Server returned non-JSON response: ' + text);
                });
            }
        })
        .then(data => {
            if (!data) return; // Handle redirect case

            // Hide spinner
            if (lookupSpinner) lookupSpinner.style.display = 'none';

            if (data.error) {
                alert(data.error);
                return;
            }
            
            resultWord.textContent = data.word;
            resultPartOfSpeech.textContent = data.part_of_speech || '';
            resultDefinition.textContent = data.definition;
            resultExamples.innerHTML = '';
            if (data.examples && data.examples.length > 0) {
                data.examples.forEach(example => {
                    const li = document.createElement('li');
                    li.textContent = example;
                    resultExamples.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'Примеры не найдены';
                resultExamples.appendChild(li);
            }
            currentWordId = data.id;
            wordResult.style.display = 'block';
            updateSaveButtonState(data.is_saved || false);
            wordInput.value = '';
            if (data.audio_file_url) {
                wordAudio.src = data.audio_file_url;
                playAudioBtn.disabled = false;
            } else {
                wordAudio.removeAttribute('src');
                playAudioBtn.disabled = true;
            }
        })
        .catch(error => {
            if (lookupSpinner) lookupSpinner.style.display = 'none';
            console.error('Error:', error);
            alert('Произошла ошибка при поиске слова.');
        });
    });
    
    // Use touchend for mobile devices to prevent hover state issues
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    const clickEvent = isTouchDevice ? 'touchend' : 'click';
    
    saveWordBtn.addEventListener(clickEvent, function(e) {
        if (isTouchDevice) {
            e.preventDefault(); // Prevent default touch behavior
        }
        
        if (!currentWordId) return;
        
        // Check if user is authenticated
        if (saveWordBtn.dataset.isAuthenticated === "true") {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const formData = new FormData();
            formData.append('word_id', currentWordId);
            
            // Disable button right away to prevent double-clicks
            saveWordBtn.disabled = true;
            
            // Choose endpoint based on current state
            const endpoint = isWordSaved ? 
                saveWordBtn.dataset.removeUrl : 
                saveWordBtn.dataset.saveUrl;
            
            fetch(endpoint, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return; // Handle redirect case
                
                if (data.success) {
                    // Toggle the saved state
                    updateSaveButtonState(!isWordSaved);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Re-enable the button if there's an error
                saveWordBtn.disabled = false;
            });
        } else {
            // Redirect directly to login page instead of showing modal
            window.location.href = saveWordBtn.dataset.loginUrl;
        }
    });
    
    // Reset button state when clicked on mobile
    if (isTouchDevice) {
        saveWordBtn.addEventListener('touchstart', function(e) {
            e.preventDefault();
            // Add a visual feedback class that will be removed on touchend
            this.classList.add('touch-active');
        });
        
        saveWordBtn.addEventListener('touchcancel', function() {
            this.classList.remove('touch-active');
        });
    }
});
