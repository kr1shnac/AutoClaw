# **AutoClaw: Master System Architecture & Execution Blueprint (v3.0 \- The Enterprise Upgrade)**

**Tagline:** The Resilient, Privacy-First Autonomous Web Orchestration Engine.

**Document Type:** Comprehensive Technical Specification & AI-Ingestion Context Document

## **1\. Project Context & Engineering Philosophy**

* **Project Nature:** Final-year capstone project integrating Applied AI Engineering, Robotic Process Automation (RPA), and State-Machine System Architecture.  
* **Development Team:** A two-person team of AI/ML engineering students (Krishna & Nuhan) operating on a strict 50/50 workload split.  
* **Timeline:** 4 Months (16-week sprint).  
* **Core Objective:** To engineer an autonomous, locally hosted web agent that acts as a "Digital Chief of Staff." It discovers, evaluates, and applies for software engineering roles using **Observation-Reasoning-Action (ORA)** loops, prioritizing extreme resilience over raw speed.  
* **The USP (Unique Selling Proposition):** AutoClaw is "Self-Healing." It abandons brittle web scraping in favor of **Vision-Language-Action (VLA)** fallbacks, Asynchronous Human-in-the-Loop (HITL) Telegram orchestration, and robust Database-Checkpointing.

## **2\. Target Platforms (The Staged Integration Funnel)**

Development and execution follow a strict order of DOM complexity, from easiest to hardest:

1. **Internshala \[Sandbox & Quick Wins\]:** Highly predictable DOM. Serves as the training ground to test standard automation and dynamic Cover Letter generation.  
2. **Lever \[Destination ATS\]:** Minimalist UI. The baseline testing ground for autonomous PDF resume uploads.  
3. **Greenhouse \[Destination ATS\]:** The industry standard for elite startups. Complex, dynamic forms serving as the primary deployment ground for the VLA visual fallback loop and Knockout Question handling.  
4. **Y Combinator / Work at a Startup \[Source Aggregator\]:** Requires login authentication but lacks aggressive rate-limiting. Tests lazy-loading extraction.  
5. **LinkedIn \[Source Aggregator\]:** The Final Boss. Heavily guarded by Cloudflare/DataDome. Scraped strictly via human-mimicking stealth delays.

## **3\. Core System Architecture (The ORA State-Machine)**

AutoClaw does not use linear scripts. It operates as a Persistent State-Machine.

### **Phase 1: Authentication (Session Sweeping)**

* **Strategy:** No live browser hijacking. AutoClaw uses storageState. The human logs in manually once. Playwright captures the authenticated session cookies/tokens and saves them locally (auth/state.json). The agent runs headless background sessions using these trusted credentials.

### **Phase 2: Stealth Discovery & Semantic Deduplication**

* **Extraction:** Uses playwright-stealth with randomized human-mimicry delays (3-8 seconds) and Ghost-Cursor movements.  
* **Deduplication:** To prevent spamming reposted jobs, the system generates a cryptographic hash of Company Name \+ First 50 words of Job Description. If the hash exists in the database, the URL is skipped.

### **Phase 3: The Semantic Brain (Local Evaluation)**

* **Data Prep:** BeautifulSoup4 strips HTML noise. The resume is compressed into a dense Markdown summary to save LLM context window space.  
* **Inference:** Passed to a local Llama 3.1 / Qwen 2.5 model via Ollama (or Groq Free Tier API as a hardware backup).  
* **Validation:** The instructor Python library forces the LLM to output a flawless Pydantic JSON schema: {"match\_score": int, "decision": "APPLY" | "SKIP", "reasoning": "str"}.

### **Phase 4: Execution & VLA Fallback**

* **Standard Execution:** Attempts to fill forms using Playwright Accessibility Locators (e.g., get\_by\_role("button", name="Submit")).  
* **The VLA Fallback (Set-of-Mark):** If the DOM is obfuscated:  
  1. Injects JS to draw numbered red bounding boxes over clickable UI elements.  
  2. Takes a screenshot.  
  3. Sends to Gemini 1.5 Flash Vision API prompting: *"Which number corresponds to the Submit button?"*  
  4. Calculates X/Y pixel coordinates of that number and executes a hardware-level click.  
       
     

## **4\. Asynchronous HITL Orchestration (The Telegram Failsafe)**

AutoClaw never crashes when confused; it asks for help using a decoupled cloud queue.

