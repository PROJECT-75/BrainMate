// QUIZDOM - The Ultimate Knowledge Challenge Platform
// Advanced Quiz Application with Modern UI/UX

class QuizDom {
    constructor() {
        this.currentScreen = 'main-menu';
        this.selectedCategory = null;
        this.selectedDifficulty = null;
        this.currentQuestionIndex = 0;
        this.questions = [];
        this.score = 0;
        this.correctAnswers = 0;
        this.timeRemaining = 30;
        this.timerInterval = null;
        this.quizStartTime = null;
        this.settings = {
            soundEnabled: true,
            timerDuration: 30,
            questionsPerQuiz: 10
        };
        this.leaderboard = [];
        this.sessionToken = null;
        this.currentQuestionData = null;
        
        this.initializeApp();
    }

    initializeApp() {
        this.loadSettings();
        this.loadCategories();
        this.bindEvents();
        this.loadLeaderboard();
        console.log('🎯 QUIZDOM initialized successfully!');
    }

    // Screen Management
    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
            screen.style.display = 'none';
        });

        // Show selected screen
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.style.display = 'block';
            targetScreen.classList.add('active');
            targetScreen.classList.add('fade-in');
            this.currentScreen = screenId;

            // Handle screen-specific logic
            this.handleScreenChange(screenId);
        }
    }

    handleScreenChange(screenId) {
        switch(screenId) {
            case 'category-selection':
                this.loadCategories();
                break;
            case 'leaderboard':
                this.displayLeaderboard();
                break;
            case 'settings':
                this.loadSettingsUI();
                break;
            case 'game-screen':
                this.initializeQuiz();
                break;
        }
    }

    // Categories Management
    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            if (response.ok) {
                const data = await response.json();
                this.renderCategories(data.categories);
                return;
            }
        } catch (error) {
            console.error('Error loading categories from API:', error);
        }
        
        // Fallback to static categories
        const categories = [
            {
                id: 'science',
                name: 'Science & Nature',
                icon: 'fas fa-microscope',
                description: 'Explore the wonders of physics, chemistry, biology, and natural phenomena'
            },
            {
                id: 'history',
                name: 'History',
                icon: 'fas fa-landmark',
                description: 'Journey through time from ancient civilizations to modern events'
            },
            {
                id: 'technology',
                name: 'Technology',
                icon: 'fas fa-microchip',
                description: 'Test your knowledge of computers, programming, and digital innovation'
            },
            {
                id: 'sports',
                name: 'Sports',
                icon: 'fas fa-trophy',
                description: 'From Olympics to world championships, challenge your sports knowledge'
            },
            {
                id: 'arts',
                name: 'Arts & Literature',
                icon: 'fas fa-palette',
                description: 'Dive into the world of literature, painting, music, and creative arts'
            },
            {
                id: 'geography',
                name: 'Geography',
                icon: 'fas fa-globe-americas',
                description: 'Explore countries, capitals, landmarks, and geographical features'
            },
            {
                id: 'entertainment',
                name: 'Entertainment',
                icon: 'fas fa-film',
                description: 'Movies, TV shows, celebrities, and pop culture trivia'
            },
            {
                id: 'general',
                name: 'General Knowledge',
                icon: 'fas fa-brain',
                description: 'Mixed topics covering a wide range of interesting facts and trivia'
            }
        ];

        this.renderCategories(categories);
    }

    renderCategories(categories) {
        const categoriesGrid = document.getElementById('categories-grid');
        if (categoriesGrid) {
            categoriesGrid.innerHTML = categories.map(category => `
                <div class="category-card" onclick="selectCategory('${category.name || category.id}', '${category.display_name || category.name}')">
                    <div class="category-icon">
                        <i class="${category.icon}"></i>
                    </div>
                    <div class="category-name">${category.display_name || category.name}</div>
                    <div class="category-description">${category.description}</div>
                </div>
            `).join('');
        }
    }

    getCategoryIdByName(categoryName) {
        // Map category names to IDs for the API
        const categoryMap = {
            'science': 1,
            'history': 2,
            'technology': 3,
            'sports': 4,
            'arts': 5,
            'geography': 6,
            'entertainment': 7,
            'general': 8
        };
        return categoryMap[categoryName] || 1;
    }

    selectCategory(categoryId, categoryName) {
        this.selectedCategory = { id: categoryId, name: categoryName };
        this.playSound('select');
        this.showScreen('difficulty-selection');
    }

    selectDifficulty(difficulty) {
        // Remove previous selection
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.classList.remove('selected');
        });

        // Add selection to clicked button
        event.target.classList.add('selected');
        this.selectedDifficulty = difficulty;
        
        // Show start quiz button
        document.getElementById('start-quiz-btn').style.display = 'inline-block';
        this.playSound('select');
    }

    // Quiz Logic
    async startQuiz() {
        if (!this.selectedCategory || !this.selectedDifficulty) {
            this.showNotification('Please select a category and difficulty level.', 'warning');
            return;
        }

        this.showScreen('game-screen');
        this.score = 0;
        this.correctAnswers = 0;
        this.currentQuestionIndex = 0;
        this.quizStartTime = Date.now();
        
        await this.loadQuestions();
        this.displayQuestion();
        this.startTimer();
        this.playSound('start');
    }

    async loadQuestions() {
        try {
            // Start a quiz session with the backend
            const response = await fetch('/api/quiz/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    category_id: this.getCategoryIdByName(this.selectedCategory.id),
                    difficulty: this.selectedDifficulty,
                    questions_count: this.settings.questionsPerQuiz
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.sessionToken = data.session_token;
                this.questions = []; // Will be loaded one by one
                await this.loadCurrentQuestion();
            } else {
                throw new Error('Failed to start quiz session');
            }
        } catch (error) {
            console.error('Error loading questions:', error);
            // Fallback to sample questions
            this.questions = await this.generateSampleQuestions();
        }
    }

    async generateSampleQuestions() {
        const questionTemplates = {
            science: [
                {
                    question: "What is the chemical symbol for gold?",
                    options: ["Au", "Ag", "Fe", "Cu"],
                    correct: 0,
                    difficulty: "easy"
                },
                {
                    question: "Which planet is closest to the Sun?",
                    options: ["Venus", "Earth", "Mercury", "Mars"],
                    correct: 2,
                    difficulty: "easy"
                },
                {
                    question: "What is the speed of light in vacuum?",
                    options: ["299,792,458 m/s", "300,000,000 m/s", "299,792,458 km/s", "186,000 miles/s"],
                    correct: 0,
                    difficulty: "hard"
                }
            ],
            history: [
                {
                    question: "In which year did World War II end?",
                    options: ["1944", "1945", "1946", "1947"],
                    correct: 1,
                    difficulty: "easy"
                },
                {
                    question: "Who was the first President of the United States?",
                    options: ["Thomas Jefferson", "John Adams", "George Washington", "Benjamin Franklin"],
                    correct: 2,
                    difficulty: "easy"
                }
            ],
            technology: [
                {
                    question: "What does CPU stand for?",
                    options: ["Central Processing Unit", "Computer Processing Unit", "Central Program Unit", "Computer Program Unit"],
                    correct: 0,
                    difficulty: "easy"
                },
                {
                    question: "Which programming language is known as the 'language of the web'?",
                    options: ["Python", "Java", "JavaScript", "C++"],
                    correct: 2,
                    difficulty: "medium"
                }
            ]
        };

        const categoryQuestions = questionTemplates[this.selectedCategory.id] || questionTemplates.science;
        const filteredQuestions = categoryQuestions.filter(q => q.difficulty === this.selectedDifficulty);
        
        // If not enough questions for selected difficulty, mix with other difficulties
        if (filteredQuestions.length < this.settings.questionsPerQuiz) {
            return [...filteredQuestions, ...categoryQuestions].slice(0, this.settings.questionsPerQuiz);
        }
        
        return filteredQuestions.slice(0, this.settings.questionsPerQuiz);
    }

    async loadCurrentQuestion() {
        if (!this.sessionToken) {
            console.error('No session token available');
            return;
        }

        try {
            const response = await fetch(`/api/quiz/${this.sessionToken}/question`);
            if (response.ok) {
                const data = await response.json();
                this.currentQuestionData = data;
                this.displayBackendQuestion();
            } else {
                throw new Error('Failed to load question');
            }
        } catch (error) {
            console.error('Error loading current question:', error);
            this.showNotification('Error loading question', 'error');
        }
    }

    displayQuestion() {
        if (this.currentQuestionIndex >= this.questions.length) {
            this.endQuiz();
            return;
        }

        const question = this.questions[this.currentQuestionIndex];
        const questionNumber = document.getElementById('question-number');
        const questionText = document.getElementById('question-text');
        const answersGrid = document.getElementById('answers-grid');
        const progressFill = document.getElementById('progress-fill');

        // Update question info
        questionNumber.textContent = `Question ${this.currentQuestionIndex + 1} of ${this.questions.length}`;
        questionText.textContent = question.question;

        // Update progress bar
        const progress = ((this.currentQuestionIndex + 1) / this.questions.length) * 100;
        progressFill.style.width = `${progress}%`;

        // Create answer buttons
        answersGrid.innerHTML = question.options.map((option, index) => `
            <button class="answer-btn" onclick="quizDom.selectAnswer(${index})" data-index="${index}">
                <strong>${String.fromCharCode(65 + index)}.</strong> ${option}
            </button>
        `).join('');

        // Reset timer
        this.timeRemaining = this.settings.timerDuration;
        this.updateTimerDisplay();
        
        // Hide next question button
        document.getElementById('next-question-btn').style.display = 'none';
    }

    displayBackendQuestion() {
        if (!this.currentQuestionData) return;

        const questionNumber = document.getElementById('question-number');
        const questionText = document.getElementById('question-text');
        const answersGrid = document.getElementById('answers-grid');
        const progressFill = document.getElementById('progress-fill');

        // Update question info
        questionNumber.textContent = `Question ${this.currentQuestionData.question_number} of ${this.currentQuestionData.total_questions}`;
        questionText.textContent = this.currentQuestionData.question.question;

        // Update progress bar
        const progress = (this.currentQuestionData.question_number / this.currentQuestionData.total_questions) * 100;
        progressFill.style.width = `${progress}%`;

        // Create answer buttons
        answersGrid.innerHTML = this.currentQuestionData.question.options.map((option, index) => `
            <button class="answer-btn" onclick="quizDom.selectBackendAnswer(${index})" data-index="${index}">
                <strong>${String.fromCharCode(65 + index)}.</strong> ${option}
            </button>
        `).join('');

        // Update score display
        this.score = this.currentQuestionData.current_score;
        this.updateScoreDisplay();

        // Reset timer
        this.timeRemaining = this.settings.timerDuration;
        this.updateTimerDisplay();
        
        // Hide next question button
        document.getElementById('next-question-btn').style.display = 'none';
    }

    selectAnswer(selectedIndex) {
        const question = this.questions[this.currentQuestionIndex];
        const answerButtons = document.querySelectorAll('.answer-btn');
        const isCorrect = selectedIndex === question.correct;

        // Disable all buttons
        answerButtons.forEach(btn => btn.classList.add('disabled'));

        // Show correct/incorrect styling
        answerButtons[selectedIndex].classList.add(isCorrect ? 'correct' : 'incorrect');
        if (!isCorrect) {
            answerButtons[question.correct].classList.add('correct');
        }

        // Update score
        if (isCorrect) {
            this.correctAnswers++;
            const points = this.getPointsForDifficulty();
            this.score += points;
            this.updateScoreDisplay();
            this.playSound('correct');
            this.showNotification(`Correct! +${points} points`, 'success');
        } else {
            this.playSound('incorrect');
            this.showNotification('Incorrect answer', 'error');
        }

        // Stop timer
        this.stopTimer();

        // Show next question button
        document.getElementById('next-question-btn').style.display = 'inline-block';
    }

    async selectBackendAnswer(selectedIndex) {
        if (!this.sessionToken) {
            console.error('No session token available');
            return;
        }

        const answerButtons = document.querySelectorAll('.answer-btn');
        
        // Disable all buttons immediately
        answerButtons.forEach(btn => btn.classList.add('disabled'));

        try {
            const response = await fetch(`/api/quiz/${this.sessionToken}/answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    answer: selectedIndex,
                    player_name: this.getPlayerName()
                })
            });

            if (response.ok) {
                const data = await response.json();
                
                // Show correct/incorrect styling
                answerButtons[selectedIndex].classList.add(data.is_correct ? 'correct' : 'incorrect');
                if (!data.is_correct) {
                    answerButtons[data.correct_answer].classList.add('correct');
                }

                // Update score and stats
                if (data.is_correct) {
                    this.correctAnswers++;
                    this.playSound('correct');
                    this.showNotification(`Correct! +${data.points_earned} points`, 'success');
                } else {
                    this.playSound('incorrect');
                    this.showNotification('Incorrect answer', 'error');
                }

                this.score = data.current_score;
                this.updateScoreDisplay();

                // Stop timer
                this.stopTimer();

                // Check if quiz is completed
                if (data.quiz_completed) {
                    setTimeout(() => {
                        this.showFinalResults(data.final_stats);
                    }, 2000);
                } else {
                    // Show next question button
                    document.getElementById('next-question-btn').style.display = 'inline-block';
                }

            } else {
                throw new Error('Failed to submit answer');
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
            this.showNotification('Error submitting answer', 'error');
            // Re-enable buttons on error
            answerButtons.forEach(btn => btn.classList.remove('disabled'));
        }
    }

    async nextQuestion() {
        if (this.sessionToken) {
            // Backend mode: load next question from API
            await this.loadCurrentQuestion();
            this.startTimer();
        } else {
            // Fallback mode: use local questions
            this.currentQuestionIndex++;
            this.displayQuestion();
            this.startTimer();
        }
    }

    showFinalResults(stats) {
        // Update results screen with backend data
        document.getElementById('final-score').textContent = stats.total_score;
        document.getElementById('correct-answers').textContent = stats.correct_answers;
        document.getElementById('accuracy').textContent = `${stats.accuracy}%`;
        document.getElementById('time-taken').textContent = `${stats.time_taken}s`;
        
        // Performance message
        const performanceMessage = this.getPerformanceMessage(stats.accuracy);
        document.getElementById('performance-message').textContent = performanceMessage;

        this.showScreen('results-screen');
        this.playSound('finish');
    }

    getPointsForDifficulty() {
        const pointsMap = {
            'easy': 5,
            'medium': 10,
            'hard': 15
        };
        return pointsMap[this.selectedDifficulty] || 5;
    }

    // Timer Management
    startTimer() {
        this.stopTimer(); // Clear any existing timer
        this.timeRemaining = this.settings.timerDuration;
        
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();

            if (this.timeRemaining <= 10) {
                document.getElementById('timer').parentElement.classList.add('warning');
            }

            if (this.timeRemaining <= 0) {
                this.timeUp();
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        document.getElementById('timer').parentElement.classList.remove('warning');
    }

    updateTimerDisplay() {
        document.getElementById('timer').textContent = this.timeRemaining;
    }

    timeUp() {
        this.stopTimer();
        this.showNotification('Time\'s up!', 'warning');
        
        // Auto-select a random answer or show correct answer
        const question = this.questions[this.currentQuestionIndex];
        const answerButtons = document.querySelectorAll('.answer-btn');
        
        answerButtons.forEach(btn => btn.classList.add('disabled'));
        answerButtons[question.correct].classList.add('correct');
        
        document.getElementById('next-question-btn').style.display = 'inline-block';
        this.playSound('timeup');
    }

    updateScoreDisplay() {
        document.getElementById('current-score').textContent = this.score;
    }

    // Quiz End
    endQuiz() {
        this.stopTimer();
        const totalTime = Math.floor((Date.now() - this.quizStartTime) / 1000);
        const accuracy = Math.round((this.correctAnswers / this.questions.length) * 100);
        
        // Update results screen
        document.getElementById('final-score').textContent = this.score;
        document.getElementById('correct-answers').textContent = this.correctAnswers;
        document.getElementById('accuracy').textContent = `${accuracy}%`;
        document.getElementById('time-taken').textContent = `${totalTime}s`;
        
        // Performance message
        const performanceMessage = this.getPerformanceMessage(accuracy);
        document.getElementById('performance-message').textContent = performanceMessage;

        // Save to leaderboard
        this.saveToLeaderboard({
            score: this.score,
            category: this.selectedCategory.name,
            difficulty: this.selectedDifficulty,
            accuracy: accuracy,
            time: totalTime,
            date: new Date().toLocaleDateString()
        });

        this.showScreen('results-screen');
        this.playSound('finish');
    }

    getPerformanceMessage(accuracy) {
        if (accuracy >= 90) return "🎉 Outstanding! You're a true quiz master!";
        if (accuracy >= 80) return "🌟 Excellent performance! Well done!";
        if (accuracy >= 70) return "👍 Good job! Keep up the great work!";
        if (accuracy >= 60) return "👌 Not bad! Room for improvement!";
        return "💪 Keep practicing! You'll get better!";
    }

    restartQuiz() {
        this.showScreen('category-selection');
    }

    // Leaderboard Management
    saveToLeaderboard(result) {
        this.leaderboard.push({
            ...result,
            id: Date.now(),
            playerName: this.getPlayerName()
        });
        
        // Sort by score (descending)
        this.leaderboard.sort((a, b) => b.score - a.score);
        
        // Keep only top 50 results
        this.leaderboard = this.leaderboard.slice(0, 50);
        
        // Save to localStorage
        localStorage.setItem('quizdom_leaderboard', JSON.stringify(this.leaderboard));
    }

    async loadLeaderboard() {
        try {
            const response = await fetch('/api/leaderboard?limit=50');
            if (response.ok) {
                const data = await response.json();
                this.leaderboard = data.leaderboard;
                return;
            }
        } catch (error) {
            console.error('Error loading leaderboard from API:', error);
        }
        
        // Fallback to localStorage
        const saved = localStorage.getItem('quizdom_leaderboard');
        if (saved) {
            this.leaderboard = JSON.parse(saved);
        }
    }

    displayLeaderboard() {
        const content = document.getElementById('leaderboard-content');
        
        if (this.leaderboard.length === 0) {
            content.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--next-gen-color-secondary);">
                    <i class="fas fa-trophy" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>No scores yet. Be the first to make it to the leaderboard!</p>
                </div>
            `;
            return;
        }

        content.innerHTML = `
            <div style="max-width: 800px; margin: 0 auto;">
                ${this.leaderboard.slice(0, 10).map((entry, index) => `
                    <div class="glass-panel" style="margin: 1rem 0; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: ${this.getRankColor(index)}; min-width: 3rem;">
                                ${index < 3 ? ['🥇', '🥈', '🥉'][index] : `#${index + 1}`}
                            </div>
                            <div>
                                <div style="font-weight: 600; font-size: 1.1rem;">${entry.playerName}</div>
                                <div style="color: var(--next-gen-color-secondary); font-size: 0.9rem;">
                                    ${entry.category} • ${entry.difficulty} • ${entry.accuracy}% • ${entry.date}
                                </div>
                            </div>
                        </div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: var(--next-gen-accent);">
                            ${entry.score}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getRankColor(index) {
        const colors = ['#ffd700', '#c0c0c0', '#cd7f32'];
        return colors[index] || 'var(--next-gen-accent)';
    }

    getPlayerName() {
        let name = localStorage.getItem('quizdom_player_name');
        if (!name) {
            name = prompt('Enter your name for the leaderboard:') || 'Anonymous';
            localStorage.setItem('quizdom_player_name', name);
        }
        return name;
    }

    // Settings Management
    loadSettings() {
        const saved = localStorage.getItem('quizdom_settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
    }

    saveSettings() {
        const soundEnabled = document.getElementById('sound-toggle').checked;
        const timerDuration = parseInt(document.getElementById('timer-range').value);
        const questionsPerQuiz = parseInt(document.getElementById('questions-count').value);

        this.settings = {
            soundEnabled,
            timerDuration,
            questionsPerQuiz
        };

        localStorage.setItem('quizdom_settings', JSON.stringify(this.settings));
        this.showNotification('Settings saved successfully!', 'success');
    }

    loadSettingsUI() {
        document.getElementById('sound-toggle').checked = this.settings.soundEnabled;
        document.getElementById('timer-range').value = this.settings.timerDuration;
        document.getElementById('questions-count').value = this.settings.questionsPerQuiz;
        document.getElementById('timer-value').textContent = this.settings.timerDuration;
    }

    bindEvents() {
        // Timer range slider
        const timerRange = document.getElementById('timer-range');
        if (timerRange) {
            timerRange.addEventListener('input', (e) => {
                document.getElementById('timer-value').textContent = e.target.value;
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (this.currentScreen === 'game-screen' && !document.querySelector('.answer-btn.disabled')) {
                const key = e.key.toLowerCase();
                if (['a', 'b', 'c', 'd'].includes(key)) {
                    const index = key.charCodeAt(0) - 97; // Convert a-d to 0-3
                    const answerButtons = document.querySelectorAll('.answer-btn');
                    if (answerButtons[index]) {
                        this.selectAnswer(index);
                    }
                }
            }
        });
    }

    // Utility Functions
    playSound(type) {
        if (!this.settings.soundEnabled) return;
        
        // Create audio context for sound effects
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Different sounds for different actions
        const frequencies = {
            select: 800,
            correct: 1000,
            incorrect: 300,
            start: 600,
            finish: 1200,
            timeup: 400
        };
        
        oscillator.frequency.setValueAtTime(frequencies[type] || 500, audioContext.currentTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 2rem;
            background: var(--next-gen-glass-bg);
            border: 1px solid var(--next-gen-border);
            border-radius: 10px;
            color: var(--next-gen-color-primary);
            font-weight: 600;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        `;

        // Type-specific styling
        const colors = {
            success: 'var(--next-gen-success-color)',
            error: 'var(--next-gen-error-color)',
            warning: 'var(--next-gen-warning-color)',
            info: 'var(--next-gen-accent)'
        };
        
        notification.style.borderLeftColor = colors[type];
        notification.style.borderLeftWidth = '4px';
        notification.textContent = message;

        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease-out forwards';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    shareScore() {
        const text = `🎯 I just scored ${this.score} points on QUIZDOM! Can you beat my score? Try it now!`;
        
        if (navigator.share) {
            navigator.share({
                title: 'QUIZDOM Score',
                text: text,
                url: window.location.href
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Score copied to clipboard!', 'success');
            });
        }
    }
}

// Global functions for HTML onclick events
let quizDom;

function showScreen(screenId) {
    quizDom.showScreen(screenId);
}

function selectCategory(categoryId, categoryName) {
    quizDom.selectCategory(categoryId, categoryName);
}

function selectDifficulty(difficulty) {
    quizDom.selectDifficulty(difficulty);
}

function startQuiz() {
    quizDom.startQuiz();
}

function nextQuestion() {
    quizDom.nextQuestion();
}

function endQuiz() {
    if (confirm('Are you sure you want to end the quiz?')) {
        quizDom.endQuiz();
    }
}

function restartQuiz() {
    quizDom.restartQuiz();
}

function saveSettings() {
    quizDom.saveSettings();
}

function shareScore() {
    quizDom.shareScore();
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    quizDom = new QuizDom();
    console.log('🚀 QUIZDOM application started!');
});

// Additional CSS animations for notifications
const additionalCSS = `
@keyframes slideIn {
    0% { transform: translateX(100%); opacity: 0; }
    100% { transform: translateX(0); opacity: 1; }
}

@keyframes fadeOut {
    0% { opacity: 1; }
    100% { opacity: 0; }
}
`;

// Inject additional CSS
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);