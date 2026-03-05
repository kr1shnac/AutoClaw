Welcome to Day 1\. This is the absolute baseline. If you and Nuhan set this up perfectly right now, you will never have to deal with the nightmare of "it works on my machine but not yours."

Here are the three foundational files and the exact terminal commands to launch the **AutoClaw** engineering environment.

---

### **1\. The Foundation Files**

Create these three files in the root folder of your project (\~/Sandbox/AutoClaw).

#### **File A: requirements.txt**

This locks in the exact versions of your tech stack so neither of you experiences unexpected updates that break the code.

Plaintext

\# AutoClaw Tech Stack (v1.0)  
playwright\>=1.41.0  
playwright-stealth\>=1.0.6  
beautifulsoup4\>=4.12.3  
pydantic\>=2.5.3  
instructor\>=0.5.2  
google-generativeai\>=0.4.0  
streamlit\>=1.31.0  
python-telegram-bot\>=20.8  
SQLAlchemy\>=2.0.25  
markdownify\>=0.11.6

#### **File B: .gitignore**

**This is the most important security file.** It ensures you don't accidentally upload your personal resume, your LinkedIn session cookies, or your API keys to the public GitHub repository.

Plaintext

\# Python Environment  
\_\_pycache\_\_/  
\*.py\[cod\]  
\*$py.class  
venv/  
env/  
.env

\# AutoClaw Specific Secrets & State  
auth/state.json  
candidate\_profile.json  
vault/  
\*.sqlite3  
\*.db  
\*.sqlite3-wal  
\*.sqlite3-shm

\# Streamlit & UI  
.streamlit/

\# OS Files  
.DS\_Store  
Thumbs.db

#### **File C: .env (Local Configuration)**

Create a file literally just named .env. This stays strictly on your local machine. You and Nuhan will each have your own copy.

Code snippet

\# AutoClaw Local Secrets  
GEMINI\_API\_KEY="your\_google\_ai\_studio\_key\_here"  
TELEGRAM\_BOT\_TOKEN="your\_botfather\_token\_here"

\# Security Whitelist (Comma-separated Telegram IDs)  
AUTHORIZED\_TELEGRAM\_IDS="krishnas\_id,nuhans\_id"

---

### **2\. The Launch Sequence (Terminal Commands)**

#### **Step 1: Krishna's Execution (The Lead Architect)**

Since you own the repository, open your terminal in \~/Sandbox/AutoClaw and run these commands to set up the dev branch and push the foundation:

Bash

\# 1\. Switch away from the website branch back to your main code  
git checkout main

\# 2\. Create and switch to the new integration branch  
git checkout \-b dev

\# (Make sure you have created requirements.txt and .gitignore in your folder now)

\# 3\. Stage the safe files (Notice we DO NOT add .env)  
git add requirements.txt .gitignore

\# 4\. Commit the foundation  
git commit \-m "Initialize project foundation, dependencies, and security rules"

\# 5\. Push the dev branch to the cloud  
git push \-u origin dev

#### **Step 2: Nuhan's Execution (The Systems Engineer)**

Nuhan needs to clone the repository and sync his laptop to yours. Send him these exact commands to run on his machine:

Bash

\# 1\. Clone the repository  
git clone https://github.com/YOUR\_USERNAME/AutoClaw.git  
cd AutoClaw

\# 2\. Switch to the dev branch  
git checkout dev

\# 3\. Create a clean Python Virtual Environment  
python3 \-m venv venv

\# 4\. Activate the environment (Mac/Linux)  
source venv/bin/activate  
\# (If Nuhan is on Windows Command Prompt, he runs: venv\\Scripts\\activate)

\# 5\. Install the exact same tech stack as Krishna  
pip install \-r requirements.txt

\# 6\. Download the invisible browser binaries for automation  
playwright install

---

### **The Environment is Locked**

Once Nuhan runs playwright install, your machines are officially synchronized. You both have identical sandboxes, secured by the .gitignore, and completely isolated from your global laptop settings via the venv.

The planning phase is 100% complete. The environment is live.

Who is opening their code editor first? Would you like the initial Python script for **Krishna's Task 1.1 (Ollama \+ Pydantic connection)** or **Nuhan's Task 1.1 (SQLite WAL Database schema)**?

