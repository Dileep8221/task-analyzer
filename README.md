<h1 align="center">Smart Task Analyzer</h1>
<p align="center">
  A Django + JavaScript based task prioritization system that evaluates tasks using urgency, importance, effort, and dependencies.
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue"/>
  <img src="https://img.shields.io/badge/Django-4.x-green"/>
  <img src="https://img.shields.io/badge/Frontend-HTML%20%2F%20CSS%20%2F%20JS-yellow"/>
  <img src="https://img.shields.io/badge/Status-Completed-success"/>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey"/>
</p>

---

## 🚀 Overview

Smart Task Analyzer is a full-stack application that helps users prioritize tasks using a balanced scoring algorithm.  
It considers urgency, importance, effort, and task dependencies while offering multiple strategies for ranking.

This project was built as part of a Software Development Intern technical assessment.

---

## ✨ Features

### 🔹 Core Functionality

- Add tasks one-by-one or via bulk JSON  
- Weighted scoring system using:
  - Urgency (deadlines)
  - Importance (1–10 scale)
  - Effort (estimated hours)
  - Dependencies (boost given to tasks that unblock others)
- Multiple analysis strategies:
  - Smart Balance  
  - Fastest Wins  
  - High Impact  
  - Deadline Driven  
- Clear explanations for each score  
- Strong validation + circular dependency detection  
- Responsive and framework-free frontend  

---

### 🌟 Bonus Features (Per Assessment Requirements)

#### 📊 Date Intelligence Summary
- Overdue tasks  
- Due today  
- Upcoming tasks  

#### 🔗 Dependency Graph Visualization
- Shows what each task depends on  
- Shows which tasks are unblocked by others  

#### 🟦 Eisenhower Matrix Visualization
- Urgent & Important → **Do First**  
- Urgent & Less Important → **Quick Wins**  
- Not Urgent & Important → **Schedule**  
- Not Urgent & Less Important → **Maybe Later**  

---

## 📂 Project Structure

task-analyzer/
│
├── backend/
│ ├── manage.py
│ ├── requirements.txt
│ ├── task_analyzer/
│ │ ├── settings.py
│ │ ├── urls.py
│ │ └── ...
│ └── tasks/
│ ├── models.py
│ ├── serializers.py
│ ├── scoring.py
│ ├── views.py
│ ├── urls.py
│ └── tests.py
│
└── frontend/
├── index.html
├── styles.css
└── script.js

yaml
Copy code

---

## ⚙️ Installation & Setup

### **Backend**

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Backend runs at:
http://127.0.0.1:8000/

Frontend
bash
Copy code
cd frontend
python -m http.server 5500
Open in browser:
http://localhost:5500/index.html

📡 API Endpoints
Method	Endpoint	Description
POST	/api/tasks/analyze/	Analyze and score tasks
GET	/api/tasks/suggest/	Suggest top 3 tasks for today

🧪 Running Tests
bash
Copy code
cd backend
python manage.py test
Tests cover:

Urgency vs importance trade-off

Dependency boost logic

Circular dependency detection

🧠 Scoring Strategy (Summary)
Each task receives a 0–100 score using:

Urgency → closer deadlines score higher

Importance → weighted impact factor

Effort → small tasks get a quick-win boost

Dependencies → tasks that unblock others get priority

Different strategies adjust weights for each factor.

🔮 Future Improvements
CRUD UI for storing tasks in the DB

User accounts & sessions

More detailed dependency graph visualization

Export/import task datasets

Drag-and-drop task dashboard

📄 License
This project was created for an internship technical assessment and is free to use for learning purposes.