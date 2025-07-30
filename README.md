# 🎯 QUIZDOM - The Ultimate Knowledge Challenge Platform

**Master Every Subject, Conquer Every Challenge**

QUIZDOM is an advanced quiz platform that transforms learning into an engaging competitive experience. Built with cutting-edge web technologies, it offers a seamless interface for knowledge testing across multiple domains with real-time scoring and global leaderboards.

![QUIZDOM Logo](https://img.shields.io/badge/QUIZDOM-v1.0.0-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)

## ✨ Features

### 🧠 **10+ Knowledge Categories**
- **Science & Nature** - Physics, Chemistry, Biology, Natural Phenomena
- **History** - Ancient Civilizations to Modern Events
- **Technology** - Programming, Computing, Digital Innovation
- **Sports** - Olympics, Championships, Athletic Knowledge
- **Arts & Literature** - Painting, Music, Literary Works
- **Geography** - Countries, Capitals, Landmarks
- **Entertainment** - Movies, TV Shows, Pop Culture
- **General Knowledge** - Mixed Topics and Trivia

### ⚡ **Three Difficulty Levels**
- **Beginner (5 points)** - Entry-level questions
- **Intermediate (10 points)** - Moderate challenge
- **Expert (15 points)** - Advanced knowledge required

### 📊 **Advanced Features**
- **Real-time Scoring** - Dynamic point calculation
- **Adaptive Timer** - Configurable time limits (15-60 seconds)
- **Progress Tracking** - Visual progress indicators
- **Global Leaderboards** - Compete with players worldwide
- **Performance Analytics** - Detailed statistics and insights
- **Sound Effects** - Audio feedback for interactions
- **Keyboard Shortcuts** - A, B, C, D keys for quick answers

### 🎨 **Modern UI/UX**
- **Glassmorphism Design** - Contemporary visual aesthetics
- **Smooth Animations** - Fluid transitions and effects
- **Fully Responsive** - Perfect experience across all devices
- **Dark Theme** - Eye-friendly color scheme
- **Customizable Settings** - Personalize your experience

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd quizdom
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database**
   ```bash
   python app.py
   ```
   The database will be automatically created with sample questions.

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Open Your Browser**
   Navigate to `http://localhost:5000`

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Lightweight database
- **JWT** - Authentication tokens
- **CORS** - Cross-origin resource sharing

### Frontend
- **HTML5** - Modern markup
- **CSS3** - Advanced styling with custom properties
- **JavaScript ES6+** - Modern JavaScript features
- **Font Awesome** - Icon library
- **Google Fonts** - Typography

### Features
- **RESTful API** - Clean, organized endpoints
- **Session Management** - Secure quiz sessions
- **Real-time Updates** - Live scoring and progress
- **Error Handling** - Graceful error management
- **Responsive Design** - Mobile-first approach

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

### Quiz Endpoints
- `GET /api/categories` - Get all categories
- `POST /api/quiz/start` - Start new quiz session
- `GET /api/quiz/{token}/question` - Get current question
- `POST /api/quiz/{token}/answer` - Submit answer
- `GET /api/quiz/{token}/status` - Get quiz status

### Leaderboard Endpoints
- `GET /api/leaderboard` - Get leaderboard entries
- `GET /api/leaderboard/top` - Get top scores

### Statistics Endpoints
- `GET /api/stats/general` - General app statistics
- `GET /api/health` - Health check

### Admin Endpoints
- `POST /api/admin/questions` - Add new questions

## 🎮 How to Play

1. **Choose Category** - Select from 8+ knowledge domains
2. **Select Difficulty** - Pick your challenge level
3. **Configure Settings** - Adjust timer and question count
4. **Start Quiz** - Begin your knowledge challenge
5. **Answer Questions** - Use mouse clicks or A/B/C/D keys
6. **Track Progress** - Monitor score and time remaining
7. **View Results** - See detailed performance statistics
8. **Compete Globally** - Check your ranking on leaderboards

## ⚙️ Configuration

### Environment Variables
```bash
PORT=5000                    # Server port
DEBUG=True                   # Debug mode
SECRET_KEY=your-secret-key   # JWT secret key
```

### Application Settings
- **Timer Duration**: 15-60 seconds per question
- **Questions Per Quiz**: 5, 10, 15, or 20 questions
- **Sound Effects**: Enable/disable audio feedback
- **Categories**: Select specific knowledge domains

## 🗄️ Database Schema

### Tables
- **Users** - Player accounts and statistics
- **Categories** - Quiz categories and metadata
- **Questions** - Quiz questions with multiple choice options
- **QuizSessions** - Individual game sessions
- **Leaderboard** - High score entries

### Sample Data
The application comes pre-loaded with:
- 8 knowledge categories
- 20+ sample questions across different difficulties
- Proper database relationships and constraints

## 🔧 Development

### Project Structure
```
quizdom/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   └── app.js           # Frontend JavaScript
├── quizdom.db           # SQLite database (auto-generated)
└── README.md            # Project documentation
```

### Adding Questions
Use the admin API endpoint to add new questions:
```json
POST /api/admin/questions
{
  "question_text": "Your question here?",
  "category_id": 1,
  "difficulty": "medium",
  "correct_answer": 2,
  "option_1": "Option A",
  "option_2": "Option B",
  "option_3": "Option C",
  "option_4": "Option D",
  "explanation": "Explanation of the correct answer"
}
```

### Custom Categories
Add new categories through the database or extend the initialization function in `app.py`.

## 🚀 Deployment

### Production Setup
1. Set environment variables
2. Use a production WSGI server (Gunicorn included)
3. Configure reverse proxy (Nginx recommended)
4. Set up SSL certificates
5. Use production database (PostgreSQL recommended)

### Docker Support
Create a `Dockerfile` for containerized deployment:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Maintain consistent indentation
- Add comments for complex logic

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Font Awesome for icons
- Google Fonts for typography
- Flask community for excellent documentation
- Open source contributors

## 📞 Support

For support, feature requests, or bug reports:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints

---

**Built with ❤️ by the QUIZDOM Team**

*Transform your knowledge into victory!* 🏆