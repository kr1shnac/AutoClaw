# **AutoClaw: Master System Architecture & Execution Blueprint (v4.0 \- Final AI Ingestion Document)**

**Document Type:** Comprehensive Technical Specification & AI-Context Ledger

**Project Name:** AutoClaw

**Team:** Krishna (Lead Architect \- 60%) & Nuhan (Systems Engineer \- 40%)

**Timeline:** 4 Months (16-week sprint)

## **1\. Project Context & Meta-Objectives**

AutoClaw is an autonomous, locally-hosted web orchestration agent designed to discover, semantically evaluate, and apply for high-tier software engineering roles. It abandons brittle web-scraping for a state-machine architecture that utilizes Asynchronous Human-in-the-Loop (HITL) communication and Vision-Language-Action (VLA) visual fallbacks. The project strictly targets five platforms, escalating in complexity: Internshala (Sandbox) \-\> Lever (Standard ATS) \-\> Greenhouse (Complex ATS) \-\> Y Combinator (Authenticated Source) \-\> LinkedIn (Adversarial Source).

## **2\. Global Git Workflow (The Team Standard)**

To prevent code conflicts and maintain a pristine codebase, both engineers must strictly adhere to this Git workflow.

1. **Base Branches:** \* main: Holds only stable, fully tested code.  
   * dev: The active integration branch where Krishna and Nuhan merge their features.  
2. **The Feature Lifecycle:**  
   * Always start from updated dev: git checkout dev \-\> git pull origin dev  
   * Create a dedicated branch for your task: git checkout \-b feature/\[your-name\]-\[task-name\]  
   * Stage and commit: git add . \-\> git commit \-m "\[Task\] Detailed description"  
   * Push: git push origin feature/\[your-name\]-\[task-name\]  
   * Merge: Open a Pull Request (PR) on GitHub to merge into dev.

---

# **Engineer 2: Nuhan's Master Ledger (40% Workload)**

**Role:** Systems & Infrastructure Engineer (Database, UI, Telegram Queue, Standard ATS)

**Instruction for AI:** Track the status of these tasks. When the user (Nuhan) prompts for the next task, identify the first \[ \] PENDING item and provide exact implementation code.

## **Phase 1: State Management & Data Parsing (Weeks 1-4)**

* **Task 1.1: SQLite WAL Database & Deduplication**  
  * **Objective:** Build the SQLite database schema (discovered\_jobs, application\_logs) and strictly enable PRAGMA journal\_mode=WAL; for thread safety. Write the cryptographic hashing function (Company Name \+ 50 words of JD) to prevent applying to duplicate jobs.  
  * **Git Branch:** feature/nuhan-sqlite-wal-schema  
  * **Commit Message:** Initialize SQLite WAL database and deduplication hash logic  
  * **Status:** \[ \] PENDING  
* **Task 1.2: HTML Noise Reduction Pipeline**  
  * **Objective:** Write the BeautifulSoup4 parser that strips navbars, footers, and scripts from raw web pages, returning only the clean Job Description text to save LLM context window space.  
  * **Git Branch:** feature/nuhan-bs4-cleaner  
  * **Commit Message:** Add BeautifulSoup HTML cleaning pipeline  
  * **Status:** \[ \] PENDING

## **Phase 2: Standard ATS Automation (Weeks 5-8)**

* **Task 2.1: Internshala & Lever Automation**  
  * **Objective:** Write the standard Playwright DOM navigation scripts for Internshala and Lever. Handle basic text inputs, the Dual-Format PDF/Docx resume upload logic, and the recursive while loop for multi-page forms.  
  * **Git Branch:** feature/nuhan-internshala-lever-ats  
  * **Commit Message:** Build deterministic application scripts for Internshala and Lever  
  * **Status:** \[ \] PENDING  
* **Task 2.2: Greenhouse Automation Base**  
  * **Objective:** Build the standard Playwright flow for Greenhouse application forms, utilizing Accessibility Locators (get\_by\_role) before Krishna's VLA fallback is triggered.  
  * **Git Branch:** feature/nuhan-greenhouse-base  
  * **Commit Message:** Build standard Greenhouse DOM navigation  
  * **Status:** \[ \] PENDING

## **Phase 3: Asynchronous HITL Gateway (Weeks 9-12)**

* **Task 3.1: Telegram Vercel Webhook Queue**  
  * **Objective:** Set up a free serverless Vercel Node.js endpoint to receive Telegram messages, acting as a queue. Write the local Python script that fetches commands from this queue to prevent the "Sleeping Laptop" failure.  
  * **Git Branch:** feature/nuhan-telegram-cloud-queue  
  * **Commit Message:** Integrate decoupled Telegram cloud queue  
  * **Status:** \[ \] PENDING  
* **Task 3.2: Telegram Security Whitelist & Timeout Failsafe**  
  * **Objective:** Hardcode the authorized Telegram User IDs into the bot logic to drop unauthorized commands. Code the 5-minute timeout timer for manual overrides; if the user doesn't respond, the bot safely skips the job.  
  * **Git Branch:** feature/nuhan-telegram-security  
  * **Commit Message:** Add ID Whitelist and 5-minute timeout failsafe to Telegram bot  
  * **Status:** \[ \] PENDING

## **Phase 4: Local Dashboard (Weeks 13-16)**

* **Task 4.1: Streamlit Live Interface**  
  * **Objective:** Build a fast, local web dashboard using Streamlit to visualize the SQLite database. Create views for "Jobs Discovered", "Jobs Applied", and "Recent LLM Match Scores".  
  * **Git Branch:** feature/nuhan-streamlit-dashboard  
  * **Commit Message:** Deploy Streamlit UI for database monitoring  
  * **Status:** \[ \] PENDING