# Automated AI Blog Pipeline 🤖✍️

An end-to-end automation pipeline that uses **Google Gemini AI** to generate high-quality technical blog posts and **Selenium** to automatically publish them to **Dev.to**.

## 🚀 Features

- **AI-Powered Content**: Generates thought-leadership articles using `gemini-2.5-flash`.
- **Selenium Automation**: Handles the full publishing flow on Dev.to, including login session management.
- **Flask Review App**: Local dashboard to view and manage generated posts.
- **CI/CD Ready**: Includes a `Jenkinsfile` for scheduled and manual automation with approval gates.
- **Robust Testing**: Comprehensive test suite ensuring pipeline reliability.

## 📂 Project Structure

```text
.
├── src/                # Core logic (Generation, Publishing, Flask App)
├── tests/              # Pytest test suite
├── data/               # Persistent storage for posts and temporary content
├── Jenkinsfile         # CI/CD pipeline definition
├── requirements.txt    # Python dependencies
└── .env.example        # Template for environment variables
```

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Google Chrome Browser
- Google Gemini API Key ([Get it here](https://aistudio.google.com/))

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Aums04/blog-automation.git
cd blog-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your details:
```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Browser Session Setup
To bypass bot detection on Dev.to, run the login script once to save your session:
```bash
python src/login_once.py
```
*Note: This will open a Chrome window. Log into Dev.to manually and close the window.*

## 📖 Usage

### Generate Content
```bash
python src/generate_blog.py --topic "The Future of Web Automation"
```

### Publish to Dev.to
```bash
python src/publish_blog.py
```

### Run Local Dashboard
```bash
python src/blog_app.py
```
Open `http://localhost:5000` to view your posts.

## 🧪 Testing
Run the test suite to ensure everything is configured correctly:
```bash
python tests/test_blog.py
```

## 🏗️ Jenkins Integration
This project is designed for Jenkins. 
1. Create a **Pipeline** job in Jenkins.
2. Point it to this repository.
3. The pipeline includes:
   - **Scheduled Daily Runs**: Automated generation at midnight.
   - **Manual Approval Gate**: Preview content before publishing.
   - **Direct Publish**: Parameterized mode for fully automated runs.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
