document.addEventListener('DOMContentLoaded', function() {
    const expandAllBtn = document.getElementById('expandAllBtn');
    const collapseAllBtn = document.getElementById('collapseAllBtn');
    const wordsCount = document.getElementById('words-count');
    const noWordsMessage = document.getElementById('no-words-message');
    const wordsAccordion = document.getElementById('wordsAccordion');
    
    // Handle accordion expand/collapse
    if (expandAllBtn && collapseAllBtn) {
        expandAllBtn.addEventListener('click', function() {
            document.querySelectorAll('.accordion-collapse').forEach(item => {
                item.classList.add('show');
                const button = document.querySelector(`[data-bs-target="#${item.id}"]`);
                if (button) button.classList.remove('collapsed');
            });
        });
        
        collapseAllBtn.addEventListener('click', function() {
            document.querySelectorAll('.accordion-collapse').forEach(item => {
                item.classList.remove('show');
                const button = document.querySelector(`[data-bs-target="#${item.id}"]`);
                if (button) button.classList.add('collapsed');
            });
        });
    }
    
    // Handle word removal
    document.querySelectorAll('.remove-word-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (!confirm('Вы уверены, что хотите удалить это слово из коллекции?')) {
                return;
            }
            
            const wordId = this.getAttribute('data-word-id');
            const userWordId = this.getAttribute('data-user-word-id');
            const card = document.getElementById(`word-card-${userWordId}`);
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const formData = new FormData();
            formData.append('word_id', wordId);
            
            fetch('/words/remove/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.removed) {
                    // Remove the card
                    card.remove();
                    
                    // Update the count
                    const currentCount = parseInt(wordsCount.textContent) - 1;
                    wordsCount.textContent = currentCount;
                    
                    // Show no words message if there are no more words
                    if (currentCount === 0 && noWordsMessage) {
                        wordsAccordion.style.display = 'none';
                        document.querySelector('.d-flex.justify-content-between.mb-3').style.display = 'none';
                        noWordsMessage.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при удалении слова.');
            });
        });
    });
});
