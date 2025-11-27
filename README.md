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
It evaluates each task based on urgency, importance, effort, and dependencies — and ranks them using different scoring strategies.

This project was built as part of a Software Development Intern technical assessment.

---

## ✨ Features

### 🔹 Core Functionality
- Add tasks individually or via bulk JSON  
- Weighted scoring based on:
  - Urgency (deadline proximity)
  - Importance (1–10 scale)
  - Effort (estimated hours)
  - Dependencies (priority boost for tasks that unblock others)
- Multiple strategies:
  - **Smart Balance**
  - **Fastest Wins**
  - **High Impact**
  - **Deadline Driven**
- Explanations for every score  
- Circular dependency detection  
- Responsive frontend (HTML + CSS + JS)

---

### 🌟 Bonus Features
#### 📊 Date Intelligence Summary
- Overdue tasks  
- Due today  
- Upcoming tasks  

#### 🔗 Dependency Graph Visualization
- Reverse dependency mapping (tasks unblocked by others)

#### 🟦 Eisenhower Matrix
- Do First  
- Quick Wins  
- Schedule  
- Maybe Later  

---

## 📂 Project Structure

```text
task-analyzer/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── task_analyzer/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   └── tasks/
│       ├── models.py
│       ├── serializers.py
│       ├── scoring.py
│       ├── views.py
│       ├── urls.py
│       └── tests.py
│
└── frontend/
    ├── index.html
    ├── styles.css
    └── script.js
⚙️ Installation & Setup
🖥 Backend Setup
bash
Copy code
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Backend runs at:
📌 http://127.0.0.1:8000/

🌐 Frontend Setup
bash
Copy code
cd frontend
python -m http.server 5500
Open the app in your browser:
📌 http://localhost:5500/index.html

📡 API Endpoints
Method	Endpoint	Description
POST	/api/tasks/analyze/	Analyze and score a list of tasks
GET	/api/tasks/suggest/	Suggest the top 3 tasks for today

🧪 Running Tests
bash
Copy code
cd backend
python manage.py test
Tests cover:

Urgency vs importance trade-offs

Dependency boost logic

Circular dependency detection

🧠 Scoring Strategy (Summary)
Each task receives a 0–100 score, calculated from:

1. Urgency
Based on days left until deadline

Overdue → max urgency

Due today → very high urgency

2. Importance
Input range 1–10

Higher importance = higher weighted score

3. Effort
Small tasks get a quick-win boost

Very large tasks result in reduced score

4. Dependencies
Tasks that unblock others get a dependency priority boost

Reverse dependency mapping determines how many tasks rely on each one

Strategy Weight Differences
Strategy	What It Favors
Smart Balance	Mix of all factors (default)
Fastest Wins	Low effort tasks
High Impact	Importance (1–10 scale)
Deadline Driven	Urgent tasks

🔮 Future Improvements
Task CRUD system with database storage

User authentication + sessions

Advanced dependency graph visualization

Export/import task sets

Drag-and-drop task planner UI

📄 License
This project was created as part of a Software Development Intern task and is free to use for learning and demonstration purposes.