* **The Cloud Queue:** Telegram messages are not sent directly to the sleeping local laptop. They hit a free Vercel/Node.js webhook, which stores the command in a lightweight cloud queue. When the laptop wakes up, AutoClaw fetches the queue and executes.  
* **Security Whitelist:** The Telegram bot hardcodes Krishna and Nuhan's unique Telegram User IDs. All other messages are dropped to prevent remote hijacking.  
* **The Unknown Question Protocol:** If Greenhouse asks an unknown Knockout Question, Playwright pauses. The bot texts a screenshot of the question to Telegram. The human replies with the answer. AutoClaw inputs the answer and saves it to candidate\_profile.json.  
* **Profile Categorization:** candidate\_profile.json strictly separates *Universal Truths* (e.g., GitHub URL—safe to auto-reuse) from *Company-Specific Answers* (e.g., "Why do you want to work here?"—never auto-reused).  
* **Timeout Failsafe:** If the human does not reply within 5 minutes, AutoClaw logs the job as SKIPPED\_MISSING\_INFO, closes the tab, and moves on to prevent session expiration.

## **5\. Advanced Edge Cases & Failsafes (The Bulletproof Layer)**

1. **The Multi-Page ATS Loop:** Application execution runs in a recursive while loop, searching for "Next" or "Continue" buttons until the final "Application Submitted" success message is found.  
2. **Dual-Format Vault:** AutoClaw checks the \<input accept="..."\> tag. If a portal blocks PDFs or has strict size limits, it dynamically switches to a compressed .docx resume stored in a local /vault directory.  
3. **Cover Letter Mad-Libs:** To prevent LLM thermal throttling/overheating, AutoClaw does not generate cover letters from scratch. It uses a pre-written template and asks the LLM to extract 2-3 specific keywords to fill the blanks, cutting generation time from 30s to 0.5s.  
4. **Post-Submit CAPTCHA Detection:** After clicking "Submit", the bot explicitly checks the DOM. If a Cloudflare Turnstile \<iframe\> appears instead of a success message, it instantly triggers the Telegram Interruption Protocol.  
5. **Residential IP Quota:** To prevent home Wi-Fi IP bans, a hard limit of MAX\_DAILY\_APPLICATIONS \= 40 is enforced at the database level.

## **6\. Technology Stack**

| Component | Technology | Purpose |
| :---- | :---- | :---- |
| **Backend & Orchestration** | Python 3.11+ | Core logic and state-machine execution. |
| **Web Automation** | Playwright (Async) | Browser control, stealth, and Session Sweeping. |
| **State Management** | SQLite3 (WAL Mode) | Thread-safe database with journal\_mode=WAL;. |
| **Local AI Engine** | Ollama | Hosts Llama 3.1 / Qwen 2.5 locally (Zero Cost). |
| **Structured JSON parsing** | instructor \+ Pydantic | Guarantees perfect JSON outputs from the LLM. |
| **Vision Inference** | Gemini 1.5 Flash API | VLA Set-of-Mark coordinate mapping. |
| **User Interface** | Streamlit | Fast, modern local web dashboard. |
| **Remote Telemetry** | python-telegram-bot | Asynchronous human-in-the-loop communication. |
| **Web Hosting / Docs** | GitHub Pages (gh-pages) | Hosts the project documentation and marketing site. |

## **7\. Task Delegation & 4-Month Timeline (50/50 Split)**

**Krishna (Lead Architect: AI Core & Stealth Operations)**

* **Month 1:** Set up Ollama, Llama 3.1, and instructor library for perfect Pydantic validation. Write the prompt templates.  
* **Month 2:** Build the Telegram webhook queue architecture (Vercel) and the Whitelist security layer.  
* **Month 3:** Engineer the VLA Set-of-Mark JS injection and Gemini Vision integration.  
* **Month 4:** Build the LinkedIn/YC stealth discovery scripts using Session Sweeping and Ghost-Cursor logic.

**Nuhan (Lead Engineer: Systems, ATS Logic & UI)**

* **Month 1:** Set up Git repo, gh-pages website, and SQLite database with WAL mode and Semantic Deduplication hashing.  
* **Month 2:** Build the standard DOM automation for Internshala (Mad-libs cover letter) and Lever.  
* **Month 3:** Build the Greenhouse application logic, integrating the Dual-Format Vault and Multi-Page ATS loop.  
* **Month 4:** Build the Streamlit dashboard and the candidate\_profile.json learning mechanism.

