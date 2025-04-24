document.addEventListener('DOMContentLoaded', function() {
    const quizContainer = document.getElementById('quizContainer');
    const resultContainer = document.getElementById('resultContainer');
    const correctResult = document.getElementById('correctResult');
    const incorrectResult = document.getElementById('incorrectResult');
    const correctAnswerText = document.getElementById('correctAnswerText');
    const nextQuestionBtn = document.getElementById('nextQuestionBtn');
    const selectedAnswerInput = document.getElementById('selectedAnswer');
    const quizForm = document.getElementById('quizForm');
    const answerOptions = document.querySelectorAll('.answer-option');

    // Add playful background to quiz area
    if (quizContainer) {
        quizContainer.parentElement.parentElement.style.background = "#F6F8FF";
        quizContainer.parentElement.parentElement.style.borderRadius = "24px";
    }

    // Add click handler to each answer option
    answerOptions.forEach(option => {
        option.style.fontFamily = "'Anybody', 'Inter', Arial, sans-serif";
        option.style.fontWeight = "700";
        option.style.fontSize = "1.15rem";
        option.style.borderRadius = "14px";
        option.style.transition = "background 0.2s, color 0.2s, box-shadow 0.2s";
        option.style.boxShadow = "0 2px 8px rgba(166,111,255,0.06)";
        option.addEventListener('mouseenter', function() {
            this.style.background = "#A66FFF22";
        });
        option.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.background = "#fff";
            }
        });
        option.addEventListener('click', function(e) {
            // Remove active class from all options
            answerOptions.forEach(btn => {
                btn.classList.remove('active');
                btn.style.background = "#fff";
                btn.style.color = "#202020";
                btn.style.boxShadow = "0 2px 8px rgba(166,111,255,0.06)";
            });
            // Add active class to selected option
            this.classList.add('active');
            this.style.background = "#A66FFF";
            this.style.color = "#fff";
            this.style.boxShadow = "0 4px 16px rgba(166,111,255,0.18)";
            // Store selected answer in hidden input
            selectedAnswerInput.value = this.getAttribute('data-answer');
            // Submit form after a short delay
            setTimeout(() => {
                handleAnswer();
            }, 400);
        });
    });

    // Function to submit answer and handle result
    function handleAnswer() {
        const formData = new FormData(quizForm);
        const selectedAnswer = selectedAnswerInput.value;
        const correctAnswer = formData.get('correct_answer');

        // Disable all answer buttons and style them
        answerOptions.forEach(btn => {
            btn.disabled = true;
            btn.style.cursor = "not-allowed";
            btn.style.fontWeight = "700";
            btn.style.fontSize = "1.15rem";
            btn.style.borderRadius = "14px";
            // Highlight correct answer
            if (btn.getAttribute('data-answer') === correctAnswer) {
                btn.style.background = "#FF7B01";
                btn.style.color = "#fff";
                btn.style.boxShadow = "0 4px 16px rgba(255,123,1,0.18)";
                btn.classList.add('quiz-correct-animate');
            }
            // If this was selected but incorrect
            if (btn.getAttribute('data-answer') === selectedAnswer && selectedAnswer !== correctAnswer) {
                btn.style.background = "#F44336";
                btn.style.color = "#fff";
                btn.style.boxShadow = "0 4px 16px rgba(244,67,54,0.18)";
                btn.classList.add('quiz-wrong-animate');
            }
        });

        // Show result
        quizContainer.style.display = 'none';
        resultContainer.style.display = 'block';

        if (selectedAnswer === correctAnswer) {
            correctResult.style.display = 'block';
            correctResult.style.background = "#FFFBF2";
            correctResult.style.color = "#202020";
        } else {
            incorrectResult.style.display = 'block';
            incorrectResult.style.background = "#FFF2F2";
            incorrectResult.style.color = "#202020";
            correctAnswerText.textContent = correctAnswer;
        }

        // Submit form to update database
        fetch(quizForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            // Store next URL for button
            nextQuestionBtn.setAttribute('data-next-url', data.next_url);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Next question button handler
    if (nextQuestionBtn) {
        nextQuestionBtn.style.background = "#A66FFF";
        nextQuestionBtn.style.color = "#fff";
        nextQuestionBtn.style.fontFamily = "'Anybody', 'Inter', Arial, sans-serif";
        nextQuestionBtn.style.fontWeight = "700";
        nextQuestionBtn.style.fontSize = "1.1rem";
        nextQuestionBtn.style.borderRadius = "14px";
        nextQuestionBtn.style.border = "none";
        nextQuestionBtn.style.marginTop = "18px";
        nextQuestionBtn.style.boxShadow = "0 2px 8px rgba(166,111,255,0.10)";
        nextQuestionBtn.addEventListener('mouseenter', function() {
            this.style.background = "#FF7B01";
        });
        nextQuestionBtn.addEventListener('mouseleave', function() {
            this.style.background = "#A66FFF";
        });
        nextQuestionBtn.addEventListener('click', function() {
            window.location.href = this.getAttribute('data-next-url') || "/words/quiz/";
        });
    }

    // Update progress bar with yellow and playful width
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.background = "#FAE14C";
        progressBar.style.borderRadius = "8px";
        const randomProgress = Math.floor(Math.random() * 100) + 1;
        progressBar.style.width = randomProgress + '%';
        progressBar.setAttribute('aria-valuenow', randomProgress);
    }

    // Add keyframes for playful feedback
    const style = document.createElement('style');
    style.innerHTML = `
    @keyframes quiz-correct-pop {
        0% { transform: scale(1);}
        60% { transform: scale(1.15);}
        100% { transform: scale(1);}
    }
    @keyframes quiz-wrong-shake {
        0% { transform: translateX(0);}
        20% { transform: translateX(-6px);}
        40% { transform: translateX(6px);}
        60% { transform: translateX(-4px);}
        80% { transform: translateX(4px);}
        100% { transform: translateX(0);}
    }
    .quiz-correct-animate { animation: quiz-correct-pop 0.4s; }
    .quiz-wrong-animate { animation: quiz-wrong-shake 0.4s; }
    `;
    document.head.appendChild(style);
});
